# Row

Horizontal layout for children.

Props
- `gap: int` — horizontal gap in points (default: theme `md`).
- `justify: start|center|end` — horizontal alignment (default: `start`).
- `equal: bool` — if `True`, columns share available width equally (or by weights) (default: `False`).

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
- When `equal=True`, each child cell expands to share the row width. You can give a child more space via `grow` on the child container, e.g. `ui.card(grow=2)` vs `ui.card(grow=1)`.

Example with equal widths and weights
```
from scriber import ui

with ui.row(equal=True, gap=12):
    with ui.card(grow=2):
        ui.text("Wider card")
    with ui.card(grow=1):
        ui.text("Narrower card")
```
