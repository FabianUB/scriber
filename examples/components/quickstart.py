from scriber import pdf, ui

with pdf.document("examples/components/quickstart.pdf") as doc:
    ui.h1("Quarterly Overview")
    ui.h2("A minimal report built with plain text, labeled separators, and tables.")
    ui.spacer("2xl")

    ui.labeled_separator("Key Metrics")
    ui.spacer("md")
    ui.table(
        [
            {"Metric": "Revenue", "Q2 FY24": "$1.8M", "Δ vs Q1": "+5%"},
            {"Metric": "Active Users", "Q2 FY24": "12,430", "Δ vs Q1":"+7%"},
            {"Metric": "Churn", "Q2 FY24": "3.2%", "Δ vs Q1": "-0.4%"},
        ],
        columns=["Metric", "Q2 FY24", "Δ vs Q1"],
        zebra=True,
    )

    ui.spacer("2xl")
    ui.labeled_separator("Notes")
    ui.text("• Metrics pulled from the analytics warehouse on 2024-07-05.")
    ui.text("• Refresh the report by rerunning this script after the next data sync.")