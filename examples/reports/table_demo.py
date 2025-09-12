from scriber import pdf, ui
from scriber.document import page


def build_table_demo():
    # Prefer pandas if available; otherwise, fall back to list of dicts
    try:
        import pandas as pd
        df = pd.DataFrame(
            {
                "Product": ["A", "B", "C", "D"],
                "Qty": [10, 5, 12, 7],
                "Price": [3.5, 9.0, 1.25, 5.0],
            }
        )
        data = df
    except Exception:
        data = [
            {"Product": "A", "Qty": 10, "Price": 3.5},
            {"Product": "B", "Qty": 5, "Price": 9.0},
            {"Product": "C", "Qty": 12, "Price": 1.25},
            {"Product": "D", "Qty": 7, "Price": 5.0},
        ]

    with pdf.document("examples/reports/output_table_demo.pdf", theme="shadcn"):
        with page():
            ui.h2("Table Demo")
            ui.text("Simple order summary table.")
            ui.spacer("sm")
            ui.table(
                data,
                zebra=True,
                compact=True,
                formats={"Price": "currency"},
                header_align=["left", "center", "right"],
            )


if __name__ == "__main__":
    build_table_demo()
