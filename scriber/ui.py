from __future__ import annotations
from contextlib import contextmanager
from typing import Optional

from .core.nodes import (
    BadgeNode,
    ButtonNode,
    CardNode,
    ColumnNode,
    RowNode,
    SeparatorNode,
    SpacerNode,
    FigureNode,
    TextNode,
)
from .document import current_container, get_current_document


# Containers
@contextmanager
def row(gap: Optional[int] = None, justify: str = "start", equal: bool = False, grow: Optional[int] = None, **props):
    doc = get_current_document()
    if gap is None:
        gap = doc.theme.spacing["md"]
    if grow is not None:
        props["grow"] = grow
    node = RowNode(gap=gap, justify=justify, equal=equal, **props)
    current_container().add(node)
    # push
    from .document import _push, _pop  # local import to avoid cycle in type-checkers

    _push(node)
    try:
        yield node
    finally:
        _pop()


@contextmanager
def column(gap: Optional[int] = None, grow: Optional[int] = None, **props):
    doc = get_current_document()
    if gap is None:
        gap = doc.theme.spacing["md"]
    if grow is not None:
        props["grow"] = grow
    node = ColumnNode(gap=gap, **props)
    current_container().add(node)
    from .document import _push, _pop

    _push(node)
    try:
        yield node
    finally:
        _pop()


@contextmanager
def card(padding: Optional[int] = None, grow: Optional[int] = None, **props):
    doc = get_current_document()
    if padding is None:
        padding = doc.theme.spacing["lg"]
    if grow is not None:
        props["grow"] = grow
    node = CardNode(padding=padding, **props)
    current_container().add(node)
    from .document import _push, _pop

    _push(node)
    try:
        yield node
    finally:
        _pop()


# Components
def text(content: str, muted: bool = False, **props):
    variant = "muted" if muted else props.pop("variant", "body")
    current_container().add(TextNode(content, variant=variant, **props))


def h1(content: str, **props):
    current_container().add(TextNode(content, variant="h1", **props))


def h2(content: str, **props):
    current_container().add(TextNode(content, variant="h2", **props))


def h3(content: str, **props):
    current_container().add(TextNode(content, variant="h3", **props))


def badge(content: str, variant: str = "default", **props):
    current_container().add(BadgeNode(content, variant=variant, **props))


def button(content: str, variant: str = "primary", **props):
    current_container().add(ButtonNode(content, variant=variant, **props))


def separator(**props):
    current_container().add(SeparatorNode(**props))


def spacer(size: Optional[str] = None, **props):
    current_container().add(SpacerNode(size=size, **props))


def figure(obj, width: Optional[float] = None, height: Optional[float] = None, dpi: int = 144, align: str = "start", caption: Optional[str] = None, **props):
    current_container().add(FigureNode(obj=obj, width=width, height=height, dpi=dpi, align=align, caption=caption, **props))
