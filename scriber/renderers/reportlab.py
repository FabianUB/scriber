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
    ListFlowable,
    Flowable,
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
    TextNode,
    PageNode,
)
from ..document import Document


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
    styles.add(
        ParagraphStyle(
            name="Button",
            parent=styles["Body"],
            alignment=1,  # center
        )
    )
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
    bg = {
        "default": theme.colors["surface"],
        "success": theme.colors["success"],
        "warning": theme.colors["warning"],
        "danger": theme.colors["danger"],
        "primary": theme.colors["primary"],
    }.get(variant, theme.colors["surface"])
    fg = colors.white if variant in {"primary", "success", "warning", "danger"} else theme.colors["foreground"]

    cell = Paragraph(text, _with_color(styles["Body"], fg))
    t = Table([[cell]])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("LEFTPADDING", (0, 0), (-1, -1), theme.spacing["sm"]),
                ("RIGHTPADDING", (0, 0), (-1, -1), theme.spacing["sm"]),
                ("TOPPADDING", (0, 0), (-1, -1), theme.spacing["xs"]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), theme.spacing["xs"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.5, bg),
            ]
        )
    )
    return t


def _button_flowable(doc: Document, node: ButtonNode, styles) -> Table:
    theme = doc.theme
    text = node.props.get("text", "")
    variant = node.props.get("variant", "primary")
    if variant == "outline":
        bg = theme.colors["card"]
        border = theme.colors["border"]
        fg = theme.colors["foreground"]
    else:
        bg = theme.colors["primary"]
        border = bg
        fg = colors.white
    cell = Paragraph(text, _with_color(styles["Button"], fg))
    t = Table([[cell]])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("GRID", (0, 0), (-1, -1), 0.8, border),
                ("LEFTPADDING", (0, 0), (-1, -1), theme.spacing["md"]),
                ("RIGHTPADDING", (0, 0), (-1, -1), theme.spacing["md"]),
                ("TOPPADDING", (0, 0), (-1, -1), theme.spacing["xs"]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), theme.spacing["xs"]),
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
    inner = ListFlowable(content)
    t = Table([[inner]])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), theme.colors["card"]),
                ("BOX", (0, 0), (-1, -1), 0.5, theme.colors["border"]),
                ("LEFTPADDING", (0, 0), (-1, -1), node.props.get("padding", theme.spacing["lg"])),
                ("RIGHTPADDING", (0, 0), (-1, -1), node.props.get("padding", theme.spacing["lg"])),
                ("TOPPADDING", (0, 0), (-1, -1), node.props.get("padding", theme.spacing["lg"])),
                ("BOTTOMPADDING", (0, 0), (-1, -1), node.props.get("padding", theme.spacing["lg"])),
            ]
        )
    )
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
    cells: List[ListFlowable | Flowable] = []
    for i, child in enumerate(node.children):
        child_flows = _to_flowables(doc, child, styles)
        cells.append(ListFlowable(child_flows))
        if i < len(node.children) - 1 and gap:
            cells.append(Spacer(gap, 1))
    data = [cells]
    t = Table(data)
    align = node.props.get("justify", "start")
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


def _separator_flowable(doc: Document, node: SeparatorNode, styles) -> Flowable:
    return HR()


def _spacer_flowable(doc: Document, node: SpacerNode, styles) -> Flowable:
    size_key = node.props.get("size") or "md"
    h = doc.theme.spacing.get(size_key, doc.theme.spacing["md"])
    return Spacer(1, h)


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

