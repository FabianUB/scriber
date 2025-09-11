# Document

Context manager that defines the output PDF file, page size, and margins.

API
- `pdf.document(output_path: str, size: str = "A4", margin: int = 32)`

Example
```
from scriber import pdf

with pdf.document("out.pdf", size="A4", margin=36):
    ...
```

Notes
- Must be the outermost context. All UI must be nested inside.
- Rendering happens on exit of the context.

