from __future__ import annotations
from reportlab.lib import colors
from reportlab.platypus import Flowable
from ...settings import Settings
import io

try:
    from svglib.svglib import svg2rlg  # type: ignore
except Exception:
    svg2rlg = None


def apply_separators(s: str, settings: Settings) -> str:
    thou = settings.thousands_separator
    dec = settings.decimal_separator
    if thou == "," and dec == ".":
        return s
    s = s.replace(",", "<T>").replace(".", "<D>")
    s = s.replace("<T>", thou).replace("<D>", dec)
    return s


def format_number(num: float, settings: Settings, decimals: int | None = None) -> str:
    d = settings.number_decimals if decimals is None else int(decimals)
    base = f"{num:,.{d}f}"
    return apply_separators(base, settings)


def format_percent(num: float, settings: Settings, decimals: int | None = None) -> str:
    d = settings.percent_decimals if decimals is None else int(decimals)
    base = f"{num*100:,.{d}f}%"
    return apply_separators(base, settings)


def figure_export(obj, dpi: int) -> tuple[str, bytes]:
    # Matplotlib / Seaborn / Plotnine path
    try:
        import matplotlib
        import matplotlib.pyplot as plt  # noqa: F401
        from matplotlib.figure import Figure as MplFigure
        from matplotlib.axes import Axes as MplAxes
    except Exception:
        matplotlib = None
        MplFigure = None
        MplAxes = None

    # Plotly via kaleido
    try:
        import plotly.io as pio  # type: ignore
    except Exception:
        pio = None

    # Altair via vl-convert-python
    try:
        import altair as alt  # type: ignore
        import vl_convert as vlc  # type: ignore
    except Exception:
        alt = None
        vlc = None

    bio = io.BytesIO()

    if pio is not None:
        try:
            import plotly.graph_objects as go  # type: ignore
            if isinstance(obj, go.Figure):
                if svg2rlg is not None:
                    svg = pio.to_image(obj, format="svg", scale=1)
                    return ("svg", svg)
                png = pio.to_image(obj, format="png", scale=max(dpi / 72, 1))
                return ("png", png)
        except Exception:
            pass

    if alt is not None and vlc is not None:
        try:
            if isinstance(obj, alt.Chart):
                if svg2rlg is not None:
                    svg = vlc.vegalite_to_svg(obj.to_json(), scale=1)
                    if isinstance(svg, str):
                        svg = svg.encode("utf-8")
                    return ("svg", svg)
                png = vlc.vegalite_to_png(obj.to_json(), scale=max(dpi / 72, 1))
                return ("png", png)
        except Exception:
            pass

    try:
        import plotnine as p9  # type: ignore
        if isinstance(obj, p9.ggplot.ggplot):  # type: ignore
            obj.draw()
            import matplotlib.pyplot as plt
            fig = plt.gcf()
            fig.savefig(bio, format="png", dpi=dpi, bbox_inches="tight")
            return ("png", bio.getvalue())
    except Exception:
        pass

    if MplFigure and isinstance(obj, MplFigure):
        obj.savefig(bio, format="png", dpi=dpi, bbox_inches="tight")
        return ("png", bio.getvalue())
    if MplAxes and isinstance(obj, MplAxes):
        fig = obj.figure
        fig.savefig(bio, format="png", dpi=dpi, bbox_inches="tight")
        return ("png", bio.getvalue())

    raise TypeError(
        "Unsupported figure type. Use Matplotlib Figure/Axes, plotnine ggplot, Plotly Figure (kaleido), or Altair Chart (vl-convert)."
    )


def resolve_color(doc, color_spec):
    if color_spec is None:
        return None
    if isinstance(color_spec, str):
        if color_spec in doc.theme.colors:
            return doc.theme.colors[color_spec]
        try:
            return colors.HexColor(color_spec)
        except Exception:
            return None
    return color_spec


class HR(Flowable):
    def __init__(self, width=1, color=colors.HexColor("#e5e7eb"), style: str = "solid", m_top: float = 0.0, m_bottom: float = 0.0):
        super().__init__()
        self.stroke_width = width  # thickness in points
        self.color = color
        self._avail_width = 0
        self.style = style
        self.m_top = max(m_top, 0.0)
        self.m_bottom = max(m_bottom, 0.0)

    def wrap(self, availWidth, availHeight):
        self._avail_width = availWidth
        h = self.m_top + max(self.stroke_width, 0.5) + self.m_bottom
        return availWidth, h

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.stroke_width)
        s = (self.style or "solid").lower()
        if s == "dashed":
            self.canv.setDash(6, 3)
        elif s == "dotted":
            self.canv.setDash(1, 2)
        else:
            self.canv.setDash()  # solid
        y = self.m_bottom + self.stroke_width / 2.0
        self.canv.line(0, y, self._avail_width, y)


def create_styles(doc):
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    theme = doc.theme
    base_font = theme.typography["font"]
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName=base_font,
            fontSize=theme.typography["size_base"],
            leading=theme.typography["size_base"] + 2,
            textColor=theme.colors["foreground"],
        )
    )
    styles.add(
        ParagraphStyle(
            name="Muted",
            parent=styles["Body"],
            textColor=theme.colors["muted"],
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1",
            parent=styles["Body"],
            fontSize=theme.typography["h1"],
            leading=theme.typography["h1"] + 2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2",
            parent=styles["Body"],
            fontSize=theme.typography["h2"],
            leading=theme.typography["h2"] + 2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H3",
            parent=styles["Body"],
            fontSize=theme.typography["h3"],
            leading=theme.typography["h3"] + 2,
        )
    )
    styles.add(ParagraphStyle(name="Button", parent=styles["Body"], alignment=1))
    return styles
