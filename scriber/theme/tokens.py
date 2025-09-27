from dataclasses import dataclass
from reportlab.lib import colors
import warnings


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


def get_theme(_: str | None) -> Theme:
    """Return the single default theme. Name is ignored for now."""
    return default_theme()


# --- Size resolution helpers ---

def spacing_value(theme: Theme, value, *, default_key: str = "md") -> float:
    """Resolve a spacing token or numeric into a point value.

    - If value is None: use theme.spacing[default_key]
    - If str: look up in theme.spacing
    - If int/float: use directly (treated as points)
    """
    if value is None:
        return float(theme.spacing[default_key])
    if isinstance(value, str):
        if value in theme.spacing:
            return float(theme.spacing[value])
        warnings.warn(
            f"Invalid spacing token '{value}'. Valid tokens: {sorted(theme.spacing.keys())}. "
            "Provide a numeric value (points) or a valid token.",
            stacklevel=3,
        )
        return float(theme.spacing[default_key])
    try:
        return float(value)
    except Exception:
        warnings.warn(
            f"Unable to interpret spacing value '{value}'. Use a numeric value (points) or one of "
            f"{sorted(theme.spacing.keys())}.",
            stacklevel=3,
        )
        return float(theme.spacing[default_key])


def size_token(theme: Theme, value, *, choices=("sm", "md", "lg")) -> str:
    """Resolve a control size token from a token or numeric value.

    - If value is a valid token: return it
    - If numeric: map by thresholds using theme.spacing: <= sm -> sm, <= md -> md, else lg
    """
    if isinstance(value, str):
        if value in choices:
            return value
        warnings.warn(
            f"Invalid size token '{value}'. Valid tokens: {sorted(choices)}. "
            "Provide a numeric value to map automatically.",
            stacklevel=3,
        )
        return "md"
    # Numeric mapping by spacing thresholds
    sm = float(theme.spacing.get("sm", 8))
    md = float(theme.spacing.get("md", 12))
    try:
        v = float(value)
    except Exception:
        warnings.warn(
            f"Unable to interpret size value '{value}'. Use a numeric value or one of {sorted(choices)}.",
            stacklevel=3,
        )
        return "md"
    if v <= sm:
        return "sm"
    if v <= md:
        return "md"
    return "lg"
