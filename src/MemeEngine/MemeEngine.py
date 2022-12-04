import os
import pathlib
import textwrap
import math

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

BORDERS_RATE = 0.02
PORTION_OF_HEIGHT = 12
PORTION_STEP = 0.5


class MemeEngine:
    def __init__(self, folder):
        self.folder = pathlib.Path(folder).resolve()
        self.font = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../stuff/arial.ttf")
        self.image_height = None

    def __set_image_height(self, image_height):
        if self.image_height is None:
            self.image_height = int(image_height)

    def body_font(self, image_height: int = None) -> FreeTypeFont:
        if image_height is None:
            if self.image_height is None:
                raise Exception("Image height must be set within class!")
            image_height = self.image_height
        font_size = int(image_height / self.proportion)
        return ImageFont.truetype(self.font, size=font_size)

    def draw_line(self, image: Image, text: str, position: str):
        draw = ImageDraw.Draw(image)
        IMAGE_WIDTH, IMAGE_HEIGHT = image.size
        self.proportion = PORTION_OF_HEIGHT

        BORDER = int(((IMAGE_WIDTH + IMAGE_HEIGHT) / 2) * BORDERS_RATE)

        IMAGE_WIDTH, IMAGE_HEIGHT = (
            IMAGE_WIDTH - IMAGE_WIDTH * BORDERS_RATE,
            IMAGE_HEIGHT - IMAGE_HEIGHT * BORDERS_RATE,
        )

        self.__set_image_height(IMAGE_HEIGHT)
        STROKE_WIDTH = 2 + int(IMAGE_HEIGHT / 400)

        _, _, full_text_w, full_text_h = draw.multiline_textbbox(
            (IMAGE_WIDTH * BORDERS_RATE, IMAGE_HEIGHT * BORDERS_RATE),
            text,
            font=self.body_font(IMAGE_HEIGHT),
        )

        if full_text_w > IMAGE_WIDTH:

            # Если изображение больше чем в 1.5 раза, то делим на 2
            if full_text_w / IMAGE_WIDTH > 1.5:
                total_chars = len(text)
                chars_per_line = math.ceil(total_chars / 2)
                wrapped_lines = textwrap.wrap(text, width=chars_per_line, break_long_words=False)

                self.proportion += len(wrapped_lines)

                text = "\n".join(wrapped_lines)
                _, _, full_text_w, full_text_h = draw.multiline_textbbox(
                    (0, 0),
                    text,
                    font=self.body_font(),
                )

        # Итеративное уменьшение размера текста
        while full_text_w > IMAGE_WIDTH:
            self.proportion += 0.2
            _, _, full_text_w, full_text_h = draw.multiline_textbbox(
                (0, 0), text, font=self.body_font()
            )

        x = ((IMAGE_WIDTH - full_text_w) / 2) + BORDER / 2
        y = BORDER

        if position == "bottom":
            y = (IMAGE_HEIGHT - full_text_h) - BORDER / 2

        draw.multiline_text(
            (x, y),
            text,
            font=self.body_font(),
            align="center",
            stroke_width=STROKE_WIDTH,
            stroke_fill="black",
        )

    def make_meme(self, img, quote_first_line, quote_second_line):
        meme_filename = os.path.basename(img).split(".")[0]
        image = Image.open(pathlib.Path(img).resolve())

        self.draw_line(image=image, text=quote_first_line, position="top")
        self.draw_line(image=image, text=quote_second_line, position="bottom")

        os.makedirs(self.folder, exist_ok=True)
        meme_path = f"{self.folder}{os.sep}{meme_filename}.png"
        image.save(meme_path)

        return meme_path


if __name__ == "__main__":
    VERY_LONG_LINE = (
        "Когда решил круто затусить на чиле под новый год"
    )

    LONG_LINE = "This very very very long long long"
    SHORT = "когда не разобралась"

    m = MemeEngine("./tmp")
    # m.make_meme("../stuff/26am_1.jpg", VERY_LONG_LINE, LONG_LINE)
    # m.make_meme("../stuff/26am_2.jpg", VERY_LONG_LINE, SHORT)
    m.make_meme("../stuff/vertical.jpg", VERY_LONG_LINE, SHORT)
