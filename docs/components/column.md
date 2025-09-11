# Column

Vertical stack of children with optional gaps.

Props
- `gap: int` — vertical gap in points (default: theme `md`).

Example
```
from scriber import ui

with ui.column(gap=16):
    ui.text("Line A")
    ui.text("Line B")
```

Notes
- Default document root is a Column, so using `ui.column` is optional unless nesting.

