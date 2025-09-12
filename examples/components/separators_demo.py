from scriber import pdf, ui
from scriber.document import page


def build_demo():
    with pdf.document("examples/components/output_separators_demo.pdf", theme="shadcn"):
        with page():
            ui.h2("Separators Demo")
            ui.text("Default separator")
            ui.separator()

            ui.text("Thicker + dashed + margin")
            ui.separator(thickness=2, style="dashed", margin=6)

            ui.text("Colored separator (primary)")
            ui.separator(color="primary")

            ui.text("Labeled separator")
            ui.labeled_separator("Section Title")

            ui.text("Labeled separator, dotted, gap=12, color=muted")
            ui.labeled_separator("Details", style="dotted", gap=12, color="#6b7280")


if __name__ == "__main__":
    build_demo()

