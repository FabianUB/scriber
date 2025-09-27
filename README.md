
<h1 align="center">
  <br>
  <img src="https://i.imgur.com/1h1J0bS.png" width="400"></a>
</h1>

<h4 align="center">An easy to use, component-based PDF creator for Python built on top of <a href="https://www.reportlab.com" target="_blank">ReportLab</a></h4>

<p align="center">
  <a href="https://opensource.org/licenses/BSD-3-Clause">
    <img src="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg"
         alt="BSD License">
  </a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quickstart">Quickstart</a> •
  <a href="#installation">Installation</a> •
  <a href="#docs">Docs</a> •
  <a href="#to-do">TO-DO</a> •
  <a href="#credits">Credits</a> 
</p>

## Features

Scriber allows you to easily build PDF documents using a component-based architecture, similar to frameworks like <a href="https://streamlit.io" target="_blank">Streamlit</a>.

It provides a simple model for creating PDF files while seamlessly integrating data from popular Python libraries such as pandas and matplotlib, enabling direct access to tabular data, visualizations, and analytical outputs without additional conversion steps. This makes it an ideal choice for generating automated reports, business intelligence summaries, or any workflow that requires consistent, data-driven documentation.


## Quickstart

An example of how to create a basic document using Scriber:

```python
from scriber import pdf, ui
with pdf.document("quickstart.pdf") as doc:
  ui.h1("Quarterly Overview")
  ui.h2("A minimal report built with plain text, labeled separators, and tables.")
  ui.spacer("2xl")

  ui.labeled_separator("Key Metrics")
  ui.spacer("md")
  ui.table(
      [
          {"Metric": "Revenue", "Q2 FY24": "$1.8M", "Δ vs Q1": "+5%"},
          {"Metric": "Active Users", "Q2 FY24": "12,430", "Δ vs Q1":"+7%"},
          {"Metric": "Churn", "Q2 FY24": "3.2%", "Δ vs Q1": "-0.4%"},
      ],
      columns=["Metric", "Q2 FY24", "Δ vs Q1"],
      zebra=True,
  )

  ui.spacer("2xl")
  ui.labeled_separator("Notes")
  ui.text("• Metrics pulled from the analytics warehouse on 2024-07-05.")
  ui.text("• Refresh the report by rerunning this script after the next data sync.")
```

This code will create the following PDF:

<img src="https://i.imgur.com/4ogWOL5.png">

## Installation

```shell
pip install scriber-pdf
```

If you want to use an image from an URL in the image component, you will also need <a href="https://pypi.org/project/requests/">requests</a> available in your project.

## Components

### Containers

- row — Horizontal container with configurable gap and justification.
- column — Vertical stack with optional gap and growth hints.
- card — Padded container with optional radius and grow props.

### Typography & Numbers

- text — Body or muted paragraph text with variant overrides.
- h1 — Large heading styled via theme tokens.
- h2 — Medium heading variant.
- h3 — Smaller heading variant.
- number — Formats numeric values (currency, percent, etc.) using document
settings.

### UI Elements

- badge — Pill-style label supporting variants.
- button — Action button with variant-driven styling.

### Layout & Spacing

- separator — Horizontal rule with thickness, color, and margin controls.
- labeled_separator — Separator with centered label and configurable gap/
margins.
- spacer — Vertical whitespace helper using spacing tokens.

### Data & Media

- table — Tabular data renderer with alignment and zebra striping options, supports Pandas and Polars dataframes.
- figure — Embeds Matplotlib/Plotly/Altair/Plotnine figures with sizing and captions.
- image — Embeds local or remote images with fit, alignment, and caching.

### Document Structure

- cover — Full-page cover with title, subtitle, and metadata rows.
- toc — Generated table of contents with depth and dot leader controls.

## Docs

The documentation for Scriber is provided on the <a href="https://github.com/FabianUB/scriber/wiki#scriber-pdf-reference">Wiki<a> section of this repository.

## TO-DO

- [ ] Typography / Fonts
  - Register custom TTF/OTF, bold/italic variants; default to Inter/Source families.
  - Hyphenation/justification improvements; keep-with-next for headings.

- [ ] Table Style Presets + Auto Fit
  - Presets: minimal, classic, condensed.
  - Auto-fit column widths based on content min/max; ellipsis for overflow.

- [ ] Captions + Numbering
  - Auto number for figures/tables; `ui.caption()` with cross-references.

- [ ] Theme: dark preset + high-contrast preset.

- [ ] Links & annotations
  - Clickable buttons/links via `canvas.linkURL` regions.

- [ ] Grid / Multi-column layouts
  - Two/three-column text flows; sidebars; consistent gutters.

- [ ] Callouts / KPI components
  - Info/warning/success boxes with icons, subtle backgrounds, optional titles.

- [ ] Links & Cross-refs
  - Clickable links and internal document anchors.

- [ ] Grid and Stack containers (absolute or z-index overlays).

- [ ] HTML snippet support (WeasyPrint-based renderer as optional backend).

- [ ] CLI: `scriber build examples/invoice_shadcn.py -o out.pdf`.

- [ ] Layout rules
  - keep-together / keep-with-next for headings + following paragraphs.
  - make UI cards easier to use + better auto formatting

- [ ] Outputs
  - Exporting to non-PDF formats (.doc, .docx, .tex...)

- [ ] Performance
  - Internal cache for repeated paragraphs, images.
  
## Credits

<a href="https://www.reportlab.com" target="_blank">ReportLab</a> - Used for rendering the PDFs.
