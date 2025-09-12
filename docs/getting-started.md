# Getting Started

## Installation

Scriber uses `uv` for dependency management.

1) Install uv (see https://docs.astral.sh/uv/)
2) Sync dependencies:

```
uv sync
```

## Quick Example

```
uv run python examples/invoices/invoice_shadcn.py   # shadcn preset
uv run python examples/invoices/invoice_classic.py  # classic preset
uv run python examples/invoices/invoice_default.py  # default preset
```

Outputs:
- `examples/invoices/output_invoice_shadcn.pdf`
- `examples/invoices/output_invoice_classic.pdf`
- `examples/invoices/output_invoice_default.pdf`

## Charts (P0)

Matplotlib example (install first: `uv add matplotlib`):

```
uv run python examples/charts/matplotlib.py
```

Output: `examples/charts/output_charts_matplotlib.pdf`

Plotly example (install first: `uv add plotly kaleido`):

```
uv run python examples/charts/plotly.py
```

Altair example (install first: `uv add altair vl-convert-python`):

```
uv run python examples/charts/altair.py
```

Tip: Install `svglib` for vector SVG rendering with Plotly/Altair:

```
uv add svglib
```

Seaborn example (install first: `uv add seaborn matplotlib`):

```
uv run python examples/charts/seaborn.py
```

Plotnine example (install first: `uv add plotnine`):

```
uv run python examples/charts/plotnine.py
```

Outputs:
- `examples/charts/output_charts_seaborn.pdf`
- `examples/charts/output_charts_plotnine.pdf`

## Minimal Usage

```
from scriber import pdf, ui
from scriber.document import page

with pdf.document("out.pdf", size="A4", margin=32, currency="€", decimal=",", thousands=".", decimals=2, font="Helvetica"):
    with page():
        with ui.card():
            ui.h2("Hello, Scriber")
            ui.text("Build PDFs with a friendly API.")
            ui.separator()
            with ui.row(justify="end", gap=8):
                ui.button("Primary")
                ui.button("Secondary", variant="outline")
```
