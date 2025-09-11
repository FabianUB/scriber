# Theme Tokens

Scriber mirrors shadcn-like tokens for a consistent look.

- Spacing: `xs, sm, md, lg, xl, 2xl`
- Radii: `sm, md, lg`
- Colors: `foreground, muted, surface, border, primary, success, warning, danger, card`
- Typography: `font`, `size_sm`, `size_base`, `size_lg`, `h1`, `h2`, `h3`

## Selecting a Theme

You can pick a preset by name or pass a custom Theme:

```
from scriber import pdf

# Use the shadcn-inspired preset (default)
with pdf.document("out.pdf", theme="shadcn"):
    ...

# Other presets: "classic"
with pdf.document("out-classic.pdf", theme="classic"):
    ...
```

Implementations live in `scriber/theme/tokens.py`: `shadcn_theme()`, `classic_theme()`. Customize by creating a `Theme` and passing it as `theme=Theme(...)`.
