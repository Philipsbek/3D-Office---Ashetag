"""
Draws the picture on the sim-racing rig's three screens: one wide ORIGINAL
night-race scene (neon city skyline, wet road running to the horizon, a rival
car's tail lights ahead, racing HUD) split across the three monitors.

    python blender/objects/make_race_screens.py  -> blender/objects/textures/race_screens.png (1536 x 288)

Needs Pillow (system Python); the image is then loaded by sim_racing.py.
"""

import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "textures", "race_screens.png")
W, H = 1536, 288  # three 16:9 panels side by side
HORIZON = 132


def font(size):
    for path in ("C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main():
    rng = random.Random(11)
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    cx = W // 2

    # sky: deep indigo to magenta haze at the horizon
    for y in range(HORIZON):
        t = y / HORIZON
        d.line([(0, y), (W, y)], fill=(int(18 + 120 * t ** 2), int(8 + 14 * t), int(40 + 70 * t)))
    # skyline: blocky towers with lit windows and a few neon roof lines
    x = 0
    while x < W:
        w = rng.randint(26, 70)
        h = rng.randint(20, 95) if abs(x - cx) > 120 else rng.randint(14, 45)
        top = HORIZON - h
        d.rectangle([x, top, x + w, HORIZON], fill=(14, 10, 28))
        for wy in range(top + 5, HORIZON - 3, 7):
            for wx in range(x + 4, x + w - 4, 7):
                if rng.random() < 0.28:
                    d.rectangle([wx, wy, wx + 2, wy + 2], fill=rng.choice([(255, 190, 110), (120, 230, 255), (255, 90, 200)]))
        if rng.random() < 0.35:
            d.line([(x, top), (x + w, top)], fill=rng.choice([(34, 228, 255), (255, 79, 216)]), width=2)
        x += w + rng.randint(0, 8)

    # ground + road in perspective to a vanishing point at the centre
    d.rectangle([0, HORIZON, W, H], fill=(10, 8, 18))
    road_l, road_r = -260, W + 260
    d.polygon([(cx - 6, HORIZON), (cx + 6, HORIZON), (road_r, H), (road_l, H)], fill=(26, 24, 38))
    # wet-road reflections of the skyline
    for _ in range(140):
        rx = rng.randint(0, W)
        ry = rng.randint(HORIZON + 4, H)
        d.line([(rx, ry), (rx, ry + rng.randint(3, 10))], fill=rng.choice([(90, 40, 110), (30, 90, 120), (120, 70, 50)]))
    # neon edge lines (cyan left, magenta right) and dashed centre line
    d.line([(cx - 6, HORIZON), (road_l + 60, H)], fill=(34, 228, 255), width=4)
    d.line([(cx + 6, HORIZON), (road_r - 60, H)], fill=(255, 79, 216), width=4)
    for k in range(12):
        t0, t1 = (k / 12) ** 2, ((k + 0.5) / 12) ** 2
        y0, y1 = HORIZON + (H - HORIZON) * t0, HORIZON + (H - HORIZON) * t1
        w0, w1 = 1 + 6 * t0, 1 + 6 * t1
        d.polygon([(cx - w0, y0), (cx + w0, y0), (cx + w1, y1), (cx - w1, y1)], fill=(255, 210, 90))

    # rival car ahead: dark body with a red light bar
    car_y, cw = 178, 64
    d.rounded_rectangle([cx - cw, car_y - 22, cx + cw, car_y + 8], radius=8, fill=(12, 12, 18))
    d.rectangle([cx - cw + 6, car_y - 10, cx + cw - 6, car_y - 5], fill=(255, 40, 60))

    glow = img.filter(ImageFilter.GaussianBlur(5))
    img = Image.blend(img, glow, 0.35)
    d = ImageDraw.Draw(img)

    # HUD: centre panel speed + gear, left panel lap/position, right panel minimap
    f_big, f_mid, f_small = font(40), font(22), font(16)
    d.text((cx, H - 46), "248", font=f_big, fill=(255, 255, 255), anchor="mm")
    d.text((cx + 62, H - 40), "km/h", font=f_small, fill=(34, 228, 255), anchor="mm")
    d.text((cx - 70, H - 46), "6", font=f_big, fill=(255, 79, 216), anchor="mm")
    for i in range(14):  # rev bar
        col = (34, 228, 255) if i < 8 else (255, 210, 90) if i < 11 else (255, 50, 70)
        d.rectangle([cx - 105 + i * 15, 14, cx - 95 + i * 15, 24], fill=col if i < 12 else (50, 20, 30))
    d.text((28, 22), "LAP 2/3", font=f_mid, fill=(255, 255, 255))
    d.text((28, 50), "P1", font=f_big, fill=(255, 210, 90))
    d.text((W - 28, 22), "NEON CIRCUIT", font=f_small, fill=(34, 228, 255), anchor="ra")
    mm = [(W - 150, 60), (W - 60, 52), (W - 40, 100), (W - 90, 120), (W - 140, 108)]
    d.line(mm + [mm[0]], fill=(255, 79, 216), width=3)
    d.ellipse([W - 64, 48, W - 56, 56], fill=(255, 255, 255))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("SAVED", OUT)


if __name__ == "__main__":
    main()
