from dataclasses import dataclass
from reportlab.lib import colors


@dataclass
class Theme:
    name: str
    spacing: dict
    radii: dict
    colors: dict
    typography: dict
    control: dict  # control sizes for components


def default_theme() -> Theme:
    return Theme(
        name="default",
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
        control={
            # Horizontal and vertical paddings per size
            "sizes": {
                "sm": {"px": 8, "py": 4, "font": "size_sm"},
                "md": {"px": 12, "py": 6, "font": "size_base"},
                "lg": {"px": 16, "py": 8, "font": "size_lg"},
            }
        },
    )


def shadcn_theme() -> Theme:
    t = default_theme()
    t.name = "shadcn"
    # Adjust to be closer to shadcn defaults
    t.colors.update(
        {
            "surface": colors.HexColor("#f6f7f9"),
            "border": colors.HexColor("#e5e7eb"),
            "card": colors.HexColor("#ffffff"),
            "primary": colors.HexColor("#111827"),  # nearly black for text emphasis
        }
    )
    return t


def classic_theme() -> Theme:
    t = default_theme()
    t.name = "classic"
    t.typography["font"] = "Times-Roman"
    t.colors.update(
        {
            "surface": colors.HexColor("#f8f5f0"),
            "border": colors.HexColor("#d1d5db"),
            "primary": colors.HexColor("#1f2937"),
        }
    )
    return t


THEMES = {
    "default": default_theme,
    "shadcn": shadcn_theme,
    "classic": classic_theme,
}


def get_theme(name: str) -> Theme:
    fn = THEMES.get(name.lower())
    if not fn:
        return default_theme()
    return fn()
