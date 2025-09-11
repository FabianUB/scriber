from scriber import pdf, ui
from scriber.document import page


def build_plotly():
    try:
        import plotly.graph_objects as go
    except Exception as e:
        raise SystemExit("Plotly is required: uv add plotly kaleido") from e

    fig = go.Figure(data=[go.Bar(x=["A", "B", "C"], y=[10, 15, 7])])
    fig.update_layout(title_text="Plotly Bar Chart", width=500, height=300)

    with pdf.document("examples/output_charts_plotly.pdf", size="A4", margin=36, theme="shadcn"):
        with page():
            ui.h2("Charts (Plotly)")
            ui.text("Rendered as SVG when svglib is available; otherwise PNG.")
            ui.spacer("sm")
            ui.figure(fig, caption="Plotly bar chart", align="center")


if __name__ == "__main__":
    build_plotly()

