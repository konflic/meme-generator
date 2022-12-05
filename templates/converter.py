import os

from PIL import Image

files = os.listdir("raw")
base = 512

for file in files:

    img = Image.open(f'raw/{file}')
    width, height = img.size

    if width < height:
        wpercent = (base / float(height))
        wsize = int((float(width) * float(wpercent)))

        img = img.resize((wsize, base), Image.Resampling.LANCZOS)
        img.save(f'output/{file.split(".")[0]}.png')
    else:
        wpercent = (base / float(height))
        hsize = int((float(height) * float(wpercent)))

        img = img.resize((base, hsize), Image.Resampling.LANCZOS)
        img.save(f'output/{file.split(".")[0]}.png')
