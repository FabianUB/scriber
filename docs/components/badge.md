# Badge

Inline label for status or metadata.

Props
- `variant: default|primary|success|warning|danger|outline|secondary` (default: `default`)
- `size: sm|md|lg` (default: `md`)

Example
```
from scriber import ui

ui.badge("PAID", variant="success")
```

Notes
- `default` uses a surface background; `primary/success/warning/danger` are solid; `outline/secondary` are subtle with borders.
- Size affects padding via theme control tokens.
