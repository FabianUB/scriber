# Card

Surface with background, border, and padding around children.

Props
- `padding: int` — inner padding in points (default: theme `lg`).
- `variant: default|outline|subtle` (default: `default`)

Example
```
from scriber import ui

with ui.card(padding=16):
    ui.h3("Summary")
    ui.text("Line item 1 ... $100")
    ui.separator()
    ui.text("Total: $100")
```

Notes
- Cards split naturally across pages; padding applies to outer edges.
- `default` is a white card with border; `outline` border-only; `subtle` uses the surface color.
