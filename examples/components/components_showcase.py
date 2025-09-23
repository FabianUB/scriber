from scriber import pdf, ui
from scriber.document import page


def build_showcase():
    header_text = "Scriber Components Showcase"
    footer_text = "Scriber Components Showcase — Footer"

    with pdf.document(
        "examples/components/output_components_showcase.pdf",
        header=header_text,
        header_align="right",
        footer=footer_text,
        page_numbers="xofy",
    ):
        with page():
            ui.h2("Components Showcase")
            ui.text("A quick tour of commonly used components.")

            ui.labeled_separator("Layout")
            with ui.row(equal=True, gap=12):
                with ui.card(grow=2):
                    ui.h3("Column A")
                    ui.text("Wider card with some content.")
                    ui.separator(style="dotted", margin=4)
                    ui.text("Muted note.", muted=True)
                with ui.card(grow=1):
                    ui.h3("Column B")
                    ui.text("Narrower card.")

            ui.spacer("lg")
            ui.labeled_separator("Buttons & Badges")
            with ui.row(gap=8):
                ui.button("Primary")
                ui.button("Outline", variant="outline")
                ui.badge("INFO", variant="secondary")
                ui.badge("OK", variant="success")
                ui.badge("WARN", variant="warning")
                ui.badge("ERR", variant="danger")

            ui.spacer("lg")
            ui.labeled_separator("Table")
            data = [
                {"Product": "A", "Qty": 10, "Price": 3.5},
                {"Product": "B", "Qty": 5, "Price": 9.0},
                {"Product": "C", "Qty": 12, "Price": 1.25},
            ]
            ui.table(data, zebra=True, compact=True, formats={"Price": "currency"}, header_align=["left", "center", "right"])

            # Optional chart if matplotlib is present
            try:
                import matplotlib.pyplot as plt

                fig, ax = plt.subplots(figsize=(3.2, 2.0), dpi=144)
                ax.plot([0, 1, 2, 3], [0, 1, 0, 1])
                ax.set_title("Demo Plot")
                ui.spacer("lg")
                ui.labeled_separator("Figure")
                ui.figure(fig, caption="Matplotlib line chart", align="center")
            except Exception:
                pass


if __name__ == "__main__":
    build_showcase()
