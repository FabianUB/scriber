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
    TextNode,
    PageNode,
)
from ..document import Document
from reportlab.lib.utils import ImageReader
import io
import os
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


class HR(Flowable):
    def __init__(self, width=1, color=colors.HexColor("#e5e7eb")):
        super().__init__()
        self.stroke_width = width
        self.color = color

    def wrap(self, availWidth, availHeight):
        return availWidth, self.stroke_width + 1

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.stroke_width)
        self.canv.line(0, 0, self.width, 0)


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

    pdf.build(story)


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
    size = node.props.get("size", "md")
    ctrl = theme.control["sizes"].get(size, theme.control["sizes"]["md"])

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
    size = node.props.get("size", "md")
    ctrl = theme.control["sizes"].get(size, theme.control["sizes"]["md"])

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
    n = len(rows)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("LEFTPADDING", (0, 0), (-1, -1), pad),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        # Default zero vertical padding for all rows
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        # Apply outer top/bottom padding only to first/last rows
        ("TOPPADDING", (0, 0), (-1, 0), pad),
        ("BOTTOMPADDING", (0, n - 1), (-1, n - 1), pad),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    t.setStyle(TableStyle(style_cmds))
    return [t]


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
    return HR()


def _spacer_flowable(doc: Document, node: SpacerNode, styles) -> Flowable:
    size_key = node.props.get("size") or "md"
    h = doc.theme.spacing.get(size_key, doc.theme.spacing["md"])
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
