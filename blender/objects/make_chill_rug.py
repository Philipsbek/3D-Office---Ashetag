"""
Draws the chill area's big floor rug (original pattern): a soft woolly plum base, a
wide navy border with teal + magenta pin lines, and a faint synthwave-grid + sun
motif woven into the middle. Not glowing: it's fabric.

    python blender/objects/make_chill_rug.py -> blender/objects/textures/chill_rug.png (1000 x 1200)
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "textures", "chill_rug.png")
W, H = 1000, 1200  # matches the rug's 3.0 x 3.6 m


def main():
    rng = random.Random(3)
    img = Image.new("RGB", (W, H), (46, 26, 58))
    d = ImageDraw.Draw(img)

    # wide navy border + pin lines
    b = 90
    d.rectangle([0, 0, W, H], fill=(20, 22, 44))
    d.rounded_rectangle([b, b, W - b, H - b], radius=40, fill=(46, 26, 58))
    for inset, col in ((34, (40, 170, 190)), (52, (190, 60, 160)), (b + 22, (40, 170, 190))):
        d.rounded_rectangle([inset, inset, W - inset, H - inset], radius=40 if inset > b else 28, outline=col, width=5)

    # woven synthwave motif in the middle: a half sun with stripes over a perspective grid
    cx, hz = W // 2, int(H * 0.5)
    r = 210
    d.pieslice([cx - r, hz - r, cx + r, hz + r], 180, 360, fill=(120, 48, 110))
    for k in range(5):
        y = hz - 30 - k * 34
        d.rectangle([cx - r, y, cx + r, y + 10 - k], fill=(46, 26, 58))
    for k in range(9):  # grid: verticals fanning out
        t = (k - 4) / 4
        d.line([(cx + t * 60, hz), (cx + t * 380, H - b - 40)], fill=(40, 120, 150), width=4)
    for k in range(6):  # grid: horizontals getting further apart
        y = hz + 20 + (k / 5) ** 1.6 * (H - b - 60 - hz)
        half = 60 + (y - hz) / (H - b - 40 - hz) * 320
        d.line([(cx - half, y), (cx + half, y)], fill=(40, 120, 150), width=4)
    # small diamond row at the top
    for k in range(7):
        x = cx + (k - 3) * 90
        y = b + 120
        d.polygon([(x, y - 22), (x + 22, y), (x, y + 22), (x - 22, y)], outline=(190, 60, 160), width=4)

    # wool: soft speckle noise + slight blur so it reads as pile, not print
    px = img.load()
    for _ in range(140000):
        x, y = rng.randrange(W), rng.randrange(H)
        c = px[x, y]
        k = rng.uniform(-14, 14)
        px[x, y] = tuple(max(0, min(255, int(v + k))) for v in c)
    img = img.filter(ImageFilter.GaussianBlur(1.1))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("SAVED", OUT)


if __name__ == "__main__":
    main()
