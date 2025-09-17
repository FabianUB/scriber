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
    return Paragraph(text, style)

