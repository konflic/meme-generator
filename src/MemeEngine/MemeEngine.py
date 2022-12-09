import math
import os
import pathlib

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

BORDERS_RATE = 0.02
PORTION_OF_HEIGHT = 12
PORTION_STEP = 0.5
MAX_SIZE = 640


class MemeEngine:
    def __init__(self, folder):
        self.folder = pathlib.Path(folder).resolve()
        self.font = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../stuff/arial.ttf"
        )
        self.image_height = None

    def __set_image_height(self, image_height):
        if self.image_height is None:
            self.image_height = int(image_height)

    def downsize_image(self, img: Image):
        width, height = img.size
        base = MAX_SIZE

        if width <= MAX_SIZE and height <= MAX_SIZE:
            return img

        if width <= height:
            wpercent = base / float(height)
            wsize = int((float(width) * float(wpercent)))
            img = img.resize((wsize, base), Image.Resampling.LANCZOS)
        else:
            wpercent = base / float(width)
            hsize = int((float(height) * float(wpercent)))
            img = img.resize((base, hsize), Image.Resampling.LANCZOS)

        return img

    def body_font(self, image_height: int = None) -> FreeTypeFont:

        if image_height is None:
            if self.image_height is None:
                raise Exception("Image height must be set within class!")
            image_height = self.image_height

        font_size = int(image_height / self.proportion)

        return ImageFont.truetype(self.font, size=font_size)

    def draw_demotivator_line(
            self, image: Image, initial_image: Image, text: str, position: str
    ):
        text = text.strip().upper()
        draw = ImageDraw.Draw(image)

        IMAGE_WIDTH, IMAGE_HEIGHT = image.size
        IMAGE_WIDTH -= int(IMAGE_WIDTH * 0.03)

        self.proportion = PORTION_OF_HEIGHT
        self.__set_image_height(IMAGE_HEIGHT)

        _, _, full_text_w, full_text_h = draw.multiline_textbbox(
            (IMAGE_WIDTH * BORDERS_RATE, IMAGE_HEIGHT * BORDERS_RATE),
            text,
            font=self.body_font(),
        )

        # Итеративное уменьшение размера текста
        while full_text_w > IMAGE_WIDTH:
            self.proportion += 0.2
            _, _, full_text_w, full_text_h = draw.multiline_textbbox(
                (0, 0), text, font=self.body_font()
            )

        image_w, image_h = initial_image.size

        x = int((IMAGE_WIDTH - full_text_w) / 2) + IMAGE_WIDTH * BORDERS_RATE
        y = int(image_h + image_h * 0.15)

        if position == "bottom":
            y = int(image_h + image_h * 0.27)
            x = int((IMAGE_WIDTH - full_text_w / 2) / 3) + IMAGE_WIDTH * BORDERS_RATE

        draw.multiline_text(
            (x, y),
            text,
            font=self.body_font(
                IMAGE_HEIGHT if position != "bottom" else IMAGE_HEIGHT / 1.5
            ),
            align="center",
        )

    def draw_mem_line(self, image: Image, text: str, position: str):
        text = text.strip().upper()
        draw = ImageDraw.Draw(image)

        IMAGE_WIDTH, IMAGE_HEIGHT = image.size

        BORDER = int(((IMAGE_WIDTH + IMAGE_HEIGHT) / 2) * BORDERS_RATE)

        IMAGE_WIDTH, IMAGE_HEIGHT = (
            IMAGE_WIDTH - IMAGE_WIDTH * BORDERS_RATE,
            IMAGE_HEIGHT - IMAGE_HEIGHT * BORDERS_RATE,
        )

        self.__set_image_height(IMAGE_HEIGHT)
        STROKE_WIDTH = 2 + int(IMAGE_HEIGHT / 500)

        _, _, full_text_w, full_text_h = draw.multiline_textbbox(
            (IMAGE_WIDTH * BORDERS_RATE, IMAGE_HEIGHT * BORDERS_RATE),
            text,
            font=self.body_font(IMAGE_HEIGHT),
        )

        if full_text_w > IMAGE_WIDTH:

            # Если изображение больше чем в 1.5 раза, то делим на 2
            if full_text_w / IMAGE_WIDTH > 1.4:
                words = text.split()
                half = math.floor(len(words) / 2)
                first_part = " ".join(words[:half])
                second_part = " ".join(words[half:])

                if len(first_part) < len(second_part):
                    half += 1

                wrapped_lines = [" ".join(words[:half]), " ".join(words[half:])]

                self.proportion += 1

                text = "\n".join(wrapped_lines)
                _, _, full_text_w, full_text_h = draw.multiline_textbbox(
                    (0, 0),
                    text,
                    font=self.body_font(),
                )

        # Итеративное уменьшение размера текста
        while full_text_w > IMAGE_WIDTH:
            self.proportion += 0.5
            _, _, full_text_w, full_text_h = draw.multiline_textbbox(
                (0, 0), text, font=self.body_font()
            )

        x = ((IMAGE_WIDTH - full_text_w) / 2) + BORDER / 2
        y = BORDER

        if position == "bottom":
            y = IMAGE_HEIGHT - (full_text_h - BORDER)

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
        image = self.downsize_image(image)

        self.draw_mem_line(image=image, text=quote_first_line, position="top")
        self.draw_mem_line(image=image, text=quote_second_line, position="bottom")

        os.makedirs(self.folder, exist_ok=True)
        meme_path = f"{self.folder}{os.sep}{meme_filename}.png"
        image.save(meme_path)

        return meme_path

    def make_demotivator(self, img, quote_first_line, quote_second_line):
        demotivator_filename = os.path.basename(img).split(".")[0]
        image = Image.open(pathlib.Path(img).resolve())

        width, height = image.size

        if width > height:
            image = image.crop((width - height, 0, width, height))
        elif height > width:
            image = image.crop((0, int((height - width) / 2), width, int((height + width) / 2)))

        width, height = image.size

        white_back = Image.new("RGB", (int(width + width * 0.03), int(height + height * 0.03)), color="white")
        d_width, d_height = int(width + (width * 0.2)), int(height + (height * 0.4))
        d_image = Image.new("RGB", (d_width, d_height), color="black")

        os.makedirs(self.folder, exist_ok=True)
        d_path = f"{self.folder}{os.sep}{demotivator_filename}.png"

        d_image.paste(white_back, (int(width * (0.1 - 0.015)), int(height * (0.1 - 0.015))))
        d_image.paste(image, (int(width * 0.1), int(height * 0.1)))

        self.draw_demotivator_line(
            d_image, image, quote_first_line, position="top"
        )
        self.draw_demotivator_line(
            d_image, image, quote_second_line, position="bottom"
        )

        d_image = self.downsize_image(d_image)
        d_image.save(d_path)

        return d_path


if __name__ == "__main__":
    VERY_LONG_LINE = "nfr b vtn ybrjulf brbrkdfjdfjgd dfdfds"

    LONG_LINE = "This very very very long long long"
    SHORT = "но потом всё"

    # MemeEngine("./tmp").make_meme("../stuff/26am_1.jpg", VERY_LONG_LINE, SHORT)
    # MemeEngine("./tmp").make_meme("../stuff/26am_2.jpg", SHORT, VERY_LONG_LINE)
    # MemeEngine("./tmp").make_meme("../stuff/vertical.jpg", VERY_LONG_LINE, VERY_LONG_LINE)

    # MemeEngine("./tmp").make_demotivator("../stuff/26am_1.jpg", SHORT, SHORT)
    MemeEngine("./tmp").make_demotivator("../stuff/horizontal.png", SHORT, LONG_LINE)
    MemeEngine("./tmp").make_demotivator("../stuff/vertical.jpg", SHORT, LONG_LINE)
