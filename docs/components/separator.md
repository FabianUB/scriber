# Separator

Horizontal rule separating content.

API
- `ui.separator(thickness: number = 1, color: str|token = 'border', style: 'solid'|'dashed'|'dotted' = 'solid', margin: number = 0, margin_top: number = 0, margin_bottom: number = 0)`

Examples
```
from scriber import ui

ui.separator()                              # default thin rule using theme border color
ui.separator(thickness=2)                   # thicker rule
ui.separator(color="#2563eb")              # custom hex color
ui.separator(color="primary")              # theme color token
ui.separator(style="dashed", margin=4)     # dashed rule with vertical margins
ui.separator(style="dotted", thickness=1)  # dotted rule
```
