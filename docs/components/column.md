# Column

Vertical stack of children with optional gaps.

Props
- `gap: int` — vertical gap in points (default: theme `md`).
- `grow: int` — when used inside `ui.row(equal=True)`, determines relative width (default: 1).

Example
```
from scriber import ui

with ui.column(gap=16):
    ui.text("Line A")
    ui.text("Line B")
```

Notes
- Default document root is a Column, so using `ui.column` is optional unless nesting.
 - Inside a row with `equal=True`, set `grow` to control how much horizontal space the column takes relative to siblings.
