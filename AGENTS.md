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

