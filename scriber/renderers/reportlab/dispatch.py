from __future__ import annotations
from typing import Callable, Dict, List
from reportlab.platypus import Flowable

from ...core.nodes import Node
from .handlers.layout import (
    separator_flowable,
    labeled_separator_flowables,
    row_flowables,
    column_flowables,
    spacer_flowable,
)
from .handlers.figure import figure_flowables
from .handlers.table import table_flowables
from .handlers.typography import text_flowable
from .handlers.button import button_flowable
from .handlers.badge import badge_flowable
from .handlers.card import card_flowables
from .handlers.document import cover_flowables, toc_flowables
from .handlers.image import image_flowables


Handler = Callable[[object, Node, object], List[Flowable]]


def _wrap_single(fn):
    def _inner(doc, node, styles):
        return [fn(doc, node, styles)]

    return _inner


HANDLERS: Dict[str, Handler] = {
    "separator": _wrap_single(separator_flowable),
    "labeled_separator": labeled_separator_flowables,
    "row": row_flowables,
    "column": column_flowables,
    "spacer": _wrap_single(spacer_flowable),
    "figure": figure_flowables,
    "image": image_flowables,
    "table": table_flowables,
    "text": _wrap_single(text_flowable),
    "button": _wrap_single(button_flowable),
    "badge": _wrap_single(badge_flowable),
    "card": card_flowables,
    "cover": cover_flowables,
    "toc": toc_flowables,
}


def get(node_type: str) -> Handler | None:
    return HANDLERS.get(node_type)
