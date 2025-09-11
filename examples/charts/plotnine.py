from scriber import pdf, ui
from scriber.document import page


def build_plotnine():
    try:
        from plotnine import ggplot, aes, geom_line, geom_point, theme_minimal
        import pandas as pd
    except Exception as e:
        raise SystemExit("Plotnine is required: uv add plotnine") from e

    df = pd.DataFrame({
        "x": [0, 1, 2, 3, 4, 5],
        "y": [0, 1, 0.5, 1.5, 1.0, 2.0],
    })
    p = ggplot(df, aes("x", "y")) + geom_line() + geom_point() + theme_minimal()

    with pdf.document("examples/charts/output_charts_plotnine.pdf", size="A4", margin=36, theme="shadcn"):
        with page():
            ui.h2("Charts (Plotnine)")
            ui.text("Plotnine renders via Matplotlib; exported as PNG.")
            ui.spacer("sm")
            ui.figure(p, caption="Plotnine line chart", align="center")


if __name__ == "__main__":
    build_plotnine()

