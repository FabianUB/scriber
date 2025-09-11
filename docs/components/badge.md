# Badge

Inline label for status or metadata.

Props
- `variant: default|primary|success|warning|danger|outline|secondary` (default: `default`)
- `size: sm|md|lg|number` (default: `md`)

Example
```
from scriber import ui

ui.badge("PAID", variant="success")
```

Notes
- `default` uses a surface background; `primary/success/warning/danger` are solid; `outline/secondary` are subtle with borders.
- Size accepts tokens or numeric points. Numeric values are mapped to the nearest of `sm|md|lg` using theme spacing thresholds for consistent sizing across components.
