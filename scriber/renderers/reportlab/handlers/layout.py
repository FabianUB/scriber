from __future__ import annotations
from typing import List
import io

from reportlab.lib import colors
from reportlab.platypus import Flowable
from reportlab.pdfbase.pdfmetrics import stringWidth

from ....core.nodes import SeparatorNode, LabeledSeparatorNode, RowNode, ColumnNode, SpacerNode
from ....document import Document
from ..base import resolve_color
from ..base import HR  # reuse HR flowable from base if exposed; fallback below
from reportlab.platypus import Table, TableStyle, Spacer
from typing import List


def separator_flowable(doc: Document, node: SeparatorNode, styles) -> Flowable:
    # Resolve thickness and color
    thickness = node.props.get("thickness")
    try:
        stroke = float(thickness) if thickness is not None else 1.0
    except Exception:
        stroke = 1.0
    col = resolve_color(doc, node.props.get("color")) or doc.theme.colors.get("border", colors.HexColor("#e5e7eb"))
    style = node.props.get("style") or "solid"
    m_top = float(node.props.get("margin_top", 0.0) or 0.0)
    m_bottom = float(node.props.get("margin_bottom", 0.0) or 0.0)
    return HR(width=stroke, color=col, style=style, m_top=m_top, m_bottom=m_bottom)


def labeled_separator_flowables(doc: Document, node: LabeledSeparatorNode, styles) -> List[Flowable]:
    # Defer to reportlab.py implementation by importing HR and using Paragraph from styles
    from reportlab.platypus import Paragraph

    text = str(node.props.get("text", ""))
    thickness = node.props.get("thickness")
    try:
        stroke = float(thickness) if thickness is not None else 1.0
    except Exception:
        stroke = 1.0
    col = resolve_color(doc, node.props.get("color")) or doc.theme.colors.get("border", colors.HexColor("#e5e7eb"))
    style = node.props.get("style") or "solid"
    m_top = float(node.props.get("margin_top", 0.0) or 0.0)
    m_bottom = float(node.props.get("margin_bottom", 0.0) or 0.0)
    gap = node.props.get("gap")
    try:
        gap = float(gap) if gap is not None else doc.theme.spacing.get("sm", 8)
    except Exception:
        gap = doc.theme.spacing.get("sm", 8)
    muted = bool(node.props.get("muted", True))
    label_style = styles["Muted"] if muted else styles["Body"]
    label = Paragraph(text, label_style)

    class _LabeledSep(Flowable):
        def __init__(self):
            super().__init__()
            self._aw = 0
            self._lw = 0
            self._lh = 0

        def wrap(self, availWidth, availHeight):
            self._aw = availWidth
            fn = getattr(label, 'style', None).fontName if hasattr(label, 'style') else "Helvetica"
            fs = getattr(label, 'style', None).fontSize if hasattr(label, 'style') else 10
            intrinsic = stringWidth(getattr(label, 'text', text), fn, fs)
            max_label_w = max(availWidth - 2 * gap, 0)
            lw_constraint = min(max_label_w, intrinsic)
            lw, lh = label.wrap(lw_constraint, 1e6)
            self._lw, self._lh = lw, lh
            content_h = max(stroke, lh)
            return availWidth, m_top + content_h + m_bottom

        def draw(self):
            c = self.canv
            c.setStrokeColor(col)
            c.setLineWidth(stroke)
            s = (style or "solid").lower()
            if s == "dashed":
                c.setDash(6, 3)
            elif s == "dotted":
                c.setDash(1, 2)
            else:
                c.setDash()
            content_h = max(stroke, self._lh)
            y = m_bottom + content_h / 2.0
            left_len = max((self._aw - self._lw - 2 * gap) / 2.0, 0)
            right_start = left_len + gap + self._lw + gap
            c.line(0, y, left_len, y)
            c.line(right_start, y, self._aw, y)
            label_x = left_len + gap
            label_y = y - (self._lh / 2.0)
            label.drawOn(c, label_x, label_y)

    return [_LabeledSep()]


def row_flowables(doc: Document, node: RowNode, styles) -> List[Flowable]:
    gap = node.props.get("gap", doc.theme.spacing["md"])
    equal = node.props.get("equal", False)
    align = node.props.get("justify", "start")

    # Collect child flowables and weights
    from ....renderers.reportlab import _to_flowables  # local import to avoid cycle typing
    items: List[Flowable] = []
    weights: List[float] = []
    for child in node.children:
        child_flows = _to_flowables(doc, child, styles)
        if not child_flows:
            cell_flow = Spacer(1, 1)
        elif len(child_flows) == 1:
            cell_flow = child_flows[0]
        else:
            inner = Table([[f] for f in child_flows])
            inner.setStyle(
                TableStyle(
                    [
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            cell_flow = inner
        items.append(cell_flow)
        w = 1.0
        if hasattr(child, "props"):
            w = float(child.props.get("grow", 1) or 1)
        weights.append(max(w, 0.0))

    if not equal:
        cells: List[Flowable] = []
        for i, flow in enumerate(items):
            cells.append(flow)
            if i < len(items) - 1 and gap:
                cells.append(Spacer(gap, 0))
        data = [cells]
        t = Table(data)
        align_map = {"start": "LEFT", "center": "CENTER", "end": "RIGHT"}
        t.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), align_map.get(align, "LEFT")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return [t]

    class _WeightedRow(Flowable):
        def __init__(self, items: List[Flowable], weights: List[float], gap: int, align: str):
            super().__init__()
            self.items = items
            self.weights = [w if w > 0 else 0 for w in weights]
            self.gap = gap
            self.align = align
            self._table = None

        def _build_table(self, availWidth):
            n = len(self.items)
            gaps = (n - 1) * self.gap if n > 1 else 0
            content_width = max(availWidth - gaps, 0)
            total_w = sum(self.weights) or n
            per_cols = [content_width * (w / total_w) for w in self.weights]
            cells: List[Flowable] = []
            col_widths: List[float] = []
            for i, (it, cw) in enumerate(zip(self.items, per_cols)):
                cells.append(it)
                col_widths.append(cw)
                if i < n - 1 and self.gap:
                    cells.append(Spacer(self.gap, 0))
                    col_widths.append(self.gap)
            t = Table([cells], colWidths=col_widths)
            align_map = {"start": "LEFT", "center": "CENTER", "end": "RIGHT"}
            t.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ALIGN", (0, 0), (-1, -1), align_map.get(self.align, "LEFT")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            self._table = t

        def wrap(self, availWidth, availHeight):
            self._build_table(availWidth)
            return self._table.wrap(availWidth, availHeight)

        def split(self, availWidth, availHeight):
            if not self._table:
                self._build_table(availWidth)
            return self._table.split(availWidth, availHeight)

        def draw(self):
            self._table.drawOn(self.canv, 0, 0)

    return [_WeightedRow(items, weights, gap, align)]


def column_flowables(doc: Document, node: ColumnNode, styles) -> List[Flowable]:
    flows: List[Flowable] = []
    gap = node.props.get("gap", doc.theme.spacing["md"])
    from ....renderers.reportlab import _to_flowables
    for i, child in enumerate(node.children):
        flows.extend(_to_flowables(doc, child, styles))
        if i < len(node.children) - 1 and gap:
            flows.append(Spacer(1, gap))
    return flows


def spacer_flowable(doc: Document, node: SpacerNode, styles) -> Flowable:
    size_val = node.props.get("size")
    if isinstance(size_val, (int, float)):
        h = float(size_val)
    else:
        key = size_val or "md"
        h = float(doc.theme.spacing.get(key, doc.theme.spacing["md"]))
    if h < 0:
        h = 0.0
    elif 0 < h < 0.5:
        h = 0.5
    return Spacer(1, h)

