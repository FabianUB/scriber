# Labeled Separator

A separator with a centered label and rules on both sides.

API
- `ui.labeled_separator(text, thickness=1, color='border'|'#hex', style='solid'|'dashed'|'dotted', gap=None, margin=0, margin_top=0, margin_bottom=0, muted=True)`

Parameters
- `text`: label string rendered between the rules.
- `thickness`: line weight in points.
- `color`: theme color token (e.g., `primary`, `border`) or hex `#rrggbb`.
- `style`: `solid` | `dashed` | `dotted`.
- `gap`: horizontal space between label and rules (defaults to theme `sm`).
- `margin`, `margin_top`, `margin_bottom`: vertical spacing above/below the whole separator.
- `muted`: render label with muted text style (default: True).

Notes
- Shares the same parameter names and behavior as `ui.separator` for consistency.
- Rules automatically expand to fill the row width around the label.

Examples
```
from scriber import pdf, ui
from scriber.document import page

with pdf.document("out_labeled_sep.pdf", theme="shadcn"):
    with page():
        ui.labeled_separator("Section Title")
        ui.labeled_separator("Details", style="dotted", thickness=1, gap=12)
        ui.labeled_separator("Alerts", style="dashed", color="danger", margin=6)
```
