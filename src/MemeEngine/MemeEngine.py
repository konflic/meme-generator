import os
import pathlib

from PIL import Image, ImageDraw, ImageFont

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../stuff/arial.ttf")


class MemeEngine:
    def __init__(self, folder):
        self.folder = pathlib.Path(folder).resolve()

    def make_meme(self, img, quote_first_line, quote_second_line, font=FONT):
        meme_filename = os.path.basename(img).split(".")[0]

        image = Image.open(pathlib.Path(img).resolve())
        image_width, image_height = image.size

        draw = ImageDraw.Draw(image)

        proportion = 10
        body_font = ImageFont.truetype(font, size=int(image_height / proportion))
        _, _, text_w, text_h = draw.textbbox((0, 0), quote_first_line, font=body_font)

        while image_width < text_w + 20:
            proportion += 0.2
            body_font = ImageFont.truetype(font, size=int(image_height / proportion))
            _, _, text_w, text_h = draw.textbbox(
                (0, 0), quote_first_line, font=body_font
            )

        draw.text(
            ((image_width - text_w) / 2, 20),
            quote_first_line,
            font=body_font,
            align="center",
            stroke_width=3,
            stroke_fill="black",
        )

        proportion = 10
        body_font = ImageFont.truetype(font, size=int(image_height / proportion))
        _, _, text_w, text_h = draw.textbbox((0, 0), quote_second_line, font=body_font)

        while image_width < text_w + 20:
            proportion += 0.5
            body_font = ImageFont.truetype(font, size=int(image_height / proportion))
            _, _, text_w, text_h = draw.textbbox(
                (0, 0), quote_second_line, font=body_font
            )

        draw.text(
            ((image_width - text_w) / 2, image_height - 20 - image_height / proportion),
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
    # Quick test
    m = MemeEngine("./tmp")
    path = m.make_meme(
        "../stuff/26am.jpg", "This fdaf df dfdfdfd df fd fdfddddd fd fdfdf df df", "Me"
    )
    print(path)
