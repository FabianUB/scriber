from typing import Union
from .document import Document as _Document
from .theme.tokens import Theme, get_theme


def document(output_path: str, size: str = "A4", margin: int = 32, theme: Union[str, Theme, None] = "shadcn"):
    if isinstance(theme, str) or theme is None:
        theme_obj = get_theme(theme or "default")
    else:
        theme_obj = theme
    return _Document(output_path=output_path, size=size, margin=margin, theme=theme_obj)
