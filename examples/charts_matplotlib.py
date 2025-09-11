from scriber import pdf, ui
from scriber.document import page


def build_charts():
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        raise SystemExit("Matplotlib is required: uv add matplotlib") from e

    fig, ax = plt.subplots(figsize=(4, 2.5), dpi=144)
    ax.plot([0, 1, 2, 3], [0, 1, 0, 1])
    ax.set_title("Demo Plot")

    with pdf.document("examples/output_charts_matplotlib.pdf", size="A4", margin=36, theme="shadcn"):
        with page():
            ui.h2("Charts (Matplotlib)")
            ui.text("Below is a Matplotlib figure embedded as a PNG.")
            ui.spacer("sm")
            ui.figure(fig, caption="Matplotlib line chart", align="center")


if __name__ == "__main__":
    build_charts()

