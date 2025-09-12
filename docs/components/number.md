# Number

Render numbers with document-level settings (currency, separators, decimals).

API
- `ui.number(value, kind='decimal', decimals=None, prefix=None, suffix=None)`

Kinds
- `decimal` (default): uses `settings.number_decimals` and locale separators.
- `currency`: uses `settings.currency_symbol` + decimal formatting.
- `percent`: multiplies by 100, appends `%`, uses `settings.percent_decimals`.
- `int`: thousands grouping without decimals.
- `thousands`: like `int` with grouping.

Examples
```
from scriber import pdf, ui
from scriber.document import page

with pdf.document("out_num.pdf", currency="€", decimal=",", thousands="."):
    with page():
        ui.text("Totals:")
        ui.number(1234.567, kind="currency")
        ui.number(0.4567, kind="percent")
        ui.number(123456, kind="thousands")
```

