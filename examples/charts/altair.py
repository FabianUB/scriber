from scriber import pdf, ui
from scriber.document import page


def build_altair():
    try:
        import altair as alt
    except Exception as e:
        raise SystemExit("Altair is required: uv add altair vl-convert-python") from e

    data = [
        {"x": 1, "y": 2},
        {"x": 2, "y": 3},
        {"x": 3, "y": 1},
    ]
    chart = alt.Chart(data).mark_line(point=True).encode(x="x:Q", y="y:Q").properties(width=400, height=250, title="Altair Line Chart")

    with pdf.document("examples/charts/output_charts_altair.pdf", size="A4", margin=36, theme="shadcn"):
        with page():
            ui.h2("Charts (Altair)")
            ui.text("Rendered as SVG when svglib is available; otherwise PNG.")
            ui.spacer("sm")
            ui.figure(chart, caption="Altair line chart", align="center")


if __name__ == "__main__":
    build_altair()

