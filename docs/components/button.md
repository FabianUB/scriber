# Button

Clickable-looking element for emphasis; in PDFs it renders as styled text block.

Props
- `variant: primary|outline` (default: `primary`)

Example
```
from scriber import ui

ui.button("Download")
ui.button("Share", variant="outline")
```

Notes
- Future: link targets can be added for clickable areas.

