from __future__ import annotations
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

from ....core.nodes import BadgeNode
from ....document import Document
from ....theme.tokens import size_token


def badge_flowable(doc: Document, node: BadgeNode, styles) -> Table:
    theme = doc.theme
    text = node.props.get("text", "")
    variant = node.props.get("variant", "default")
    size_in = node.props.get("size", "md")
    tok = size_token(theme, size_in)
    ctrl = theme.control["sizes"].get(tok, theme.control["sizes"]["md"])

    if variant in ("primary", "solid"):
        bg, fg, border = theme.colors["primary"], colors.white, theme.colors["primary"]
    elif variant == "success":
        bg, fg, border = theme.colors["success"], colors.white, theme.colors["success"]
    elif variant in ("outline", "secondary"):
        bg, fg, border = theme.colors["card"], theme.colors["foreground"], theme.colors["border"]
    elif variant == "danger":
        bg, fg, border = theme.colors["danger"], colors.white, theme.colors["danger"]
    else:
        bg, fg, border = theme.colors["surface"], theme.colors["foreground"], theme.colors["surface"]

    st = ParagraphStyle(name="BadgeText", parent=styles["Body"], textColor=fg)
    para = Paragraph(text, st)
    t = Table([[para]])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), ctrl["px"]),
        ("RIGHTPADDING", (0, 0), (-1, -1), ctrl["px"]),
        ("TOPPADDING", (0, 0), (-1, -1), ctrl["py"]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), ctrl["py"]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.5, border),
    ]))
    return t
