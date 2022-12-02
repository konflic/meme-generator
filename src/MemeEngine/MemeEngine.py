import os
import pathlib

from PIL import Image, ImageDraw, ImageFont

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../stuff/arial.ttf")

BORDERS = 15
PORTION_OF_HEIGHT = 10
PORTION_STEP = 0.5


class MemeEngine:
    def __init__(self, folder):
        self.folder = pathlib.Path(folder).resolve()
        self.font = FONT

    def prepare_line(self, image: Image, draw: ImageDraw, text):
        IMAGE_WIDTH, IMAGE_HEIGHT = image.size
        proportion = PORTION_OF_HEIGHT
        body_font = ImageFont.truetype(self.font, size=int(IMAGE_HEIGHT / proportion))
        _, _, text_w, text_h = draw.textbbox((0, 0), text, font=body_font)

        if text_w + BORDERS > IMAGE_WIDTH:

            difference = text_w + BORDERS - IMAGE_WIDTH
            half_pic_width = int(IMAGE_WIDTH * 0.5)

            if difference > half_pic_width:

                words = text.split(" ")
                line = ""
                final_lines = []

                for word in words:
                    line += word + " "
                    _, _, text_w, text_h = draw.multiline_textbbox(
                        (0, 0), line, font=body_font
                    )

                    if text_w + BORDERS > IMAGE_WIDTH:
                        proportion += PORTION_STEP
                        body_font = ImageFont.truetype(
                            self.font, size=int(IMAGE_HEIGHT / proportion)
                        )
                        line = line.strip() + "\n"
                        final_lines.append(line)
                        line = ""

                final_lines.append(line)
                text = "".join(final_lines).strip()
                _, _, text_w, text_h = draw.multiline_textbbox(
                    (0, 0), text, font=body_font
                )

            else:
                while IMAGE_WIDTH < text_w + BORDERS:
                    proportion += PORTION_STEP
                    body_font = ImageFont.truetype(
                        self.font, size=int(IMAGE_HEIGHT / proportion)
                    )
                    _, _, text_w, text_h = draw.textbbox((0, 0), text, font=body_font)

        return text, text_w, body_font, proportion

    def make_meme(self, img, quote_first_line, quote_second_line):
        meme_filename = os.path.basename(img).split(".")[0]
        image = Image.open(pathlib.Path(img).resolve())
        draw = ImageDraw.Draw(image)
        IMAGE_WIDTH, IMAGE_HEIGHT = image.size

        text, text_w, body_font, _ = self.prepare_line(
            image=image, draw=draw, text=quote_first_line
        )

        draw.multiline_text(
            ((IMAGE_WIDTH - text_w) / 2, BORDERS),
            text,
            font=body_font,
            align="center",
            stroke_width=3,
            stroke_fill="black"
        )

        text, text_w, body_font, proportion = self.prepare_line(
            image=image, draw=draw, text=quote_second_line
        )

        draw.text(
            ((IMAGE_WIDTH - text_w) / 2, IMAGE_HEIGHT - 20 - IMAGE_HEIGHT / proportion),
            quote_second_line,
            font=body_font,
            stroke_fill="black",
            stroke_width=3,
            align="center",
        )

        os.makedirs(self.folder, exist_ok=True)
        meme_path = f"{self.folder}{os.sep}{meme_filename}.png"
        image.save(meme_path)

        return meme_path


if __name__ == "__main__":
    VERY_LONG_LINE = (
        "This very very very long long long line of test that wont ever fit in"
    )
    LONG_LINE = "This very very very long long long"
    SHORT = "This very very short"

    m = MemeEngine("./tmp")
    m.make_meme("../stuff/26am_1.jpg", VERY_LONG_LINE, LONG_LINE)
    m.make_meme("../stuff/26am_2.jpg", VERY_LONG_LINE, SHORT)
