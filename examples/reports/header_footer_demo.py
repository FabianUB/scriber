from scriber import pdf, ui
from scriber.document import page
import datetime as dt


def build_demo():
    today = dt.date.today().strftime("%Y-%m-%d")

    def header(canv, rl_doc, doc):
        canv.saveState()
        canv.setFont(doc.theme.typography["font"], 10)
        canv.setFillColor(doc.theme.colors["muted"])
        y = rl_doc.height + rl_doc.topMargin + 10
        canv.drawString(rl_doc.leftMargin, y, f"Acme Corp — Quarterly Report ({today})")
        canv.restoreState()

    with pdf.document(
        "examples/reports/output_header_footer_demo.pdf",
        theme="shadcn",
        header=header,
        footer="Confidential — Internal Use Only",
        page_numbers="xofy",
    ):
        with page():
            ui.h2("Header / Footer Demo")
            ui.text("Demonstrates a document header, footer, and page numbering.")
            ui.spacer("md")
            with ui.card():
                for i in range(40):
                    ui.text(f"Paragraph {i+1}: Lorem ipsum dolor sit amet, consectetur adipiscing elit.")


if __name__ == "__main__":
    build_demo()

