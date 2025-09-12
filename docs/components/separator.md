# Separator

Horizontal rule separating content.

API
- `ui.separator(thickness: number = 1, color: str|token = 'border')`

Examples
```
from scriber import ui

ui.separator()                       # default thin rule using theme border color
ui.separator(thickness=2)            # thicker rule
ui.separator(color="#2563eb")       # custom hex color
ui.separator(color="primary")       # theme color token
```
