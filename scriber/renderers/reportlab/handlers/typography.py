from __future__ import annotations
from typing import List
from reportlab.platypus import Paragraph

from ....core.nodes import TextNode
from ....document import Document


def text_flowable(doc: Document, node: TextNode, styles) -> Paragraph:
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
    para = Paragraph(text, style)

    heading_levels = {"h1": 0, "h2": 1, "h3": 2}
    if variant in heading_levels:
        level = heading_levels[variant]
        doc._heading_counter = getattr(doc, "_heading_counter", 0) + 1
        bookmark = f"heading_{doc._heading_counter}"
        para._bookmarkName = bookmark
        para._scriber_heading_level = level
        para._scriber_heading_text = str(text)
        para._scriber_bookmark_name = bookmark
        para.keepWithNext = True
    return para

