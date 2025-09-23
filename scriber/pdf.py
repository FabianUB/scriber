from typing import Union, Optional, Dict, Any
from .document import Document as _Document
from .theme.tokens import Theme, get_theme
from .settings import Settings, default_settings


def document(
    output_path: str,
    size: str = "A4",
    margin: int = 32,
    theme: Union[str, Theme, None] = "default",
    *,
    settings: Optional[Union[Settings, Dict[str, Any]]] = None,
    currency: Optional[str] = None,
    decimal: Optional[str] = None,
    thousands: Optional[str] = None,
    decimals: Optional[int] = None,
    font: Optional[str] = None,
    header: Optional[object] = None,
    header_align: str = "left",
    footer: Optional[object] = None,
    page_numbers: Optional[object] = "xofy",
):
    # Theme selection
    if isinstance(theme, str) or theme is None:
        # Single default theme for now; name is accepted but ignored
        theme_obj = get_theme("default")
    else:
        theme_obj = theme

    # Font override (default for document)
    if font:
        theme_obj.typography["font"] = font

    # Settings assembly
    if isinstance(settings, Settings):
        settings_obj = settings
    else:
        settings_obj = default_settings()
        if isinstance(settings, dict):
            for k, v in settings.items():
                if hasattr(settings_obj, k):
                    setattr(settings_obj, k, v)
    if currency is not None:
        settings_obj.currency_symbol = currency
    if decimal is not None:
        settings_obj.decimal_separator = decimal
    if thousands is not None:
        settings_obj.thousands_separator = thousands
    if decimals is not None:
        settings_obj.number_decimals = int(decimals)

    header_align_value = (header_align or "left").lower()

    return _Document(
        output_path=output_path,
        size=size,
        margin=margin,
        theme=theme_obj,
        settings=settings_obj,
        header=header,
        header_align=header_align_value,
        footer=footer,
        page_numbers=page_numbers,
    )
