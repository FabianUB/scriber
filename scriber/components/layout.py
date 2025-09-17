from __future__ import annotations
from typing import Optional

from ..core.nodes import SeparatorNode, LabeledSeparatorNode
from ..document import get_current_document, current_container


def separator(
    thickness: Optional[float] = None,
    color: Optional[object] = None,
    style: Optional[str] = None,
    margin: Optional[float] = None,
    margin_top: Optional[float] = None,
    margin_bottom: Optional[float] = None,
    **props,
):
    if thickness is not None:
        props["thickness"] = thickness
    if color is not None:
        props["color"] = color
    if style is not None:
        props["style"] = style
    if margin is not None:
        props["margin_top"] = margin
        props["margin_bottom"] = margin
    if margin_top is not None:
        props["margin_top"] = margin_top
    if margin_bottom is not None:
        props["margin_bottom"] = margin_bottom
    current_container().add(SeparatorNode(**props))


def labeled_separator(
    text: str,
    thickness: Optional[float] = None,
    color: Optional[object] = None,
    style: Optional[str] = None,
    gap: Optional[float] = None,
    margin: Optional[float] = None,
    margin_top: Optional[float] = None,
    margin_bottom: Optional[float] = None,
    muted: bool = True,
    **props,
):
    if thickness is not None:
        props["thickness"] = thickness
    if color is not None:
        props["color"] = color
    if style is not None:
        props["style"] = style
    if gap is not None:
        props["gap"] = gap
    if margin is not None:
        props["margin_top"] = margin
        props["margin_bottom"] = margin
    if margin_top is not None:
        props["margin_top"] = margin_top
    if margin_bottom is not None:
        props["margin_bottom"] = margin_bottom
    props["muted"] = muted
    current_container().add(LabeledSeparatorNode(text, **props))

