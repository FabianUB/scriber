from dataclasses import dataclass
from reportlab.lib import colors


@dataclass
class Theme:
    spacing: dict
    radii: dict
    colors: dict
    typography: dict


def default_theme() -> Theme:
    return Theme(
        spacing={
            "xs": 4,
            "sm": 8,
            "md": 12,
            "lg": 16,
            "xl": 24,
            "2xl": 32,
        },
        radii={
            "sm": 2,
            "md": 4,
            "lg": 8,
        },
        colors={
            "foreground": colors.black,
            "muted": colors.HexColor("#6b7280"),
            "surface": colors.whitesmoke,
            "border": colors.HexColor("#e5e7eb"),
            "primary": colors.HexColor("#2563eb"),
            "success": colors.HexColor("#16a34a"),
            "warning": colors.HexColor("#ca8a04"),
            "danger": colors.HexColor("#dc2626"),
            "card": colors.HexColor("#ffffff"),
        },
        typography={
            "font": "Helvetica",
            "size_sm": 9,
            "size_base": 10,
            "size_lg": 12,
            "h1": 22,
            "h2": 18,
            "h3": 14,
        },
    )

