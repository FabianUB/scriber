# Button

Clickable-looking element for emphasis; in PDFs it renders as styled text block.

Props
- `variant: primary|outline|secondary|ghost|danger` (default: `primary`)
- `size: sm|md|lg` (default: `md`)

Example
```
from scriber import ui

ui.button("Download")
ui.button("Share", variant="outline")
```

Notes
- Variants follow shadcn-inspired styles; `secondary` uses a subtle surface, `ghost` is text-only, `danger` is red.
- Size affects padding and font size based on theme control tokens.
- Future: link targets can be added for clickable areas.
