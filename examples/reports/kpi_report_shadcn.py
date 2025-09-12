from scriber import pdf, ui
from scriber.document import page


def kpi_card(label: str, value: str, delta: str = None, variant: str = "default"):
    with ui.card(radius=8):
        ui.text(label, muted=True)
        ui.spacer("s")
        ui.h2(value)
        ui.spacer(1.5)
        if delta:
            ui.badge(delta, variant=variant, size="sm")


def build_report():
    # Optional charts dependency
    try:
        import matplotlib.pyplot as plt
    except Exception:
        plt = None

    with pdf.document("examples/reports/output_kpi_report_shadcn.pdf", size="A4", margin=36, theme="shadcn"):
        with page():
            ui.h2("Acme Corp — Q3 KPI Report")
            ui.text("Confidential — Internal use only", muted=True)

            ui.spacer("lg")

            # KPIs grid
            with ui.row(equal=True, gap=10):
                kpi_card("Revenue", "$1.24M", "+8.2%", variant="success")
                kpi_card("Churn", "2.4%", "-0.3%", variant="success")
                kpi_card("Active Users", "84,120", "+3.1%", variant="success")

            ui.spacer("lg")

            with ui.card(variant="subtle"):
                ui.h3("Highlights")
                ui.text("• New enterprise deals closed in EMEA region.")
                ui.text("• Reduced churn through onboarding improvements.")

            ui.spacer("lg")

            if plt is not None:
                fig, ax = plt.subplots(figsize=(5, 3), dpi=144)
                ax.plot([1, 2, 3, 4], [100, 240, 310, 420])
                ax.set_title("Quarterly Revenue (k)")
                with ui.card():
                    ui.h3("Charts")
                    ui.figure(fig, caption="Revenue trend", align="center")
            else:
                ui.text("Install matplotlib to render charts: uv add matplotlib", muted=True)


if __name__ == "__main__":
    build_report()

