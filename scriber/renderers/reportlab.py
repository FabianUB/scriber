from __future__ import annotations
from typing import List, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    KeepInFrame,
    Flowable,
    Image,
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from ..core.nodes import (
    BadgeNode,
    ButtonNode,
    CardNode,
    ColumnNode,
    Node,
    RowNode,
    SeparatorNode,
    SpacerNode,
    FigureNode,
    TableNode,
    LabeledSeparatorNode,
    TextNode,
    PageNode,
)
from ..document import Document
from .handlers.layout import separator_flowable as _sep_handler, labeled_separator_flowables as _labeled_sep_handler
from ..settings import Settings
from ..theme.tokens import size_token
from reportlab.lib.utils import ImageReader
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
    theme = doc.theme
    base_font = theme.typography["font"]
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName=base_font,
            fontSize=theme.typography["size_base"],
            leading=theme.typography["size_base"] + 2,
            textColor=theme.colors["foreground"],
        )
    )
    styles.add(
        ParagraphStyle(
            name="Muted",
            parent=styles["Body"],
            textColor=theme.colors["muted"],
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1",
            parent=styles["Body"],
            fontSize=theme.typography["h1"],
            leading=theme.typography["h1"] + 2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2",
            parent=styles["Body"],
            fontSize=theme.typography["h2"],
            leading=theme.typography["h2"] + 2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H3",
            parent=styles["Body"],
            fontSize=theme.typography["h3"],
            leading=theme.typography["h3"] + 2,
        )
    )
    styles.add(ParagraphStyle(name="Button", parent=styles["Body"], alignment=1))
    return styles


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


class HR(Flowable):
    def __init__(self, width=1, color=colors.HexColor("#e5e7eb"), style: str = "solid", m_top: float = 0.0, m_bottom: float = 0.0):
        super().__init__()
        self.stroke_width = width  # thickness in points
        self.color = color
        self._avail_width = 0
        self.style = style
        self.m_top = max(m_top, 0.0)
        self.m_bottom = max(m_bottom, 0.0)

    def wrap(self, availWidth, availHeight):
        self._avail_width = availWidth
        # Ensure the flowable reserves at least the stroke thickness in height
        h = self.m_top + max(self.stroke_width, 0.5) + self.m_bottom
        return availWidth, h

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.stroke_width)
        # Dash styles
        s = (self.style or "solid").lower()
        if s == "dashed":
            self.canv.setDash(6, 3)
        elif s == "dotted":
            self.canv.setDash(1, 2)
        else:
            self.canv.setDash()  # solid
        # Draw a horizontal line across the available width accounting for margins
        y = self.m_bottom + self.stroke_width / 2.0
        self.canv.line(0, y, self._avail_width, y)


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

    # root is a Column; iterate children (pages/containers)
    for child in doc.root.children:
        story.extend(_to_flowables(doc, child, styles))

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
                canv.drawString(rl_doc.leftMargin, y, str(doc.header))
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

    # Page numbering canvas
    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            # Save current page state, but do not finalize the page yet
            self._saved_page_states.append(dict(self.__dict__))
            # Start a new page without emitting the current one
            canvas.Canvas._startPage(self)

        def save(self):
            """Add page info to each page (page x of y)."""
            # Include last page state
            self._saved_page_states.append(dict(self.__dict__))
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

    pdf.build(story, onFirstPage=_draw_header_footer, onLaterPages=_draw_header_footer, canvasmaker=NumberedCanvas)


def _text_flowable(doc: Document, node: TextNode, styles) -> Paragraph:
    variant = node.props.get("variant", "body")
    text = node.props.get("text", "")
    style_map = {
        "body": styles["Body"],
        "muted": styles["Muted"],
        "h1": styles["H1"],
        "h2": styles["H2"],
        "h3": styles["H3"],
    }
    style = style_map.get(variant, styles["Body"])
    return Paragraph(text, style)


def _badge_flowable(doc: Document, node: BadgeNode, styles) -> Table:
    theme = doc.theme
    text = node.props.get("text", "")
    variant = node.props.get("variant", "default")
    size_in = node.props.get("size", "md")
    tok = size_token(theme, size_in)
    ctrl = theme.control["sizes"].get(tok, theme.control["sizes"]["md"])

    # shadcn-inspired variants
    if variant in ("primary", "solid"):
        bg, fg, border = theme.colors["primary"], colors.white, theme.colors["primary"]
    elif variant == "success":
        bg, fg, border = theme.colors["success"], colors.white, theme.colors["success"]
    elif variant in ("outline", "secondary"):
        bg, fg, border = theme.colors["card"], theme.colors["foreground"], theme.colors["border"]
    elif variant == "danger":
        bg, fg, border = theme.colors["danger"], colors.white, theme.colors["danger"]
    else:  # default
        bg, fg, border = theme.colors["surface"], theme.colors["foreground"], theme.colors["surface"]

    cell = Paragraph(text, _with_color(styles["Body"], fg))
    t = Table([[cell]])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("LEFTPADDING", (0, 0), (-1, -1), ctrl["px"]),
                ("RIGHTPADDING", (0, 0), (-1, -1), ctrl["px"]),
                ("TOPPADDING", (0, 0), (-1, -1), ctrl["py"]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), ctrl["py"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.5, border),
            ]
        )
    )
    return t


def _button_flowable(doc: Document, node: ButtonNode, styles) -> Table:
    theme = doc.theme
    text = node.props.get("text", "")
    variant = node.props.get("variant", "primary")
    size_in = node.props.get("size", "md")
    tok = size_token(theme, size_in)
    ctrl = theme.control["sizes"].get(tok, theme.control["sizes"]["md"])

    # Variants
    if variant == "outline":
        bg, border, fg = theme.colors["card"], theme.colors["border"], theme.colors["foreground"]
    elif variant == "ghost":
        bg, border, fg = theme.colors["card"], theme.colors["card"], theme.colors["primary"]
    elif variant == "secondary":
        bg, border, fg = theme.colors["surface"], theme.colors["surface"], theme.colors["foreground"]
    elif variant == "danger":
        bg, border, fg = theme.colors["danger"], theme.colors["danger"], colors.white
    else:  # primary/default
        bg, border, fg = theme.colors["primary"], theme.colors["primary"], colors.white

    cell_style = _with_color(styles["Button"], fg)
    # Adjust font size for control size
    cell_style.fontSize = theme.typography[ctrl["font"]]
    cell_style.leading = cell_style.fontSize + 2
    cell = Paragraph(text, cell_style)
    t = Table([[cell]])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("GRID", (0, 0), (-1, -1), 0.8, border),
                ("LEFTPADDING", (0, 0), (-1, -1), ctrl["px"]),
                ("RIGHTPADDING", (0, 0), (-1, -1), ctrl["px"]),
                ("TOPPADDING", (0, 0), (-1, -1), ctrl["py"]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), ctrl["py"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return t


def _card_flowables(doc: Document, node: CardNode, styles) -> List[Flowable]:
    theme = doc.theme
    content: List[Flowable] = []
    for child in node.children:
        content.extend(_to_flowables(doc, child, styles))

    # Build a single-column table where each child is its own row.
    # This allows natural page-splitting (no giant KeepTogether cell).
    rows = [[f] for f in content]
    if not rows:
        rows = [[Spacer(1, theme.spacing["sm"])]]
    t = Table(rows)

    pad = node.props.get("padding", theme.spacing["lg"])
    variant = node.props.get("variant", "default")
    bg = theme.colors["card"] if variant in ("default", "outline") else theme.colors["surface"]
    border_color = theme.colors["border"] if variant in ("default", "outline") else theme.colors["surface"]
    radius_prop = node.props.get("radius")
    # Map radius prop to numeric points
    if isinstance(radius_prop, str):
        radius = float(theme.radii.get(radius_prop, 0))
    elif isinstance(radius_prop, (int, float)):
        radius = float(radius_prop)
    else:
        radius = 0.0

    if radius <= 0:
        n = len(rows)
        style_cmds = [
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("BOX", (0, 0), (-1, -1), 0.5, border_color),
            ("LEFTPADDING", (0, 0), (-1, -1), pad),
            ("RIGHTPADDING", (0, 0), (-1, -1), pad),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, 0), pad),
            ("BOTTOMPADDING", (0, n - 1), (-1, n - 1), pad),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
        t.setStyle(TableStyle(style_cmds))
        return [t]

    # Rounded card path: keep content together; intended for small cards
    class RoundedCard(Flowable):
        def __init__(self, inner: Table, pad: float, bg, border_color, radius: float):
            super().__init__()
            self.inner = inner
            self.pad = pad
            self.bg = bg
            self.border_color = border_color
            self.radius = radius
            self._w = 0
            self._h = 0

        def wrap(self, availWidth, availHeight):
            iw, ih = self.inner.wrap(max(availWidth - 2 * self.pad, 0), max(availHeight - 2 * self.pad, 0))
            self._w = min(availWidth, iw + 2 * self.pad)
            self._h = ih + 2 * self.pad
            return self._w, self._h

        def draw(self):
            c = self.canv
            c.saveState()
            c.setFillColor(self.bg)
            c.setStrokeColor(self.border_color)
            c.setLineWidth(0.5)
            c.roundRect(0, 0, self._w, self._h, self.radius, stroke=1, fill=1)
            c.restoreState()
            self.inner.drawOn(c, self.pad, self.pad)

    # Prepare inner table paddings since outer rounded box provides padding
    n = len(rows)
    t.setStyle(
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
    return [RoundedCard(t, pad, bg, border_color, radius)]


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
    flows: List[Flowable] = []
    gap = node.props.get("gap", doc.theme.spacing["md"])
    for i, child in enumerate(node.children):
        flows.extend(_to_flowables(doc, child, styles))
        if i < len(node.children) - 1 and gap:
            flows.append(Spacer(1, gap))
    return flows


def _row_flowables(doc: Document, node: RowNode, styles) -> List[Flowable]:
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


def _with_color(style: ParagraphStyle, color):
    s = ParagraphStyle(name=style.name + "+color", parent=style)
    s.textColor = color
    return s


def _to_flowables(doc: Document, node: Node, styles) -> List[Flowable]:
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
