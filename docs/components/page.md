# Page

Container representing a page section. Currently treated as a vertical column.

API
- `from scriber.document import page`
- `with page(**props): ...`

Example
```
from scriber.document import page

with page():
    ...
```

Notes
- Exposed under `scriber.document.page`. A `ui.page` alias may be added later for ergonomics.
- Useful for structuring content; multiple `page()` blocks flow sequentially.

