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
    TableNode,
    TextNode,
)
from .document import current_container, get_current_document
from .theme.tokens import spacing_value


# Containers
@contextmanager
def row(gap: Optional[object] = None, justify: str = "start", equal: bool = False, grow: Optional[int] = None, **props):
    doc = get_current_document()
    gap_pts = spacing_value(doc.theme, gap, default_key="md")
    if grow is not None:
        props["grow"] = grow
    node = RowNode(gap=gap_pts, justify=justify, equal=equal, **props)
    current_container().add(node)
    # push
    from .document import _push, _pop  # local import to avoid cycle in type-checkers

    _push(node)
    try:
        yield node
    finally:
        _pop()


@contextmanager
def column(gap: Optional[object] = None, grow: Optional[int] = None, **props):
    doc = get_current_document()
    gap_pts = spacing_value(doc.theme, gap, default_key="md")
    if grow is not None:
        props["grow"] = grow
    node = ColumnNode(gap=gap_pts, **props)
    current_container().add(node)
    from .document import _push, _pop

    _push(node)
    try:
        yield node
    finally:
        _pop()


@contextmanager
def card(padding: Optional[object] = None, grow: Optional[int] = None, radius: Optional[object] = None, **props):
    doc = get_current_document()
    pad_pts = spacing_value(doc.theme, padding, default_key="lg")
    if grow is not None:
        props["grow"] = grow
    if radius is not None:
        props["radius"] = radius
    node = CardNode(padding=pad_pts, **props)
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


def spacer(size: Optional[object] = None, **props):
    # Store numeric points directly to simplify renderer logic
    doc = get_current_document()
    h = spacing_value(doc.theme, size, default_key="md")
    current_container().add(SpacerNode(size=h, **props))


def number(value, kind: str = "decimal", decimals: Optional[int] = None, prefix: Optional[str] = None, suffix: Optional[str] = None, **props):
    """Render a formatted number using document settings.

    kind: 'decimal' | 'currency' | 'percent' | 'int' | 'thousands'
    decimals: override decimals for decimal/currency/percent
    prefix/suffix: extra strings to add around the formatted value
    """
    doc = get_current_document()
    from .core.nodes import TextNode
    from .renderers.reportlab import _format_number, _format_percent, _apply_separators  # type: ignore

    s = str(value)
    try:
        num = float(str(value).replace(",", ""))
        if kind == "currency":
            s = _format_number(num, doc.settings, decimals)
            s = f"{doc.settings.currency_symbol}{s}"
        elif kind == "percent":
            s = _format_percent(num, doc.settings, decimals)
        elif kind == "int":
            s = _format_number(num, doc.settings, 0)
            # remove decimals entirely
            if doc.settings.decimal_separator in s:
                s = s.split(doc.settings.decimal_separator)[0]
        elif kind == "thousands":
            s = _format_number(num, doc.settings, 0)
        else:
            s = _format_number(num, doc.settings, decimals)
    except Exception:
        # leave as string
        pass

    if prefix:
        s = f"{prefix}{s}"
    if suffix:
        s = f"{s}{suffix}"
    current_container().add(TextNode(s, **props))


def table(data, columns: Optional[list] = None, align: Optional[object] = None, col_widths: Optional[list] = None, zebra: bool = False, header: bool = True, compact: bool = False, **props):
    current_container().add(
        TableNode(
            data=data,
            columns=columns,
            align=align,
            col_widths=col_widths,
            zebra=zebra,
            header=header,
            compact=compact,
            **props,
        )
    )


def figure(obj, width: Optional[float] = None, height: Optional[float] = None, dpi: int = 144, align: str = "start", caption: Optional[str] = None, **props):
    current_container().add(FigureNode(obj=obj, width=width, height=height, dpi=dpi, align=align, caption=caption, **props))
