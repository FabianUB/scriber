# Spacer

Adds vertical space between elements.

API
- `ui.spacer(size: Optional[Union[str, number]] = None)`
  - Accepts theme keys (`xs`, `sm`, `md`, `lg`, `xl`, `2xl`) or numeric points.

Example
```
from scriber import ui

ui.spacer("lg")
```

Notes
- Defaults to theme `md` if omitted.
- Numeric values are treated as points; e.g., `ui.spacer(0.5)` is a very small gap.
- Extremely small values can collapse inside table layouts; values below ~0.5pt are clamped to 0.5pt for reliability.
