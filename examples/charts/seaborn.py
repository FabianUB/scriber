from scriber import pdf, ui
from scriber.document import page


def build_seaborn():
    try:
        import seaborn as sns
        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd
    except Exception as e:
        raise SystemExit("Seaborn and Matplotlib are required: uv add seaborn matplotlib") from e

    # Synthetic dataset
    rng = np.random.default_rng(0)
    x = np.linspace(0, 10, 50)
    y = np.sin(x) + rng.normal(scale=0.2, size=len(x))
    cat = np.where(x < 5, "A", "B")
    df = pd.DataFrame({"x": x, "y": y, "group": cat})

    fig, ax = plt.subplots(figsize=(4.5, 3), dpi=144)
    sns.scatterplot(data=df, x="x", y="y", hue="group", ax=ax)
    sns.lineplot(data=df, x="x", y="y", ax=ax)
    ax.set_title("Seaborn Scatter + Line")

    with pdf.document("examples/charts/output_charts_seaborn.pdf", size="A4", margin=36, theme="shadcn"):
        with page():
            ui.h2("Charts (Seaborn)")
            ui.text("Seaborn plots are Matplotlib figures under the hood.")
            ui.spacer("sm")
            ui.figure(fig, caption="Seaborn scatter+line", align="center")


if __name__ == "__main__":
    build_seaborn()

