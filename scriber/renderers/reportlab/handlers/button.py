from __future__ import annotations
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

from ....core.nodes import ButtonNode
from ....document import Document
from ....theme.tokens import size_token


def button_flowable(doc: Document, node: ButtonNode, styles) -> Table:
    theme = doc.theme
    text = node.props.get("text", "")
    variant = node.props.get("variant", "primary")
    size_in = node.props.get("size", "md")
    tok = size_token(theme, size_in)
    ctrl = theme.control["sizes"].get(tok, theme.control["sizes"]["md"])

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

    st = ParagraphStyle(name="ButtonSized", parent=styles["Button"])
    st.textColor = fg
    st.fontSize = theme.typography[ctrl["font"]]
    st.leading = st.fontSize + 2
    para = Paragraph(text, st)
    t = Table([[para]])
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
