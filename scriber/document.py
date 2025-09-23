from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import List, Optional

from .core.nodes import ColumnNode, ContainerNode, PageNode
from .theme.tokens import Theme, default_theme
from .settings import Settings, default_settings


_container_stack: List[ContainerNode] = []
_current_doc: Optional["Document"] = None


def _push(container: ContainerNode) -> None:
    _container_stack.append(container)


def _pop() -> None:
    if _container_stack:
        _container_stack.pop()


def current_container() -> ContainerNode:
    if not _container_stack:
        raise RuntimeError("No active container. Use pdf.document(...) context.")
    return _container_stack[-1]


@dataclass
class Document:
    output_path: str
    size: str = "A4"
    margin: int = 32
    theme: Theme = field(default_factory=default_theme)
    settings: Settings = field(default_factory=default_settings)
    # Simple header/footer configuration
    header: object | None = None  # str or callable(canvas, doc_rl, doc)
    header_align: str = "left"
    footer: object | None = None  # str or callable(canvas, doc_rl, doc)
    page_numbers: object | None = "xofy"  # 'x', 'xofy', False

    def __post_init__(self) -> None:
        self.header_align = (self.header_align or "left").lower()
        if self.header_align not in {"left", "right", "center"}:
            self.header_align = "left"
        self._heading_counter = 0
        self._has_toc = False
        self._toc_depth = 0
        self._outline_depth = 3
        self._story_started = False
        self._last_flowable_pagebreak = False
        self.root = ColumnNode(gap=self.theme.spacing["md"])  # default vertical flow

    def __enter__(self) -> "Document":
        global _current_doc
        if _current_doc is not None:
            raise RuntimeError("Nested documents are not supported.")
        _current_doc = self
        _push(self.root)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        from .renderers.reportlab import render

        # Pop any remaining containers to avoid leaking state
        _container_stack.clear()
        global _current_doc
        try:
            render(self, self.output_path)
        finally:
            _current_doc = None


def get_current_document() -> Document:
    if _current_doc is None:
        raise RuntimeError("No active document context.")
    return _current_doc


@contextmanager
def page(**props):
    doc = get_current_document()
    node = PageNode(**props)
    doc.root.add(node)
    _push(node)
    try:
        yield node
    finally:
        _pop()
