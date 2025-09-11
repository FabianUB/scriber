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
    def __init__(self, gap: Optional[int] = None, justify: str = "start", **props: Any) -> None:
        super().__init__("row", {"gap": gap, "justify": justify, **props})


@dataclass
class ColumnNode(ContainerNode):
    def __init__(self, gap: Optional[int] = None, **props: Any) -> None:
        super().__init__("column", {"gap": gap, **props})


@dataclass
class CardNode(ContainerNode):
    def __init__(self, padding: Optional[int] = None, **props: Any) -> None:
        super().__init__("card", {"padding": padding, **props})

