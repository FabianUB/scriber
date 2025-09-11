# Badge

Inline label for status or metadata.

Props
- `variant: default|primary|success|warning|danger` (default: `default`)

Example
```
from scriber import ui

ui.badge("PAID", variant="success")
```

Notes
- `default` uses a surface background; other variants use colored backgrounds with white text.

