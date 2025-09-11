# Scriber TODO / Roadmap (prioritized)

Legend: P0 = highest priority, P1 = next, P2 = later

## P0
- Charts: embed plots (MPL, Seaborn, Plotnine, Plotly, Altair)
  - API: `ui.figure(obj, width=None, height=None, dpi=144, align="start", caption=None)`
    - Accept: `matplotlib.figure.Figure`, Matplotlib Axes, Seaborn (returns MPL), Plotnine (`ggplot`) and render via Matplotlib backend.
    - Accept: Plotly Figure (export via Kaleido), Altair Chart (export via altair_saver+kaleido).
  - Renderer (ReportLab):
    - Raster path: export to PNG bytes; embed via `reportlab.platypus.Image` with width/height fitting and maintain aspect ratio.
    - Vector path (nice-to-have): support SVG export for Plotly/Altair and convert via `svglib` -> Flowable for crisp print.
  - Deps:
    - Base: `matplotlib` (required for MPL/Seaborn/Plotnine).
    - Optional: `kaleido` (Plotly static export) and `altair_saver[selenium,kaleido]` (choose kaleido route) or `vl-convert-python`.
    - Optional: `svglib` for SVG-to-ReportLab.
  - Examples + Docs:
    - Add `examples/charts_*.py` for each backend.
    - Docs page `docs/components/figure.md` with usage patterns and caveats.
  - Testing:
    - Golden PDFs are heavy; prefer structural checks (file size, story build) and manual visual verification initially.

- Table component (data tables)
  - API: `ui.table(data, columns=None, align=None, col_widths=None, zebra=False)`
  - Pagination: row-splitting, header repeat on page-break.

- Headers/Footers & Page Numbers
  - API: `with pdf.document(..., header=fn, footer=fn)` or callbacks per page.

## P1
- Plotly/Altair vector path (SVG) behind optional deps; fallback to PNG.
- Theme: dark preset + high-contrast preset.
- Font management
  - Register custom TTF/OTF, use Inter by default; bold/italic variants.
  - Font fallback for Unicode.
- Links & annotations
  - Clickable buttons/links via `canvas.linkURL` regions.

## P2
- Grid and Stack containers (absolute or z-index overlays).
- Image component with URL/file/bytes support and caching.
- HTML snippet support (WeasyPrint-based renderer as optional backend).
- CLI: `scriber build examples/invoice_shadcn.py -o out.pdf`.
- Layout rules
  - keep-together / keep-with-next for headings + following paragraphs.
- Performance
  - Internal cache for repeated paragraphs, images.

## Notes / Decisions
- Prefer pure-Python and optional extras for heavy deps (kaleido, svglib).
- Start with PNG rasterization for reliability; add SVG path where feasible.
- Maintain a minimal, predictable layout model (no implicit flex-wrap).
