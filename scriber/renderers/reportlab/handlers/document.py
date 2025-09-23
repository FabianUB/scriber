from __future__ import annotations
from typing import List, Sequence, Tuple

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from ....core.nodes import CoverNode, TOCNode
from ....document import Document

_ALIGN_MAP = {
    "left": TA_LEFT,
    "center": TA_CENTER,
    "right": TA_RIGHT,
}

_TABLE_ALIGN = {
    "left": "LEFT",
    "center": "CENTER",
    "right": "RIGHT",
}


def cover_flowables(doc: Document, node: CoverNode, styles) -> List[Flowable]:
    title = node.props.get("title", "")
    subtitle = node.props.get("subtitle")
    meta: Sequence[Tuple[str, str]] = node.props.get("meta", []) or []
    align = (node.props.get("align") or "center").lower()
    page_break = bool(node.props.get("page_break", True))

    align = align if align in _ALIGN_MAP else "center"
    flows: List[Flowable] = []

    if getattr(doc, "_story_started", False) and not getattr(doc, "_last_flowable_pagebreak", False):
        flows.append(PageBreak())

    spacing = doc.theme.spacing
    colors_theme = doc.theme.colors

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["H1"],
        alignment=_ALIGN_MAP[align],
        fontSize=styles["H1"].fontSize + 4,
        leading=styles["H1"].leading + 4,
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["H2"],
        alignment=_ALIGN_MAP[align],
        textColor=colors_theme.get("muted", colors.HexColor("#6b7280")),
    )
    meta_label_style = ParagraphStyle(
        "CoverMetaLabel",
        parent=styles["Body"],
        textColor=colors_theme.get("muted", colors.HexColor("#6b7280")),
    )
    meta_value_style = ParagraphStyle(
        "CoverMetaValue",
        parent=styles["Body"],
    )

    flows.append(Spacer(1, spacing.get("2xl", 64) * 1.5))
    flows.append(Paragraph(title, title_style))

    if subtitle:
        flows.append(Spacer(1, spacing.get("md", 16)))
        flows.append(Paragraph(str(subtitle), subtitle_style))

    if meta:
        flows.append(Spacer(1, spacing.get("xl", 24)))
        table_data = []
        for label, value in meta:
            table_data.append([
                Paragraph(f"<b>{label}</b>", meta_label_style),
                Paragraph(str(value), meta_value_style),
            ])
        meta_table = Table(table_data, hAlign=_TABLE_ALIGN[align])
        meta_table.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ]
            )
        )
        flows.append(meta_table)

    is_last = bool(doc.root.children) and doc.root.children[-1] is node
    if page_break and not is_last:
        flows.append(PageBreak())

    return flows


def toc_flowables(doc: Document, node: TOCNode, styles) -> List[Flowable]:
    title = node.props.get("title")
    depth = int(node.props.get("depth", 3))
    dot_leader = bool(node.props.get("dot_leader", True))
    page_break = bool(node.props.get("page_break", True))
    title_align = (node.props.get("title_align") or "left").lower()
    title_align = title_align if title_align in _ALIGN_MAP else "left"

    depth = max(1, min(depth, 6))

    flows: List[Flowable] = []

    if getattr(doc, "_story_started", False) and not getattr(doc, "_last_flowable_pagebreak", False):
        flows.append(PageBreak())

    if title:
        title_style = ParagraphStyle(
            "TOCTitle",
            parent=styles["H2"],
            alignment=_ALIGN_MAP[title_align],
        )
        flows.append(Paragraph(str(title), title_style))
        flows.append(Spacer(1, doc.theme.spacing.get("md", 16)))

    toc = TableOfContents()

    body_style = styles["Body"]
    level_styles = []
    base_indent = doc.theme.spacing.get("md", 16)
    for level in range(depth):
        level_styles.append(
            ParagraphStyle(
                f"TOCLevel{level}",
                parent=body_style,
                leftIndent=base_indent * level,
                firstLineIndent=0,
                spaceBefore=doc.theme.spacing.get("xs", 8) if level > 0 else 0,
                leading=body_style.leading,
                fontSize=max(body_style.fontSize - level, 8),
            )
        )
    toc.levelStyles = level_styles
    if dot_leader:
        toc.dotsMinLevel = 0
    else:
        toc.dotsMinLevel = depth + 1

    flows.append(toc)

    is_last = bool(doc.root.children) and doc.root.children[-1] is node
    if page_break and not is_last:
        flows.append(PageBreak())

    return flows
