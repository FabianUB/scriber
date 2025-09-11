# Text and Headings

Render text with variants.

APIs
- `ui.text(content: str, muted: bool = False, **props)`
- `ui.h1(content: str)`
- `ui.h2(content: str)`
- `ui.h3(content: str)`

Example
```
from scriber import ui

ui.h2("Invoice")
ui.text("Thanks for your business.")
ui.text("Muted detail.", muted=True)
```

Notes
- Typography sizes and colors come from theme tokens.

