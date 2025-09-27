
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

This tool allows you to easily build PDF documents using a component-based architecture, similar to frameworks like <a href="https://streamlit.io" target="_blank">Streamlit</a>.

It uses a simple syntax that let's you iterate through prototypes fast, so you can easily adjust the PDFs to your liking.


## Quickstart

An example of how to create a basic document using Scriber:

```python
from scriber import pdf, ui

with pdf.document("quickstart.pdf") as doc:
  ui.text("Quarterly Overview")
  ui.text("A minimal report built with plain text, labeled separators, and tables")

  ui.labeled_separator("Key Metrics")
  ui.table(
      [
          {"Metric": "Revenue", "Q2 FY24": "$1.8M", "Δ vs Q1": "+5%"},
          {"Metric": "Active Users", "Q2 FY24": "12,430", "Δ vs Q1":"+7%"},
          {"Metric": "Churn", "Q2 FY24": "3.2%", "Δ vs Q1": "-0.4%"},
      ],
      columns=["Metric", "Q2 FY24", "Δ vs Q1"],
      zebra=True,
  )

  ui.labeled_separator("Notes")
  ui.text("• Metrics pulled from the analytics warehouse on 2024-07-05.")
  ui.text("• Refresh the report by rerunning this script after the nextdata sync.")
```

This code will create the following PDF:

<img src="https://i.imgur.com/4ogWOL5.png">

## Installation

-- Working on uploading Scriber to Python Package Index --

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
- figure — Embeds Matplotlib/Plotly/Altair/Plotnine figures with sizing and captions
- image — Embeds local or remote images with fit, alignment, and caching

### Document Structure

- cover — Full-page cover with title, subtitle, and metadata rows
- toc — Generated table of contents with depth and dot leader controls

## Docs

## TO-DO

## Credits

<a href="https://www.reportlab.com" target="_blank">ReportLab</a> - Used for rendering the PDFs.
