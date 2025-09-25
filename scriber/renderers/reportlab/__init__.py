from __future__ import annotations
from typing import List, Tuple

from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    PageBreak,
)
from reportlab.pdfgen import canvas

from ...core.nodes import (
    BadgeNode,
    ButtonNode,
    CardNode,
    ColumnNode,
    Node,
    RowNode,
    SeparatorNode,
    SpacerNode,
    FigureNode,
    ImageNode,
    TableNode,
    LabeledSeparatorNode,
    TextNode,
    PageNode,
)
from ...document import Document
from .handlers.layout import (
    separator_flowable as _sep_handler,
    labeled_separator_flowables as _labeled_sep_handler,
    row_flowables as _row_handler,
    column_flowables as _column_handler,
    spacer_flowable as _spacer_handler,
)
from .handlers.typography import text_flowable as _text_handler
from .handlers.badge import badge_flowable as _badge_handler
from .handlers.button import button_flowable as _button_handler
from .handlers.card import card_flowables as _card_handler
from .handlers.table import table_flowables as _table_handler
from .handlers.figure import figure_flowables as _figure_handler
from .handlers.image import image_flowables as _image_handler
from ...settings import Settings
from ...theme.tokens import size_token
from .base import create_styles
from . import dispatch
import io
import os
import numbers
import datetime as _dt
try:
    from svglib.svglib import svg2rlg  # type: ignore
except Exception:  # optional dependency
    svg2rlg = None


PAGE_SIZES = {
    "A4": A4,
    "LETTER": LETTER,
}


def _styles(doc: Document):
    return create_styles(doc)


def _bold_font_name(base: str) -> str:
    base_lower = (base or "").lower()
    if "helvetica" in base_lower:
        return "Helvetica-Bold"
    if "times" in base_lower:
        return "Times-Bold"
    if "courier" in base_lower:
        return "Courier-Bold"
    # Fallback: Helvetica-Bold is generally available
    return "Helvetica-Bold"


def _apply_separators(s: str, settings: Settings) -> str:
    # Convert from US-style string (',' thousands and '.' decimal) to desired
    thou = settings.thousands_separator
    dec = settings.decimal_separator
    if thou == "," and dec == ".":
        return s
    # Temporarily replace to avoid collision
    s = s.replace(",", "<T>").replace(".", "<D>")
    s = s.replace("<T>", thou).replace("<D>", dec)
    return s


def _format_number(num: float, settings: Settings, decimals: int | None = None) -> str:
    d = settings.number_decimals if decimals is None else int(decimals)
    base = f"{num:,.{d}f}"
    return _apply_separators(base, settings)


def _format_percent(num: float, settings: Settings, decimals: int | None = None) -> str:
    d = settings.percent_decimals if decimals is None else int(decimals)
    base = f"{num*100:,.{d}f}%"
    return _apply_separators(base, settings)


from .base import HR


def render(doc: Document, output_path: str) -> None:
    # Ensure output directory exists
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    page_size = PAGE_SIZES.get(doc.size.upper(), A4)
    pdf = SimpleDocTemplate(
        output_path,
        pagesize=page_size,
        leftMargin=doc.margin,
        rightMargin=doc.margin,
        topMargin=doc.margin,
        bottomMargin=doc.margin,
    )

    styles = _styles(doc)
    story: List[Flowable] = []

    doc._heading_counter = getattr(doc, "_heading_counter", 0)
    doc._outline_depth = getattr(doc, "_outline_depth", 3)
    doc._toc_depth = getattr(doc, "_toc_depth", 0)
    doc._has_toc = getattr(doc, "_has_toc", False)
    doc._story_started = False
    doc._last_flowable_pagebreak = getattr(doc, "_last_flowable_pagebreak", False)

    # root is a Column; iterate children (pages/containers)
    for child in doc.root.children:
        flows = _to_flowables(doc, child, styles)
        if flows:
            story.extend(flows)
            doc._story_started = True
            doc._last_flowable_pagebreak = isinstance(flows[-1], PageBreak)

    # Page decorations: header/footer and page numbers
    def _draw_header_footer(canv, rl_doc):
        # Header
        if doc.header:
            if callable(doc.header):
                try:
                    doc.header(canv, rl_doc, doc)
                except Exception:
                    pass
            else:
                canv.saveState()
                canv.setFont(doc.theme.typography["font"], 10)
                canv.setFillColor(doc.theme.colors["muted"])  # muted
                y = rl_doc.height + rl_doc.topMargin + 10
                text = str(doc.header)
                align = getattr(doc, 'header_align', 'left') or 'left'
                align = align.lower()
                if align == 'right':
                    x = rl_doc.leftMargin + rl_doc.width
                    canv.drawRightString(x, y, text)
                elif align == 'center':
                    x = rl_doc.leftMargin + (rl_doc.width / 2.0)
                    canv.drawCentredString(x, y, text)
                else:
                    canv.drawString(rl_doc.leftMargin, y, text)
                canv.restoreState()
        # Footer
        if doc.footer:
            if callable(doc.footer):
                try:
                    doc.footer(canv, rl_doc, doc)
                except Exception:
                    pass
            else:
                canv.saveState()
                canv.setFont(doc.theme.typography["font"], 9)
                canv.setFillColor(doc.theme.colors["muted"])  # muted
                y = rl_doc.bottomMargin - 16
                canv.drawString(rl_doc.leftMargin, y, str(doc.footer))
                canv.restoreState()

    def _after_flowable(flow):
        level = getattr(flow, '_scriber_heading_level', None)
        if level is None:
            return
        text_value = getattr(flow, '_scriber_heading_text', '')
        bookmark = getattr(flow, '_scriber_bookmark_name', None)
        outline_depth = getattr(doc, '_outline_depth', 3)
        if bookmark:
            try:
                pdf.canv.bookmarkPage(bookmark)
            except Exception:
                pass
        if bookmark and level < max(outline_depth, 0):
            try:
                pdf.canv.addOutlineEntry(text_value, bookmark, level=level, closed=False)
            except Exception:
                pass
        if getattr(doc, '_has_toc', False) and level < max(getattr(doc, '_toc_depth', 0), 0):
            try:
                page_number = pdf.canv.getPageNumber()
            except Exception:
                page_number = 0
            try:
                pdf.notify('TOCEntry', (level, text_value, page_number, bookmark))
            except Exception:
                pass

    pdf.afterFlowable = _after_flowable

    # Page numbering canvas
    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            # Save current page state but do not emit the page yet
            self._saved_page_states.append(dict(self.__dict__))
            canvas.Canvas._startPage(self)

        def save(self):
            """Add page info to each page (page x of y)."""
            total = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                if doc.page_numbers:
                    self.draw_page_number(self._pageNumber, total)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_num, total):
            fmt = doc.page_numbers
            if not fmt:
                return
            if fmt == "x":
                label = f"{page_num}"
            else:  # default 'xofy'
                label = f"{page_num} of {total}"
            self.saveState()
            self.setFont(doc.theme.typography["font"], 9)
            self.setFillColor(doc.theme.colors["muted"])
            # Use canvas page size and a default margin if template not available here
            page_w, page_h = getattr(self, "_pagesize", (595.27, 841.89))
            right_margin = getattr(pdf, 'rightMargin', 36)
            bottom_margin = getattr(pdf, 'bottomMargin', 36)
            y = bottom_margin - 16
            x = page_w - right_margin
            self.drawRightString(x, y, label)
            self.restoreState()

    build_kwargs = dict(onFirstPage=_draw_header_footer, onLaterPages=_draw_header_footer, canvasmaker=NumberedCanvas)
    if getattr(doc, '_has_toc', False):
        pdf.multiBuild(story, **build_kwargs)
    else:
        pdf.build(story, **build_kwargs)


def _text_flowable(doc, node, styles): return _text_handler(doc, node,
styles)


def _badge_flowable(doc, node, styles): return _badge_handler(doc, node,
styles)


def _button_flowable(doc, node, styles): return _button_handler(doc, node,
styles)


def _card_flowables(doc, node, styles): return _card_handler(doc, node,
styles)


def _normalize_table_source(source, columns):
    # Try pandas
    try:
        import pandas as pd  # type: ignore
        if isinstance(source, pd.DataFrame):
            if columns is None:
                columns = list(source.columns)
            rows = source[columns].astype(object).values.tolist()
            return columns, rows
    except Exception:
        pass
    # Try polars
    try:
        import polars as pl  # type: ignore
        if isinstance(source, pl.DataFrame):
            if columns is None:
                columns = list(source.columns)
            rows = source.select(columns).to_numpy().tolist()
            return columns, rows
    except Exception:
        pass
    # List[dict]
    if isinstance(source, list) and source and isinstance(source[0], dict):
        keys = columns or list(source[0].keys())
        rows = [[row.get(k) for k in keys] for row in source]
        return keys, rows
    # List[list]
    if isinstance(source, list) and source and isinstance(source[0], (list, tuple)):
        if columns is None:
            # No headers provided; leave to caller
            return None, [list(r) for r in source]
        else:
            return columns, [list(r) for r in source]
    # Empty or unknown
    return columns, []


def _table_flowables(doc: Document, node: TableNode, styles) -> List[Flowable]:
    theme = doc.theme
    src = node.props.get("source")
    columns = node.props.get("columns")
    header = bool(node.props.get("header", True))
    zebra = bool(node.props.get("zebra", False))
    compact = bool(node.props.get("compact", False))
    align_prop = node.props.get("align")
    header_align_prop = node.props.get("header_align")
    header_bold = bool(node.props.get("header_bold", True))
    formats = node.props.get("formats", {}) or {}
    currency_symbol = node.props.get("currency_symbol") or doc.settings.currency_symbol
    col_widths_prop = node.props.get("col_widths")

    cols, rows = _normalize_table_source(src, columns)
    n_cols = len(cols) if cols else (len(rows[0]) if rows else 0)

    # Detect numeric columns when align not provided
    numeric_cols = [False] * n_cols
    if n_cols:
        for ci in range(n_cols):
            is_numeric = True
            for r in rows:
                if ci >= len(r):
                    continue
                v = r[ci]
                if v is None:
                    continue
                if isinstance(v, numbers.Number):
                    continue
                # Try to parse strings
                try:
                    float(str(v).replace(",", ""))
                except Exception:
                    is_numeric = False
                    break
            numeric_cols[ci] = is_numeric

    # Build body with formatting
    def fmt_cell(ci: int, v):
        if v is None:
            return ""
        # Date/time formatting
        if isinstance(v, (_dt.datetime, _dt.date)):
            try:
                if isinstance(v, _dt.datetime):
                    return v.strftime(doc.settings.datetime_format)
                return v.strftime(doc.settings.date_format)
            except Exception:
                return str(v)
        fmt = None
        fmt_decimals = None
        # Resolve formats by column name or index
        if isinstance(formats, dict):
            if cols and ci < len(cols) and cols[ci] in formats:
                fmt = formats[cols[ci]]
            elif ci in formats:
                fmt = formats[ci]
        # If format is a dict/tuple, extract type and decimals
        if isinstance(fmt, dict):
            fmt_decimals = fmt.get("decimals")
            fmt = fmt.get("type")
        elif isinstance(fmt, (list, tuple)) and fmt:
            fmt, *rest = fmt
            if rest:
                fmt_decimals = rest[0]

        if fmt == "currency" and numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                s = _format_number(num, doc.settings, fmt_decimals)
                return f"{currency_symbol}{s}"
            except Exception:
                return str(v)
        if fmt == "percent" and numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                return _format_percent(num, doc.settings, fmt_decimals)
            except Exception:
                return str(v)
        if fmt == "int" and numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                s = _format_number(num, doc.settings, 0)
                # drop decimal part entirely
                if doc.settings.decimal_separator in s:
                    s = s.split(doc.settings.decimal_separator)[0]
                return s
            except Exception:
                return str(v)
        if fmt == "thousands" and numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                return _format_number(num, doc.settings, 0)
            except Exception:
                return str(v)
        if isinstance(fmt, str) and fmt not in ("currency",):
            try:
                num = float(str(v).replace(",", ""))
                s = format(num, fmt)
                # If fmt uses ',' as thousands, '.' as decimals, translate
                if any(ch in s for ch in [",", "."]):
                    s = _apply_separators(s, doc.settings)
                return s
            except Exception:
                return str(v)
        # Default numeric formatting
        if numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                return _format_number(num, doc.settings)
            except Exception:
                return str(v)
        return str(v)

    data = []
    if header and cols:
        # Base header style (bold vs normal)
        if header_bold:
            base_header_style = ParagraphStyle(name="Header", parent=styles["Body"], fontName=_bold_font_name(theme.typography["font"]))
        else:
            base_header_style = styles["Body"]

        def ps_with_align(base, align_token):
            if not align_token:
                return base
            token = str(align_token).lower()
            align_map = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}
            if token not in align_map:
                return base
            return ParagraphStyle(name=base.name + f"-{token}", parent=base, alignment=align_map[token])

        # Build per-column header styles according to header_align (if provided)
        header_cells = []
        for i, h in enumerate(cols):
            if isinstance(header_align_prop, (list, tuple)):
                a = header_align_prop[i] if i < len(header_align_prop) else None
            else:
                a = header_align_prop
            st = ps_with_align(base_header_style, a)
            header_cells.append(Paragraph(str(h), st))
        data.append(header_cells)
    for row in rows:
        data.append([Paragraph(fmt_cell(ci, (row[ci] if ci < len(row) else None)), styles["Body"]) for ci in range(n_cols)])

    # Dynamic flowable to compute widths and apply styles at layout time
    class _DataTable(Flowable):
        def __init__(self, data, cols, align_prop, col_widths_prop, zebra, compact):
            super().__init__()
            self.data = data
            self.cols = cols
            self.align_prop = align_prop
            self.col_widths_prop = col_widths_prop
            self.zebra = zebra
            self.compact = compact
            self._t = None

        def _col_widths(self, availWidth):
            n = len(self.cols) if self.cols else (len(self.data[0]) if self.data else 0)
            if not n:
                return []
            if isinstance(self.col_widths_prop, (list, tuple)) and self.col_widths_prop:
                vals = []
                total_frac = 0.0
                for w in self.col_widths_prop:
                    if isinstance(w, (int, float)):
                        vals.append(float(w))
                    elif isinstance(w, str) and w.endswith("%"):
                        try:
                            frac = float(w[:-1]) / 100.0
                        except Exception:
                            frac = 0
                        vals.append(frac)
                        total_frac += frac
                    else:
                        vals.append(None)
                # If any percentages present, scale them to availWidth; None -> auto
                if total_frac > 0:
                    scaled = [vw * availWidth if isinstance(vw, float) and vw <= 1 else vw for vw in vals]
                    return scaled
                return vals
            # default: equal split
            return [availWidth / n] * n

        def _alignments(self, n_cols):
            def map_align(a):
                return {"left": "LEFT", "center": "CENTER", "right": "RIGHT"}.get(str(a).lower(), "LEFT")

            if isinstance(self.align_prop, (list, tuple)):
                arr = [map_align(a) for a in self.align_prop]
                if len(arr) < n_cols:
                    arr += ["LEFT"] * (n_cols - len(arr))
                return arr[:n_cols]
            elif self.align_prop:
                return [map_align(self.align_prop)] * n_cols
            else:
                return ["LEFT"] * n_cols

        def _build(self, availWidth):
            n_cols = len(self.data[0]) if self.data else 0
            col_widths = self._col_widths(availWidth)
            repeat = 1 if (header and cols) else 0
            t = Table(self.data, colWidths=col_widths or None, repeatRows=repeat)
            pad_y = theme.control["sizes"]["sm" if self.compact else "md"]["py"]
            pad_x = theme.control["sizes"]["sm" if self.compact else "md"]["px"]
            style_cmds = [
                ("LEFTPADDING", (0, 0), (-1, -1), pad_x),
                ("RIGHTPADDING", (0, 0), (-1, -1), pad_x),
                ("TOPPADDING", (0, 0), (-1, -1), pad_y),
                ("BOTTOMPADDING", (0, 0), (-1, -1), pad_y),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, theme.colors["border"]),
            ]
            # Header styling
            if self.cols:
                style_cmds += [
                    ("BACKGROUND", (0, 0), (-1, 0), theme.colors["surface"]),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.8, theme.colors["border"]),
                ]
            # Zebra striping
            if self.zebra and len(self.data) > (1 if self.cols else 0):
                start = 1 if self.cols else 0
                # Apply background to every other row starting from start
                for r in range(start, len(self.data)):
                    if (r - start) % 2 == 0:
                        style_cmds.append(("BACKGROUND", (0, r), (-1, r), theme.colors["surface"]))

            # Alignments per column
            aligns = self._alignments(n_cols)
            # If no align provided, use numeric detection
            if not self.align_prop:
                aligns = ["RIGHT" if numeric_cols[c] else "LEFT" for c in range(n_cols)]
            for c, a in enumerate(aligns):
                style_cmds.append(("ALIGN", (c, 0), (c, -1), a))

            # Header alignment via ParagraphStyle; table-level header align override not required

            t.setStyle(TableStyle(style_cmds))
            self._t = t

        def wrap(self, availWidth, availHeight):
            self._build(availWidth)
            return self._t.wrap(availWidth, availHeight)

        def split(self, availWidth, availHeight):
            if not self._t:
                self._build(availWidth)
            return self._t.split(availWidth, availHeight)

        def draw(self):
            self._t.drawOn(self.canv, 0, 0)

    return [_DataTable(data, cols, align_prop, col_widths_prop, zebra, compact)]


def _column_flowables(doc: Document, node: ColumnNode, styles) -> List[Flowable]:
    return _column_handler(doc, node, styles)


def _row_flowables(doc: Document, node: RowNode, styles) -> List[Flowable]:
    # Delegate to handler; leave legacy code below unreachable for now during refactor
    from .handlers.layout import row_flowables as _row_handler
    return _row_handler(doc, node, styles)
    gap = node.props.get("gap", doc.theme.spacing["md"])
    equal = node.props.get("equal", False)
    align = node.props.get("justify", "start")

    # Build per-child flowables and capture growth weights
    content_items: List[Flowable] = []
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
        content_items.append(cell_flow)
        w = 1.0
        if hasattr(child, "props"):
            w = float(child.props.get("grow", 1) or 1)
        weights.append(max(w, 0.0))

    # If not equal distribution, fall back to simple table with auto widths and spacer columns
    if not equal:
        cells: List[Flowable] = []
        for i, flow in enumerate(content_items):
            cells.append(flow)
            if i < len(content_items) - 1 and gap:
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

    # Equal or weighted distribution: use a dynamic table that computes column widths at wrap time
    class _WeightedRow(Flowable):
        def __init__(self, items: List[Flowable], weights: List[float], gap: int, align: str):
            super().__init__()
            self.items = items
            self.weights = [w if w > 0 else 0 for w in weights]
            self.gap = gap
            self.align = align
            self._table = None

        def _build_table(self, availWidth):
            # total gap width
            n = len(self.items)
            gaps = (n - 1) * self.gap if n > 1 else 0
            content_width = max(availWidth - gaps, 0)
            total_w = sum(self.weights) or n
            per_cols = [content_width * (w / total_w) for w in self.weights]
            # Build row cells and colWidths interleaving gaps
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

    return [_WeightedRow(content_items, weights, gap, align)]


def _separator_flowable(doc: Document, node: SeparatorNode, styles) -> Flowable:
    return _sep_handler(doc, node, styles)


def _labeled_separator_flowables(doc: Document, node: LabeledSeparatorNode, styles) -> List[Flowable]:
    return _labeled_sep_handler(doc, node, styles)


def _spacer_flowable(doc: Document, node: SpacerNode, styles) -> Flowable:
    # Delegate to handler; leave legacy code below unreachable for now during refactor
    from .handlers.layout import spacer_flowable as _spacer_handler
    return _spacer_handler(doc, node, styles)
    size_val = node.props.get("size")
    if isinstance(size_val, (int, float)):
        h = float(size_val)
    else:
        key = size_val or "md"
        h = float(doc.theme.spacing.get(key, doc.theme.spacing["md"]))
    # Very small heights can be collapsed by tables/layout; enforce a tiny minimum
    if h < 0:
        h = 0.0
    elif 0 < h < 0.5:
        h = 0.5
    return Spacer(1, h)


def _figure_export(obj, dpi: int) -> Tuple[str, bytes]:
    # Matplotlib / Seaborn / Plotnine path
    try:
        import matplotlib
        import matplotlib.pyplot as plt  # noqa: F401
        from matplotlib.figure import Figure as MplFigure
        from matplotlib.axes import Axes as MplAxes
    except Exception:
        matplotlib = None
        MplFigure = None
        MplAxes = None

    # Plotly path via kaleido
    try:
        import plotly.io as pio  # type: ignore
    except Exception:
        pio = None

    # Altair via vl-convert-python
    try:
        import altair as alt  # type: ignore
        import vl_convert as vlc  # type: ignore
    except Exception:
        alt = None
        vlc = None

    bio = io.BytesIO()

    # Plotly
    if pio is not None:
        try:
            import plotly.graph_objects as go  # type: ignore

            if isinstance(obj, go.Figure):
                if svg2rlg is not None:
                    svg = pio.to_image(obj, format="svg", scale=1)
                    return ("svg", svg)
                png = pio.to_image(obj, format="png", scale=max(dpi / 72, 1))
                return ("png", png)
        except Exception:
            pass

    # Altair
    if alt is not None and vlc is not None:
        try:
            if isinstance(obj, alt.Chart):
                if svg2rlg is not None:
                    svg = vlc.vegalite_to_svg(obj.to_json(), scale=1)
                    if isinstance(svg, str):
                        svg = svg.encode("utf-8")
                    return ("svg", svg)
                png = vlc.vegalite_to_png(obj.to_json(), scale=max(dpi / 72, 1))
                return ("png", png)
        except Exception:
            pass

    # Plotnine -> Matplotlib
    try:
        import plotnine as p9  # type: ignore

        if isinstance(obj, p9.ggplot.ggplot):  # type: ignore
            # Draw to create a matplotlib figure
            obj.draw()
            import matplotlib.pyplot as plt

            fig = plt.gcf()
            fig.savefig(bio, format="png", dpi=dpi, bbox_inches="tight")
            return ("png", bio.getvalue())
    except Exception:
        pass

    # Matplotlib Figure/Axes
    if MplFigure and isinstance(obj, MplFigure):
        obj.savefig(bio, format="png", dpi=dpi, bbox_inches="tight")
        return ("png", bio.getvalue())
    if MplAxes and isinstance(obj, MplAxes):
        fig = obj.figure
        fig.savefig(bio, format="png", dpi=dpi, bbox_inches="tight")
        return ("png", bio.getvalue())

    raise TypeError(
        "Unsupported figure type. Pass a Matplotlib Figure/Axes, plotnine ggplot, Plotly Figure (requires kaleido), or Altair Chart (requires vl-convert-python)."
    )


def _figure_flowables(doc: Document, node: FigureNode, styles) -> List[Flowable]:
    theme = doc.theme
    obj = node.props.get("obj")
    dpi = node.props.get("dpi", 144)
    fmt, data = _figure_export(obj, dpi)

    width = node.props.get("width")
    height = node.props.get("height")
    flows: List[Flowable] = []
    # Frame bounds (approx) to keep images within a page
    page_w, page_h = PAGE_SIZES.get(doc.size.upper(), A4)
    frame_w = page_w - doc.margin * 2
    frame_h = page_h - doc.margin * 2

    if fmt == "svg" and svg2rlg is not None:
        drawing = svg2rlg(io.BytesIO(data))
        dw, dh = float(getattr(drawing, 'width', 0) or 0), float(getattr(drawing, 'height', 0) or 0)
        if width or height:
            if width and height and dw and dh:
                s = min(width / dw, height / dh)
            elif width and dw:
                s = width / dw
            elif height and dh:
                s = height / dh
            else:
                s = 1
        else:
            # Fit to frame by default
            s = 1
            if dw and dh:
                s = min(frame_w / dw, frame_h / dh, 1)
        drawing.width, drawing.height = (dw * s if dw else 0), (dh * s if dh else 0)
        drawing.scale(s, s)
        align = node.props.get("align", "start")
        t = Table([[drawing]])
        t.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), {"start":"LEFT","center":"CENTER","end":"RIGHT"}.get(align, "LEFT")),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))
        flows.append(t)
    else:
        reader = ImageReader(io.BytesIO(data))
        px_w, px_h = reader.getSize()
        if width and height:
            target_w, target_h = width, height
        elif width:
            scale = width / float(px_w / 2)
            target_w, target_h = width, (px_h / 2) * scale
        elif height:
            scale = height / float(px_h / 2)
            target_w, target_h = (px_w / 2) * scale, height
        else:
            target_w, target_h = px_w / 2, px_h / 2
        # Fit to frame if oversized
        if target_w > frame_w or target_h > frame_h:
            s = min(frame_w / target_w, frame_h / target_h)
            target_w, target_h = target_w * s, target_h * s
        img = Image(io.BytesIO(data), width=target_w, height=target_h)
        align = node.props.get("align", "start")
        img.hAlign = {"start": "LEFT", "center": "CENTER", "end": "RIGHT"}.get(align, "LEFT")
        flows.append(img)

    caption = node.props.get("caption")
    if caption:
        cap = Paragraph(caption, styles["Muted"])
        flows.append(Spacer(1, theme.spacing["xs"]))
        flows.append(cap)
    # Return flows directly (no KeepTogether) to allow page breaks when inside tables/cards
    return flows


# legacy helper removed; color styling handled in handlers


def _to_flowables(doc: Document, node: Node, styles) -> List[Flowable]:
    try:
        h = dispatch.get(getattr(node, 'type', None))
        if h:
            return h(doc, node, styles)
    except Exception:
        pass
    if isinstance(node, TextNode):
        return [_text_flowable(doc, node, styles)]
    if isinstance(node, BadgeNode):
        return [_badge_flowable(doc, node, styles)]
    if isinstance(node, ButtonNode):
        return [_button_flowable(doc, node, styles)]
    if isinstance(node, SeparatorNode):
        return [_separator_flowable(doc, node, styles)]
    if isinstance(node, SpacerNode):
        return [_spacer_flowable(doc, node, styles)]
    if isinstance(node, FigureNode):
        return _figure_flowables(doc, node, styles)
    if isinstance(node, ImageNode):
        return _image_flowables(doc, node, styles)
    if isinstance(node, TableNode):
        return _table_flowables(doc, node, styles)
    if isinstance(node, LabeledSeparatorNode):
        return _labeled_separator_flowables(doc, node, styles)
    if isinstance(node, CardNode):
        return _card_flowables(doc, node, styles)
    if isinstance(node, RowNode):
        return _row_flowables(doc, node, styles)
    if isinstance(node, ColumnNode):
        return _column_flowables(doc, node, styles)
    if isinstance(node, PageNode):
        # treat as a vertical column
        return _column_flowables(doc, node, styles)
    # Fallback: ignore unknown nodes
    return []
def _badge_flowable(doc: Document, node: BadgeNode, styles) -> Table:
    return _badge_handler(doc, node, styles)


def _button_flowable(doc: Document, node: ButtonNode, styles) -> Table:
    return _button_handler(doc, node, styles)


def _image_flowables(doc: Document, node: ImageNode, styles) -> List[Flowable]:
    return _image_handler(doc, node, styles)


def _card_flowables(doc: Document, node: CardNode, styles) -> List[Flowable]:
    return _card_handler(doc, node, styles)


def _table_flowables(doc: Document, node: TableNode, styles) -> List[Flowable]:
    return _table_handler(doc, node, styles)


def _figure_flowables(doc: Document, node: FigureNode, styles) -> List[Flowable]:
    return _figure_handler(doc, node, styles)
