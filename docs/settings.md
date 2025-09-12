# Document Settings

Define global defaults for each PDF document, such as currency symbol, decimal/thousands separators, and default number of decimals. These settings apply across all pages and components that use numeric formatting, and can still be overridden per component.

Usage
```
from scriber import pdf

with pdf.document(
    "out.pdf",
    theme="shadcn",
    currency="€",         # default currency symbol
    decimal=",",           # decimal separator
    thousands=".",        # thousands separator
    decimals=2,            # default decimals for numbers
    font="Helvetica",     # default document font (theme override)
):
    ...
```

Alternatively, pass a Settings object:
```
from scriber.settings import Settings

with pdf.document("out.pdf", settings=Settings(currency_symbol="€", decimal_separator=",", thousands_separator=".")):
    ...
```

Current consumers
- Table: uses settings for numeric default formatting and `'currency'` shortcut.

Planned consumers
- Number/text helpers, KPI widgets, and chart annotations.

