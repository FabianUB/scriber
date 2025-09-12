from scriber import pdf, ui
from scriber.document import page
import random
import datetime as dt


def gen_rows(n, cols):
    rows = []
    for i in range(n):
        row = []
        for c in range(cols):
            kind = c % 6
            if kind == 0:
                row.append(f"Item {i}-{c}")
            elif kind == 1:
                row.append(i * c)
            elif kind == 2:
                row.append((i + 1) * (c + 0.5) / 3.0)
            elif kind == 3:
                row.append(random.choice([None, i * 1000, (i + 0.1234)]))
            elif kind == 4:
                row.append(dt.date(2024, 1, 1) + dt.timedelta(days=i))
            else:
                row.append("Lorem ipsum dolor sit amet, consectetur adipiscing elit."[: random.randint(10, 56)])
        rows.append(row)
    return rows


def to_pandas(columns, rows):
    try:
        import pandas as pd

        return pd.DataFrame(rows, columns=columns)
    except Exception:
        return None


def to_polars(columns, rows):
    try:
        import polars as pl

        return pl.DataFrame({columns[i]: [r[i] for r in rows] for i in range(len(columns))})
    except Exception:
        return None


def build_tables():
    with pdf.document(
        "examples/reports/output_table_stress.pdf",
        theme="shadcn",
        currency="€",
        decimal=",",
        thousands=".",
        decimals=2,
    ):
        with page():
            ui.h2("Table Stress Examples")
            ui.text("Multiple tables with varying columns, data types, widths, and formatting.")

            # 1) Simple list-of-dicts (3 columns)
            data1 = [
                {"Product": "A", "Qty": 10, "Price": 3.5},
                {"Product": "B", "Qty": 5, "Price": 9.0},
                {"Product": "C", "Qty": 12, "Price": 1.25},
            ]
            ui.h3("Simple (list[dict])")
            ui.table(
                data1,
                zebra=True,
                compact=True,
                formats={"Price": "currency"},
                header_align=["left", "center", "right"],
            )

            ui.spacer("md")

            # 2) Wide table (8 columns) with mixed types
            cols2 = [f"Col {i+1}" for i in range(8)]
            rows2 = gen_rows(15, len(cols2))
            df2 = to_pandas(cols2, rows2) or rows2
            ui.h3("Wide (8 columns, mixed types)")
            ui.table(
                df2,
                zebra=True,
                align=None,  # triggers numeric auto-align
                col_widths=["12%", "12%", "12%", "12%", "12%", "16%", "12%", "12%"],
                formats={3: ("percent", 1), 5: ("currency", 0)},
            )

            ui.spacer("md")

            # 3) Narrow table (4 columns) from polars if available
            cols3 = ["Name", "Score", "Change", "Updated"]
            rows3 = [
                ["Alpha", 1234.5, 0.0345, dt.datetime(2024, 2, 5, 10, 30)],
                ["Beta", 12, -0.12, dt.datetime(2024, 2, 6, 18, 5)],
                ["Gamma", None, 0.0, dt.datetime(2024, 2, 7, 9, 15)],
            ]
            df3 = to_polars(cols3, rows3) or rows3
            ui.h3("Polars (if installed) or raw rows")
            ui.table(
                df3,
                columns=cols3,
                zebra=False,
                compact=False,
                formats={"Score": ",.1f", "Change": ("percent", 2)},
                header_align="center",
            )

            ui.spacer("md")

            # 4) Long text columns with fixed point widths
            cols4 = ["ID", "Description", "Amount"]
            rows4 = [[i, " — ".join(["Long text"] * (i % 4 + 1)), 1000 * i + 0.5] for i in range(1, 12)]
            ui.h3("Long text + fixed widths")
            ui.table(
                rows4,
                columns=cols4,
                col_widths=[40, 320, 100],
                zebra=True,
                formats={"Amount": "currency"},
                align=["left", "left", "right"],
                header_align=["left", "left", "right"],
                compact=True,
            )

            ui.spacer("md")

            # 5) Many columns (12+) to test auto widths and wrapping
            cols5 = [f"H{i+1}" for i in range(12)]
            rows5 = gen_rows(8, len(cols5))
            ui.h3("Very wide (12 columns)")
            ui.table(
                rows5,
                columns=cols5,
                zebra=True,
                compact=True,
                header_align="center",
            )


if __name__ == "__main__":
    random.seed(0)
    build_tables()

