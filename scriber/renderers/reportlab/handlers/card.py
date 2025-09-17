from __future__ import annotations
from typing import List
from reportlab.platypus import Table, TableStyle, Flowable, Spacer
from reportlab.lib import colors

from ....core.nodes import CardNode
from ....document import Document


def card_flowables(doc: Document, node: CardNode, styles) -> List[Flowable]:
    theme = doc.theme
    # Collect child flowables
    from ....renderers.reportlab import _to_flowables
    content: List[Flowable] = []
    for child in node.children:
        content.extend(_to_flowables(doc, child, styles))
    rows = [[f] for f in content]
    if not rows:
        rows = [[Spacer(1, theme.spacing["sm"])]]
    t = Table(rows)

    pad = node.props.get("padding", theme.spacing["lg"])
    variant = node.props.get("variant", "default")
    radius_prop = node.props.get("radius")
    bg = theme.colors["card"] if variant in ("default", "outline") else theme.colors["surface"]
    border_color = theme.colors["border"] if variant in ("default", "outline") else theme.colors["surface"]

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

