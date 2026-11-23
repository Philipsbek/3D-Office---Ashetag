"""
Draws the big TV's picture for the chill area: an ORIGINAL games-console home
screen (no real brand, logo or UI): deep blue-violet gradient with soft light
waves, a top bar (profile, clock), a row of game tiles with the selected one
lifted, and big hero art + title + "Play" button for the selected game.
All game names and art are made up.

    python blender/objects/make_console_home.py -> blender/objects/textures/console_home.png (1600 x 900)
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "textures", "console_home.png")
W, H = 1600, 900


def font(size, bold=True):
    for path in (("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf") if bold else ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf")):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
    return img


def hero_art(w, h, rng):
    """Made-up game key art: a neon city skyline under a big moon, a lone racer on the road."""
    img = gradient(w, h, (34, 10, 70), (210, 60, 140))
    d = ImageDraw.Draw(img)
    d.ellipse([w * 0.58, h * 0.08, w * 0.88, h * 0.08 + w * 0.3], fill=(255, 214, 150))
    x = 0
    while x < w:
        bw = rng.randint(40, 110)
        bh = rng.randint(int(h * 0.2), int(h * 0.62))
        d.rectangle([x, h * 0.78 - bh, x + bw, h * 0.78], fill=(18, 8, 40))
        for wy in range(int(h * 0.78 - bh) + 10, int(h * 0.78) - 8, 16):
            for wx in range(x + 8, x + bw - 8, 14):
                if rng.random() < 0.3:
                    d.rectangle([wx, wy, wx + 5, wy + 6], fill=rng.choice([(255, 200, 120), (90, 230, 255), (255, 90, 210)]))
        x += bw + rng.randint(2, 10)
    d.rectangle([0, h * 0.78, w, h], fill=(14, 6, 28))
    d.polygon([(w * 0.48, h * 0.78), (w * 0.52, h * 0.78), (w * 0.9, h), (w * 0.1, h)], fill=(40, 22, 70))
    d.line([(w * 0.48, h * 0.78), (w * 0.1, h)], fill=(34, 228, 255), width=4)
    d.line([(w * 0.52, h * 0.78), (w * 0.9, h)], fill=(255, 79, 216), width=4)
    # the racer: a low car silhouette with red tail lights
    cx, cy = w * 0.5, h * 0.9
    d.rounded_rectangle([cx - 70, cy - 26, cx + 70, cy + 8], radius=10, fill=(8, 8, 14))
    d.rectangle([cx - 60, cy - 14, cx + 60, cy - 8], fill=(255, 50, 70))
    return img.filter(ImageFilter.GaussianBlur(0.6))


def tile_art(w, h, kind, rng):
    palettes = [((255, 120, 60), (90, 20, 120)), ((40, 200, 255), (10, 30, 90)), ((120, 255, 160), (10, 60, 60)),
                ((255, 220, 90), (130, 40, 20)), ((200, 120, 255), (30, 10, 70)), ((255, 90, 150), (40, 10, 50))]
    top, bot = palettes[kind % len(palettes)]
    img = gradient(w, h, top, bot)
    d = ImageDraw.Draw(img)
    shape = kind % 3
    if shape == 0:  # planet + rings
        d.ellipse([w * 0.25, h * 0.25, w * 0.75, h * 0.75], fill=tuple(int(c * 0.5) for c in top))
        d.arc([w * 0.08, h * 0.42, w * 0.92, h * 0.6], 0, 360, fill=(255, 255, 255), width=4)
    elif shape == 1:  # mountains + sun
        d.ellipse([w * 0.55, h * 0.15, w * 0.85, h * 0.45], fill=(255, 245, 210))
        d.polygon([(0, h), (w * 0.35, h * 0.4), (w * 0.6, h * 0.75), (w * 0.8, h * 0.5), (w, h)], fill=tuple(int(c * 0.35) for c in bot))
    else:  # a sword / blade glyph
        d.polygon([(w * 0.5, h * 0.12), (w * 0.56, h * 0.62), (w * 0.44, h * 0.62)], fill=(240, 245, 255))
        d.rectangle([w * 0.34, h * 0.62, w * 0.66, h * 0.67], fill=(255, 210, 90))
        d.rectangle([w * 0.47, h * 0.67, w * 0.53, h * 0.86], fill=(60, 30, 20))
    return img


def main():
    rng = random.Random(7)
    img = gradient(W, H, (8, 10, 40), (22, 12, 70))
    # soft light waves across the background
    waves = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(waves)
    for k in range(5):
        pts = [(x, H * 0.62 + math.sin(x / 210 + k * 0.9) * 60 + k * 26) for x in range(0, W + 20, 20)]
        wd.line(pts, fill=(120, 140, 255, 40 + k * 8), width=3)
    img.paste(waves.filter(ImageFilter.GaussianBlur(2)), (0, 0), waves.filter(ImageFilter.GaussianBlur(2)))

    # hero art for the selected game fills the top-right, fading into the background
    hero = hero_art(1000, 560, rng).convert("RGBA")
    mask = Image.new("L", hero.size, 0)
    md = ImageDraw.Draw(mask)
    for x in range(hero.width):
        md.line([(x, 0), (x, hero.height)], fill=int(255 * min(1, x / 360)))
    fade_bottom = Image.new("L", hero.size, 0)
    fd = ImageDraw.Draw(fade_bottom)
    for y in range(hero.height):
        fd.line([(0, y), (hero.width, y)], fill=int(255 * min(1, (hero.height - y) / 180)))
    mask = Image.composite(mask, Image.new("L", hero.size, 0), fade_bottom)
    img.paste(hero, (W - hero.width, 0), mask)

    d = ImageDraw.Draw(img)
    f_title, f_mid, f_small, f_tiny = font(64), font(28), font(22, bold=False), font(18)

    # top bar: home icon, store, then clock + profile on the right
    d.rounded_rectangle([60, 40, 108, 88], radius=10, outline=(235, 240, 255), width=3)
    d.text((132, 50), "Games", font=f_mid, fill=(255, 255, 255))
    d.text((250, 50), "Media", font=f_mid, fill=(150, 160, 200))
    d.rounded_rectangle([W - 250, 42, W - 130, 88], radius=23, fill=(14, 12, 44))
    d.text((W - 190, 65), "21:47", font=f_mid, fill=(235, 240, 255), anchor="mm")
    d.ellipse([W - 110, 40, W - 60, 90], fill=(255, 120, 60), outline=(255, 255, 255), width=3)

    # tile row: selected tile lifted + outlined, the rest smaller
    names = ["NEON DRIFT", "STARFALL", "PIXEL KNIGHTS", "DEEP ORBIT", "SUMMIT", "BLADE CITY", "GARDEN 2"]
    x, y0 = 60, 150
    for i, n in enumerate(names):
        size = 172 if i == 0 else 128
        y = y0 if i == 0 else y0 + 22
        art = tile_art(size, size, i + 1, rng) if i else hero_art(size, size, rng)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=16, fill=255)
        img.paste(art, (x, y), mask)
        if i == 0:
            d.rounded_rectangle([x - 6, y - 6, x + size + 6, y + size + 6], radius=20, outline=(255, 255, 255), width=4)
            d.text((x + size + 22, y + size - 34), n, font=f_mid, fill=(255, 255, 255))
            x += size + 220
        else:
            x += size + 18
        if x > W - 140:
            break

    # selected game: title, blurb, Play button, progress
    d.text((60, 430), "NEON DRIFT", font=f_title, fill=(255, 255, 255))
    d.text((64, 510), "Race the night city. Season 3 is live.", font=f_small, fill=(205, 210, 240))
    d.rounded_rectangle([60, 570, 300, 640], radius=35, fill=(255, 255, 255))
    d.text((180, 605), "Play", font=f_mid, fill=(10, 10, 30), anchor="mm")
    d.rounded_rectangle([320, 570, 390, 640], radius=35, outline=(235, 240, 255), width=3)
    d.text((355, 603), "···", font=f_mid, fill=(235, 240, 255), anchor="mm")
    d.text((60, 690), "Progress  68%", font=f_tiny, fill=(170, 180, 220))
    d.rounded_rectangle([60, 720, 420, 728], radius=4, fill=(60, 64, 110))
    d.rounded_rectangle([60, 720, 60 + int(360 * 0.68), 728], radius=4, fill=(255, 255, 255))

    # bottom: activity cards
    for k, (t, s) in enumerate((("Trophy unlocked", "Night Owl · NEON DRIFT"), ("Friend online", "Philips is napping"), ("New update", "STARFALL 1.4"))):
        cx = 560 + k * 340
        d.rounded_rectangle([cx, 700, cx + 320, 820], radius=18, fill=(26, 24, 78), outline=(110, 120, 190), width=2)
        d.text((cx + 22, 722), t, font=f_tiny, fill=(170, 180, 220))
        d.text((cx + 22, 756), s, font=f_small, fill=(255, 255, 255))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("SAVED", OUT)


if __name__ == "__main__":
    main()
