from __future__ import annotations
from typing import List
import io

from reportlab.lib import colors
from reportlab.platypus import Flowable
from reportlab.pdfbase.pdfmetrics import stringWidth

from ....core.nodes import SeparatorNode, LabeledSeparatorNode
from ....document import Document
from ..base import resolve_color
from ..base import HR  # reuse HR flowable from base if exposed; fallback below


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

