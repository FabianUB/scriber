# Scriber

Shadcn-inspired, Streamlit-like PDF builder for Python. Build reports and invoices using a simple, declarative container API and render to PDF.

## Quick Start

- Requirements: Python 3.10+
- Dependencies managed with `uv`.

### Setup

1) Install uv (see https://docs.astral.sh/uv/):

   - macOS (Homebrew): `brew install uv`
   - or follow upstream installation instructions

2) Sync dependencies:

```
uv sync
```

3) Run examples:

```
uv run python examples/invoices/invoice_shadcn.py
uv run python examples/charts/matplotlib.py
uv run python examples/reports/kpi_report_shadcn.py
```

Outputs are written next to each example (e.g., `examples/invoices/output_*.pdf`).

## Development Workflow

- Add dependencies: `uv add <package>`
- Remove dependencies: `uv remove <package>`
- Run a script: `uv run python <path>`
- (Optional) Create a virtualenv: `uv venv` (uv can manage one automatically)

## Documentation

- Docs live in `docs/` as Markdown.
- Component docs under `docs/components/` mirror the implemented API and props.
- Keep docs updated with each change; include examples that run against the current code.
- Consider adding a docs site generator (e.g., MkDocs) later; for now, Markdown is the source of truth.

## Roadmap / TODOs

- See `TODO.md` for a prioritized roadmap. Top priority is chart embedding across Matplotlib/Seaborn/Plotnine/Plotly/Altair with a unified `ui.figure(...)` API and ReportLab image/SVG embedding.

### Commit Etiquette

- Commit after each meaningful change with a descriptive message that explains the error fixed or feature added.
- Prefer small, focused commits; reference any error messages in the body when fixing bugs.
- Keep AGENTS.md updated with notable changes that affect usage or contributor workflow.

## Project Structure

```
scriber/
  __init__.py
  pdf.py          # document context manager
  ui.py           # Streamlit-like API wrappers
  document.py     # context stack and lifecycle
  core/nodes.py   # node definitions
  renderers/
    reportlab.py  # ReportLab-based renderer
  theme/tokens.py # shadcn-inspired tokens
examples/
  invoices/
    invoice.py
  charts/
    matplotlib.py
    seaborn.py
    plotnine.py
    plotly.py
    altair.py
  reports/
    kpi_report_shadcn.py
pyproject.toml
AGENTS.md
.gitignore
```

### Examples Organization

- Invoices under `examples/invoices/` with multiple theme variants.
- Charts under `examples/charts/` covering Matplotlib, Seaborn, Plotnine, Plotly, and Altair.
- Reports under `examples/reports/` (e.g., `kpi_report_shadcn.py`).

## Design Notes

- Components are shadcn-inspired, not actual React components. We mirror design tokens (spacing, radii, colors, typography) and ergonomics in Python.
- Renderer is initially ReportLab (pure Python, pagination-capable). HTML→PDF can be added later if needed.

## Architecture (Components Split)

- UI Components (`scriber/components/*`): user-facing DSL helpers that create Nodes and manage composition (e.g., `separator`, `labeled_separator`).
- Renderer Handlers (`scriber/renderers/reportlab/handlers/*`): per-node rendering to ReportLab flowables (layout, styling, pagination decisions).
- Core (`scriber/core/*`): Node definitions and shared data structures (stable contracts across renderers).
- Base Renderer Utilities (`scriber/renderers/reportlab/base.py`): shared helpers (styles, color/size resolution, common flowables like HR).
- Facade (`scriber/ui.py`): re-exports component helpers to keep the public API stable.

Contributor workflow:
- Add/modify what authors write → `scriber/components/*` (builders).
- Add/modify how it renders → `scriber/renderers/reportlab/handlers/*` (handlers) and register in the central dispatch (TBD as we migrate).

### Adding a New Component
- Define a Node (only if needed) in `scriber/core/nodes.py`.
- Add a builder in `scriber/components/<name>.py` creating that Node (normalize props, tokens→points, context managers if needed).
- Implement a handler in `scriber/renderers/reportlab/handlers/<name>.py` with signature `(doc, node, styles) -> list[Flowable]`.
- Register the handler in `scriber/renderers/reportlab/dispatch.py` mapping `node.type` → function.
- Update docs in `docs/components/<name>.md` and add a small example under `examples/components/`.

### Style/Helper Changes
- Shared color/number/percent/figure utils live in `scriber/renderers/reportlab/base.py`.
- Styles are created in the renderer; we may extract these into base in the future for easier testing.

## Git

Initialize and commit the scaffold:

```
git init
git add -A
git commit -m "chore: scaffold scriber with uv and MVP"
```

Standard development flow applies (feature branches, PRs, etc.).

## Changelog (notable dev-facing changes)

- fix(document): use `default_factory` for `Theme` to avoid dataclass mutable default error (`ValueError: mutable default Theme ... use default_factory`).
- fix(renderer): remove `ListFlowable` (prevent numbered items) and rework Card/Row layouts to avoid unsplittable `KeepTogether` cells causing `LayoutError` (oversized table cells). Cards now render as a one-column table with child-per-row; Rows stack multi-flowable children via an inner one-column table. Horizontal gaps are separate spacer columns.
 - fix(table): wire `TableNode` into renderer dispatch so `ui.table(...)` appears in PDFs.

### Documentation Added
- Initial docs structure in `docs/` with component pages and getting started guide.

## API Guidelines (Standardization)

- Size props: accept both named tokens and numeric points.
  - Tokens: spacing `xs|sm|md|lg|xl|2xl`, control sizes `sm|md|lg`.
  - Numeric: treated as points; very small spacer heights are clamped to >= 0.5pt for visibility.
- Layout gaps/padding: use a consistent prop name `gap` for spacing between children; `padding` for inner padding.
- Width distribution: rows use `equal=True` for equal/weighted columns; children can set `grow` (default 1).
- Alignment naming:
  - `align` for body cells (tables), `header_align` for table header cells.
  - Row `justify`: `start|center|end`.
- Separator props: `thickness`, `color`, `style`, `margin`, `margin_top`, `margin_bottom`.
  - Labeled separator mirrors the same names and adds `gap` (between label and lines) and `muted` for label style.
- Variants: components use `variant` for stylistic variants (e.g., buttons/cards).
- Theme tokens: where `color` accepts strings, allow theme color keys or CSS-like hex (e.g., `"#2563eb"`).
