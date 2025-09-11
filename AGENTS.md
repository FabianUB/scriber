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

3) Run the example:

```
uv run python examples/invoice.py
```

This will generate `examples/output_invoice.pdf`.

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
  invoice.py
pyproject.toml
AGENTS.md
.gitignore
```

## Design Notes

- Components are shadcn-inspired, not actual React components. We mirror design tokens (spacing, radii, colors, typography) and ergonomics in Python.
- Renderer is initially ReportLab (pure Python, pagination-capable). HTML→PDF can be added later if needed.

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

### Documentation Added
- Initial docs structure in `docs/` with component pages and getting started guide.
