from scriber import pdf, ui


def build_invoice():
    with pdf.document("examples/output_invoice.pdf", size="A4", margin=36):
        # Page is optional here, but it helps structure
        from scriber.document import page

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
                ui.badge("PAID", variant="success")

            ui.spacer("lg")

            with ui.card():
                ui.h3("Summary")
                ui.text("Consulting Services (Aug) .................................. $4,000")
                ui.text("Build & Integration ........................................ $2,500")
                ui.separator()
                ui.text("Total: $6,500")

            ui.spacer("lg")

            with ui.row(gap=8, justify="end"):
                ui.button("Download")
                ui.button("Share", variant="outline")


if __name__ == "__main__":
    build_invoice()

