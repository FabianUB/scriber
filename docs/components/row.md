# Row

Horizontal layout for children.

Props
- `gap: int` — horizontal gap in points (default: theme `md`).
- `justify: start|center|end` — horizontal alignment (default: `start`).

Example
```
from scriber import ui

with ui.row(gap=12, justify="end"):
    ui.button("OK")
    ui.button("Cancel", variant="outline")
```

Notes
- Children that produce multiple flowables are stacked in a single column within a cell.
- Gap is inserted as a spacer column; it does not affect row height.

