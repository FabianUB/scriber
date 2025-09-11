from scriber import pdf, ui
from scriber.document import page


def build_invoice():
    with pdf.document("examples/invoices/output_invoice_shadcn.pdf", size="A4", margin=36, theme="shadcn"):
        with page():
            with ui.card():
                ui.h2("Invoice #INV-1001")
                ui.text("Acme Inc.")
                ui.text("123 Business Rd, Gotham")
                ui.separator()
                ui.text("Billed To:")
                ui.text("Wayne Enterprises")
                ui.text("1007 Mountain Dr, Gotham")

            ui.spacer("lg")

            with ui.row(gap=12, justify="end"):
                ui.badge("PAID", variant="success", size="sm")

            ui.spacer("lg")

            with ui.card(variant="subtle"):
                ui.h3("Summary")
                ui.text("Consulting Services (Aug) .................................. $4,000")
                ui.text("Build & Integration ........................................ $2,500")
                ui.separator()
                ui.text("Total: $6,500")

            ui.spacer("lg")

            with ui.row(gap=8, justify="end"):
                ui.button("Download", size="lg")
                ui.button("Share", variant="outline", size="lg")


if __name__ == "__main__":
    build_invoice()

