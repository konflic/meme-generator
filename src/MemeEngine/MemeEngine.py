import hashlib
import time
import os
import pathlib

from PIL import Image, ImageDraw, ImageFont


class MemeEngine:

    def __init__(self, folder):
        self.folder = pathlib.Path(folder).resolve()

    def make_meme(self, img, quote_body, quote_author, body_font="arial.ttf"):
        # Creating unique name for meme
        meme_filename = hashlib.md5(f"{quote_body}{quote_author}{time.time()}".encode()).hexdigest()

        image = Image.open(pathlib.Path(img).resolve())

        image_draw = ImageDraw.Draw(image)
        body_font = ImageFont.truetype(body_font, size=50)
        image_draw.text((100, 100), quote_body, font=body_font)
        image_draw.text((200, 300), quote_author, font=body_font)

        os.makedirs(self.folder, exist_ok=True)

        meme_path = f"{self.folder}{os.sep}{meme_filename}.png"
        image.save(meme_path)

        return meme_path


if __name__ == "__main__":
    image_path = "../_data/photos/dog/xander_1.jpg"
    m = MemeEngine("./tmp")
    path = m.make_meme(image_path, "This is test text", "Me")
    print(path)
