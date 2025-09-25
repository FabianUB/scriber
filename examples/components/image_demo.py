from pathlib import Path

from scriber import pdf, ui
from scriber.document import page


def build_image_demo():
    demo_image = Path(__file__).parent / "logo.png"

    with pdf.document("examples/components/output_image_demo.pdf"):
        with page():
            ui.h2("Image Component Demo")
            ui.text("Embed images from file paths or URLs.")

            ui.spacer("md")
            ui.labeled_separator("From file path")
            if demo_image.exists():
                ui.image(demo_image, width=180, caption="Loaded from local file", align="center")
            else:
                ui.text("Place logo.png next to this script", muted=True)

            ui.spacer("lg")
            ui.labeled_separator("From URL")
            ui.image("https://i.imgur.com/1h1J0bS.png", width="xl", caption="Remote image placeholder", align="center")


if __name__ == "__main__":
    build_image_demo()
