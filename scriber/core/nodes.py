from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class Node:
    type: str
    props: dict = field(default_factory=dict)
    children: List[Node] = field(default_factory=list)

    def add(self, child: "Node") -> None:
        self.children.append(child)


# Leaf nodes
@dataclass
class TextNode(Node):
    def __init__(self, text: str, variant: str = "body", **props: Any) -> None:
        super().__init__("text", {"text": text, "variant": variant, **props})


@dataclass
class BadgeNode(Node):
    def __init__(self, text: str, variant: str = "default", **props: Any) -> None:
        super().__init__("badge", {"text": text, "variant": variant, **props})


@dataclass
class ButtonNode(Node):
    def __init__(self, text: str, variant: str = "primary", **props: Any) -> None:
        super().__init__("button", {"text": text, "variant": variant, **props})


@dataclass
class SeparatorNode(Node):
    def __init__(self, **props: Any) -> None:
        super().__init__("separator", {**props})


@dataclass
class SpacerNode(Node):
    def __init__(self, size: Optional[str] = None, **props: Any) -> None:
        super().__init__("spacer", {"size": size, **props})


@dataclass
class LabeledSeparatorNode(Node):
    def __init__(self, text: str, **props: Any) -> None:
        super().__init__("labeled_separator", {"text": text, **props})


@dataclass
class FigureNode(Node):
    def __init__(
        self,
        obj: Any,
        width: Optional[float] = None,
        height: Optional[float] = None,
        dpi: int = 144,
        align: str = "start",
        caption: Optional[str] = None,
        **props: Any,
    ) -> None:
        # Store object reference; renderer will resolve/export
        super().__init__(
            "figure",
            {"obj": obj, "width": width, "height": height, "dpi": dpi, "align": align, "caption": caption, **props},
        )


@dataclass
class ImageNode(Node):
    def __init__(
        self,
        source: Any,
        width: Optional[float] = None,
        height: Optional[float] = None,
        fit: str = "contain",
        align: str = "start",
        caption: Optional[str] = None,
        cache_key: Optional[str] = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "image",
            {
                "source": source,
                "width": width,
                "height": height,
                "fit": fit,
                "align": align,
                "caption": caption,
                "cache_key": cache_key,
                **props,
            },
        )


@dataclass
class TableNode(Node):
    def __init__(
        self,
        data: Any,
        columns: Optional[list] = None,
        align: Optional[Any] = None,
        header_align: Optional[Any] = None,
        header_bold: bool = True,
        formats: Optional[dict] = None,
        currency_symbol: str = "$",
        col_widths: Optional[list] = None,
        zebra: bool = False,
        header: bool = True,
        compact: bool = False,
        **props: Any,
    ) -> None:
        # Store the raw data source; renderer will normalize (supports pandas/polars/lists)
        super().__init__(
            "table",
            {
                "source": data,
                "columns": columns,
                "align": align,
                "header_align": header_align,
                "header_bold": header_bold,
                "formats": formats or {},
                "currency_symbol": currency_symbol,
                "col_widths": col_widths,
                "zebra": zebra,
                "header": header,
                "compact": compact,
                **props,
            },
        )



@dataclass
class CoverNode(Node):
    def __init__(self, title: str, subtitle: Optional[str] = None, meta: Optional[list] = None, align: str = "center", page_break: bool = True, **props: Any) -> None:
        super().__init__(
            "cover",
            {
                "title": title,
                "subtitle": subtitle,
                "meta": meta or [],
                "align": align,
                "page_break": page_break,
                **props,
            },
        )


@dataclass
class TOCNode(Node):
    def __init__(
        self,
        title: Optional[str] = None,
        depth: int = 3,
        dot_leader: bool = True,
        page_break: bool = True,
        title_align: str = "left",
        **props: Any,
    ) -> None:
        super().__init__(
            "toc",
            {
                "title": title,
                "depth": depth,
                "dot_leader": dot_leader,
                "page_break": page_break,
                "title_align": title_align,
                **props,
            },
        )

# Containers
@dataclass
class ContainerNode(Node):
    pass


@dataclass
class PageNode(ContainerNode):
    def __init__(self, **props: Any) -> None:
        super().__init__("page", {**props})


@dataclass
class RowNode(ContainerNode):
    def __init__(self, gap: Optional[int] = None, justify: str = "start", equal: bool = False, **props: Any) -> None:
        super().__init__("row", {"gap": gap, "justify": justify, "equal": equal, **props})


@dataclass
class ColumnNode(ContainerNode):
    def __init__(self, gap: Optional[int] = None, **props: Any) -> None:
        super().__init__("column", {"gap": gap, **props})


@dataclass
class CardNode(ContainerNode):
    def __init__(self, padding: Optional[int] = None, **props: Any) -> None:
        super().__init__("card", {"padding": padding, **props})
