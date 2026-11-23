"""
Draws the anime-style advert used on the G-building banners: an ORIGINAL
character (not from any existing show) - a girl with a short violet bob, big
magenta eyes and a neon hair clip, on a magenta-to-indigo gradient with
halftone dots, speed lines, a vertical katakana tagline and "NEON NIGHT".

    python blender/objects/make_anime_ad.py   -> blender/objects/textures/anime_ad.png (512 x 1024)

Needs Pillow (system Python); the image is then loaded by glass_city.py.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "textures", "anime_ad.png")
W, H = 512, 1024


def font(size, jp=False):
    for path in (("C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/msgothic.ttc") if jp else ("C:/Windows/Fonts/arialbd.ttf",)):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main():
    rng = random.Random(7)
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # background gradient + halftone + speed lines
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(235 - 150 * t), int(40 + 10 * t), int(170 + 40 * t)))
    for y in range(0, H, 14):
        for x in range(0, W, 14):
            r = 1 + 3 * (1 - y / H) * (x / W)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 120, 220))
    for k in range(40):
        a = rng.uniform(0, 2 * math.pi)
        cx, cy = 256, 420
        r0, r1 = rng.uniform(260, 320), 700
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r1, cy + math.sin(a) * r1)], fill=(255, 210, 250), width=2)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(layer)
    TEAL, TEAL_D, TEAL_L = (120, 80, 230), (70, 40, 160), (200, 175, 255)  # violet hair (names kept)
    SKIN, SKIN_S = (255, 226, 212), (245, 190, 180)
    # back hair: long flowing shape behind head and shoulders
    # short bob: ends at the jaw line
    g.polygon([(128, 300), (112, 480), (118, 640), (170, 690), (200, 600), (312, 600), (342, 690), (394, 640), (400, 480),
               (384, 300), (256, 200)], fill=TEAL_D)
    # shoulders / jacket with neon collar
    g.polygon([(70, 1024), (110, 790), (200, 720), (312, 720), (402, 790), (442, 1024)], fill=(30, 26, 60))
    g.polygon([(200, 720), (256, 820), (312, 720), (290, 710), (256, 780), (222, 710)], fill=(255, 255, 255))
    g.line([(200, 720), (256, 822), (312, 720)], fill=(60, 255, 240), width=6)
    # neck
    g.polygon([(230, 640), (282, 640), (288, 728), (224, 728)], fill=SKIN_S)
    # face: rounded top, pointed anime chin
    g.polygon([(150, 420), (156, 520), (190, 600), (240, 660), (256, 670), (272, 660), (322, 600), (356, 520), (362, 420)], fill=SKIN)
    g.ellipse([150, 250, 362, 520], fill=SKIN)
    # ears hidden by hair; headphones band + cups (neon cyan)
    # a small neon hair clip instead of headphones
    g.polygon([(318, 300), (350, 290), (356, 312), (324, 322)], fill=(60, 255, 240))
    # bangs: spiky fringe over the forehead
    g.polygon([(150, 380), (160, 270), (210, 225), (256, 215), (302, 225), (352, 270), (362, 380), (335, 330), (318, 405), (290, 320),
               (262, 395), (240, 318), (214, 405), (196, 330), (172, 395)], fill=TEAL)
    g.polygon([(214, 240), (256, 222), (300, 238), (262, 262)], fill=TEAL_L)  # hair shine
    # eyes: big anime eyes with magenta irises and two highlights each
    for ex in (208, 304):
        g.ellipse([ex - 38, 430, ex + 38, 520], fill=(255, 255, 255))
        g.ellipse([ex - 30, 436, ex + 30, 520], fill=(190, 30, 150))
        g.ellipse([ex - 22, 456, ex + 22, 516], fill=(255, 90, 200))
        g.ellipse([ex - 12, 470, ex + 12, 500], fill=(40, 0, 50))
        g.ellipse([ex - 20, 448, ex - 4, 468], fill=(255, 255, 255))
        g.ellipse([ex + 8, 492, ex + 16, 500], fill=(255, 255, 255))
        g.arc([ex - 44, 418, ex + 44, 470], 195, 345, fill=(40, 20, 40), width=9)  # upper lashes
        g.line([(ex - 34, 412), (ex + 30, 404)], fill=TEAL_D, width=6)  # brows
    # blush, nose, smile
    for bx in (186, 326):
        g.ellipse([bx - 26, 535, bx + 26, 552], fill=(255, 170, 190))
    g.line([(256, 545), (252, 555)], fill=SKIN_S, width=3)
    g.arc([236, 568, 276, 598], 20, 160, fill=(170, 60, 90), width=4)
    layer = layer.filter(ImageFilter.SMOOTH)
    img.paste(layer, (0, 0), layer)

    d = ImageDraw.Draw(img)
    # vertical katakana tagline (original text: "neon night") + English line
    fj = font(46, jp=True)
    for i, ch in enumerate("ネオンナイト"):
        d.text((440, 90 + i * 56), ch, font=fj, fill=(255, 255, 255), stroke_width=3, stroke_fill=(120, 0, 120))
    fe = font(64)
    d.text((W / 2, 965), "NEON NIGHT", font=fe, fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=(90, 0, 110))
    d.rectangle([40, 1002, W - 40, 1008], fill=(60, 255, 240))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("SAVED", OUT)


if __name__ == "__main__":
    main()
