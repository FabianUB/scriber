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
uv run python examples/invoice.py
```

This generates `examples/output_invoice.pdf`.

## Minimal Usage

```
from scriber import pdf, ui
from scriber.document import page

with pdf.document("out.pdf", size="A4", margin=32):
    with page():
        with ui.card():
            ui.h2("Hello, Scriber")
            ui.text("Build PDFs with a friendly API.")
            ui.separator()
            with ui.row(justify="end", gap=8):
                ui.button("Primary")
                ui.button("Secondary", variant="outline")
```

