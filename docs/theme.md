# Theme Tokens (Default Theme)

Scriber ships with a single, well‑tuned default theme. It provides consistent tokens for spacing, radii, colors, and typography — optimized for print‑friendly PDFs.

- Spacing: `xs, sm, md, lg, xl, 2xl`
- Radii: `sm, md, lg`
- Colors: `foreground, muted, surface, border, primary, success, warning, danger, card`
- Typography: `font`, `size_sm`, `size_base`, `size_lg`, `h1`, `h2`, `h3`

Usage
```
from scriber import pdf

# Default theme is applied automatically
with pdf.document("out.pdf"):
    ...

# You can override the default font at the document level
with pdf.document("out-font.pdf", font="Helvetica"):
    ...
```

Customization
- Adjust look via document `font=` override and component‑level props.
- For deeper customization, you can construct a Theme object and pass it:
  - Note: the library currently focuses on a single default theme; external Themes are advanced usage.
