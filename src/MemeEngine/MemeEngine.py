import os
import pathlib
import textwrap

from PIL import Image, ImageDraw, ImageFont

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../stuff/arial.ttf")

BORDERS_RATE = 0.02
PORTION_OF_HEIGHT = 12
PORTION_STEP = 0.5


class MemeEngine:
    def __init__(self, folder):
        self.folder = pathlib.Path(folder).resolve()
        self.font = FONT

    def draw_line(self, image: Image, text: str, position: str):
        text.lower()
        draw = ImageDraw.Draw(image)
        IMAGE_WIDTH, IMAGE_HEIGHT = image.size
        BORDER = int((IMAGE_WIDTH + IMAGE_HEIGHT) / 2 * BORDERS_RATE)
        IMAGE_WIDTH, IMAGE_HEIGHT = (
            IMAGE_WIDTH - IMAGE_WIDTH * BORDERS_RATE,
            IMAGE_HEIGHT - IMAGE_HEIGHT * BORDERS_RATE,
        )
        proportion = PORTION_OF_HEIGHT
        STROKE = 2 + int(IMAGE_HEIGHT / 400)
        FONT_SIZE = int(IMAGE_HEIGHT / proportion)

        body_font = ImageFont.truetype(self.font, size=FONT_SIZE)
        _, _, full_text_w, full_text_h = draw.multiline_textbbox(
            (IMAGE_WIDTH * BORDERS_RATE, IMAGE_HEIGHT * BORDERS_RATE),
            text,
            font=body_font,
        )

        if full_text_w > IMAGE_WIDTH:
            chars = len(text)
            len_per_char = int(full_text_w / chars) + 1
            chars_per_line = int(IMAGE_WIDTH / len_per_char)
            text = "\n".join(textwrap.wrap(text, width=chars_per_line))
            _, _, full_text_w, full_text_h = draw.multiline_textbbox(
                (IMAGE_WIDTH * BORDERS_RATE, IMAGE_HEIGHT * BORDERS_RATE),
                text,
                font=body_font,
            )

        while full_text_w > IMAGE_WIDTH:
            proportion += 0.3
            FONT_SIZE = int(IMAGE_HEIGHT / proportion)
            body_font = ImageFont.truetype(self.font, size=FONT_SIZE)
            _, _, full_text_w, full_text_h = draw.multiline_textbbox(
                (0, 0), text, font=body_font
            )

        x = ((IMAGE_WIDTH - full_text_w) / 2) + BORDER / 2
        y = BORDER

        if position == "bottom":
            y = (IMAGE_HEIGHT - full_text_h) - BORDER / 2

        draw.multiline_text(
            (x, y),
            text,
            font=body_font,
            align="center",
            stroke_width=STROKE,
            stroke_fill="black",
        )

        # _, _, text_w, text_h = draw.textbbox((0, 0), text, font=body_font)
        # BORDERS = IMAGE_WIDTH * BORDERS_RATE
        #
        # if text_w + BORDERS > IMAGE_WIDTH:
        #
        #     difference = text_w + BORDERS - IMAGE_WIDTH
        #     half_pic_width = int(IMAGE_WIDTH * 0.5)
        #
        #     if difference > half_pic_width:
        #
        #         words = text.split(" ")
        #         line = ""
        #         final_lines = []
        #
        #         for word in words:
        #             line += word + " "
        #             _, _, text_w, text_h = draw.multiline_textbbox(
        #                 (0, 0), line, font=body_font
        #             )
        #
        #             if text_w + BORDERS > IMAGE_WIDTH:
        #                 proportion += PORTION_STEP
        #                 body_font = ImageFont.truetype(
        #                     self.font, size=int(IMAGE_HEIGHT / proportion)
        #                 )
        #                 line = line.strip() + "\n"
        #                 final_lines.append(line)
        #                 line = ""
        #
        #         final_lines.append(line)
        #         text = "".join(final_lines).strip()
        #         _, _, text_w, text_h = draw.multiline_textbbox(
        #             (0, 0), text, font=body_font
        #         )
        #
        #     else:
        #         while IMAGE_WIDTH < text_w + BORDERS:
        #             proportion += PORTION_STEP
        #             body_font = ImageFont.truetype(
        #                 self.font, size=int(IMAGE_HEIGHT / proportion)
        #             )
        #             _, _, text_w, text_h = draw.textbbox((0, 0), text, font=body_font)

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
        "This very very very long long long line of test that wont ever fit in"
    )

    LONG_LINE = "This very very very long long long"
    SHORT = "This very very short"

    m = MemeEngine("./tmp")
    m.make_meme("../stuff/26am_1.jpg", VERY_LONG_LINE, LONG_LINE)
    m.make_meme("../stuff/26am_2.jpg", VERY_LONG_LINE, SHORT)
    m.make_meme("../stuff/vertical.png", VERY_LONG_LINE, SHORT)
