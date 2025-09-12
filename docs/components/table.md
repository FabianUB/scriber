# Table

Display tabular data with optional header, zebra striping, and alignment. Supports pandas and polars DataFrames, as well as lists.

API
- `ui.table(data, columns=None, align=None, col_widths=None, zebra=False, header=True, compact=False, header_align=None, header_bold=True, formats=None, currency_symbol="$")`

Data inputs
- pandas.DataFrame: columns inferred unless `columns` is provided.
- polars.DataFrame: columns inferred unless `columns` is provided.
- List[dict]: columns inferred from first row unless provided.
- List[list|tuple]: if `columns` is provided, treated as body rows; otherwise, no header.

Props
- `columns`: list of column names to select/order.
- `align`: `'left'|'center'|'right'` or list per column.
- `header_align`: `'left'|'center'|'right'` or list per column.
- `header_bold`: render header in bold (default: True).
- `formats`: dict mapping column name or index to format:
  - `'currency'` for currency format using `currency_symbol` with `#,###.##` pattern.
  - Any Python numeric format spec (e.g., `',.1f'`, `'.0f'`).
- `currency_symbol`: symbol when using `'currency'` (default: `$`).
- `col_widths`: list of absolute widths (points) or percentages as strings, e.g. `['30%', '40%', '30%']`.
- `zebra`: alternate row backgrounds.
- `header`: show header row if columns known (default: True).
- `compact`: smaller paddings.

Notes
- Headers repeat across page breaks automatically.
- Numeric columns are right-aligned by default when `align` is not provided (auto-detected).
- For pandas/polars, install as needed: `uv add pandas` or `uv add polars`.

Example (pandas)
```
import pandas as pd
from scriber import pdf, ui
from scriber.document import page

df = pd.DataFrame({"Product": ["A", "B", "C"], "Qty": [10, 5, 12], "Price": [3.5, 9.0, 1.25]})

with pdf.document("out_table.pdf", theme="shadcn"):
    with page():
        ui.h3("Order Summary")
        ui.table(
            df,
            zebra=True,
            compact=True,
            formats={"Price": "currency"},
            header_align=["left", "center", "right"],
        )
```
