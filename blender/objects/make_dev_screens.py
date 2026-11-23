"""
Draws the pictures for the workstations' new ultrawide monitors (21:9, 2560 x 1080):

  textures/dev_screen_code.png  a dark code editor (file tree, tabs, syntax-coloured TSX of this
                                very site, minimap, a terminal showing a git push) next to a
                                browser with the repo page
  textures/dev_screen_repo.png  a dark git-hosting repository page (file list, README, language
                                bar, contribution graph) next to a narrower editor

ORIGINAL UI only: styled like popular dark-mode dev tools but no real product names or logos
(the repo lives at git.philipsbek.dev).

    python blender/objects/make_dev_screens.py
"""

import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "textures")
W, H = 2560, 1080

BG = (13, 17, 23)
PANEL = (22, 27, 34)
LINE = (48, 54, 61)
TEXT = (230, 237, 243)
MUTED = (139, 148, 158)
BLUE = (88, 166, 255)
GREEN = (63, 185, 80)
PINK = (255, 123, 172)
ORANGE = (255, 166, 87)
PURPLE = (210, 168, 255)
CYAN = (121, 192, 255)
STRING = (165, 214, 255)
COMMENT = (110, 118, 129)


def font(size, mono=True, bold=False):
    names = (("consolab.ttf" if bold else "consola.ttf"),) if mono else (("segoeuib.ttf" if bold else "segoeui.ttf"), "arial.ttf")
    for n in names:
        p = os.path.join("C:/Windows/Fonts", n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


CODE = [
    [("// ", COMMENT), ("Floating speech bubbles over each section of the 3D office", COMMENT)],
    [("import", PINK), (" { ", TEXT), ("useFrame", CYAN), (", ", TEXT), ("useThree", CYAN), (" } ", TEXT), ("from", PINK), (" '@react-three/fiber'", STRING)],
    [("import", PINK), (" * ", TEXT), ("as", PINK), (" THREE ", TEXT), ("from", PINK), (" 'three'", STRING)],
    [],
    [("export", PINK), (" ", TEXT), ("function", PINK), (" ", TEXT), ("SectionBubbles", PURPLE), ("({ hotspots, current, onSelect }: ", TEXT), ("Props", ORANGE), (") {", TEXT)],
    [("  ", TEXT), ("const", PINK), (" { camera, size } = ", TEXT), ("useThree", PURPLE), ("()", TEXT)],
    [("  ", TEXT), ("const", PINK), (" v = ", TEXT), ("useMemo", PURPLE), ("(() => ", TEXT), ("new", PINK), (" THREE.", TEXT), ("Vector3", ORANGE), ("(), [])", TEXT)],
    [],
    [("  ", TEXT), ("useFrame", PURPLE), ("(() => {", TEXT)],
    [("    hotspots.", TEXT), ("forEach", PURPLE), ("((h, i) => {", TEXT)],
    [("      v.", TEXT), ("copy", PURPLE), ("(h.top).", TEXT), ("project", PURPLE), ("(camera)", TEXT)],
    [("      ", TEXT), ("const", PINK), (" x = ((v.x + ", TEXT), ("1", ORANGE), (") / ", TEXT), ("2", ORANGE), (") * size.width", TEXT)],
    [("      ", TEXT), ("const", PINK), (" y = ((", TEXT), ("1", ORANGE), (" - v.y) / ", TEXT), ("2", ORANGE), (") * size.height", TEXT)],
    [("      ", TEXT), ("// keep the bubble clear of the top bar", COMMENT)],
    [("      bubbles[i].style.transform = ", TEXT), ("`translate(${", STRING), ("x", TEXT), ("}px, ${", STRING), ("Math", ORANGE), (".", TEXT), ("max", PURPLE), ("(y, ", TEXT), ("90", ORANGE), (")", TEXT), ("}px)`", STRING)],
    [("    })", TEXT)],
    [("  })", TEXT)],
    [],
    [("  ", TEXT), ("return", PINK), (" ", TEXT), ("null", ORANGE)],
    [("}", TEXT)],
    [],
    [("export", PINK), (" ", TEXT), ("const", PINK), (" MEMO_SPOTS = {", TEXT)],
    [("  chengnan: { object: ", TEXT), ("'LoungeSpot'", STRING), (" },", TEXT)],
    [("  simrig: { object: ", TEXT), ("'SimRigSpot'", STRING), (", view: { eye: [", TEXT), ("0", ORANGE), (", ", TEXT), ("1.05", ORANGE), (", ", TEXT), ("0.5", ORANGE), ("] } },", TEXT)],
    [("  pinball: { object: ", TEXT), ("'PinballSpot'", STRING), (" },", TEXT)],
    [("}", TEXT)],
]


def editor(img, x0, y0, x1, y1, rng, terminal=True, title="Scene.tsx"):
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], fill=BG)
    f, fs, fb = font(22), font(19), font(20, bold=True)
    # activity bar + file tree
    d.rectangle([x0, y0, x0 + 56, y1], fill=(10, 13, 18))
    for k in range(5):
        d.rounded_rectangle([x0 + 16, y0 + 24 + k * 64, x0 + 40, y0 + 48 + k * 64], radius=5, outline=MUTED if k else BLUE, width=3)
    tx = x0 + 56
    d.rectangle([tx, y0, tx + 300, y1], fill=PANEL)
    d.text((tx + 20, y0 + 18), "EXPLORER", font=fs, fill=MUTED)
    tree = [("v office-starter", TEXT, 0), ("v app", TEXT, 1), ("page.tsx", MUTED, 2), ("layout.tsx", MUTED, 2), ("v components", TEXT, 1),
            ("Scene.tsx", BLUE, 2), ("CityScape.tsx", MUTED, 2), ("Memo.tsx", MUTED, 2), ("arcadeGame.ts", MUTED, 2), ("v content", TEXT, 1),
            ("site.ts", MUTED, 2), ("> blender", TEXT, 1), ("> public", TEXT, 1), ("package.json", MUTED, 1), ("README.md", MUTED, 1)]
    for k, (n, c, depth) in enumerate(tree):
        yy = y0 + 60 + k * 34
        if n == title:
            d.rectangle([tx, yy - 4, tx + 300, yy + 26], fill=(33, 40, 52))
        d.text((tx + 20 + depth * 18, yy), n, font=fs, fill=c)
    # tabs
    ex = tx + 300
    d.rectangle([ex, y0, x1, y0 + 46], fill=PANEL)
    others = [n for n in ("Scene.tsx", "CityScape.tsx", "site.ts") if n != title][:2]
    for k, n in enumerate([title] + others):
        bx = ex + k * 210
        d.rectangle([bx, y0, bx + 208, y0 + 46], fill=BG if k == 0 else PANEL)
        if k == 0:
            d.line([(bx, y0), (bx + 208, y0)], fill=BLUE, width=3)
        d.text((bx + 18, y0 + 12), n, font=fs, fill=TEXT if k == 0 else MUTED)
    # code with line numbers
    code_bottom = y1 - (300 if terminal else 40)
    lh = 32
    for i, line in enumerate(CODE):
        yy = y0 + 64 + i * lh
        if yy > code_bottom - lh:
            break
        d.text((ex + 18, yy), f"{i + 1:>3}", font=f, fill=(72, 79, 88))
        if i == 14:
            d.rectangle([ex + 70, yy - 4, x1 - 140, yy + lh - 6], fill=(28, 36, 48))
        cx = ex + 80
        for txt, col in line:
            d.text((cx, yy), txt, font=f, fill=col)
            cx += d.textlength(txt, font=f)
    # blinking-cursor stand-in on line 15
    d.rectangle([ex + 900, y0 + 64 + 14 * lh, ex + 903, y0 + 64 + 14 * lh + 24], fill=TEXT)
    # minimap (only on a wide editor, so it never sits on top of the code)
    mx = x1 - 120
    for k in range(70 if (x1 - ex) > 1100 else 0):
        yy = y0 + 60 + k * 9
        if yy > code_bottom:
            break
        ln = rng.randint(10, 90)
        d.rectangle([mx, yy, mx + ln, yy + 4], fill=rng.choice([PINK, CYAN, STRING, MUTED, PURPLE]) + (0,))
    # terminal
    if terminal:
        ty = y1 - 290
        d.rectangle([ex, ty, x1, y1 - 30], fill=(10, 13, 18))
        d.line([(ex, ty), (x1, ty)], fill=LINE, width=2)
        d.text((ex + 18, ty + 10), "TERMINAL", font=fs, fill=TEXT)
        d.line([(ex + 18, ty + 38), (ex + 118, ty + 38)], fill=BLUE, width=2)
        lines = [
            [("philips@studio ", GREEN), ("~/office-starter (main) ", CYAN), ("$ git push origin main", TEXT)],
            [("Enumerating objects: 42, done.", MUTED)],
            [("Writing objects: 100% (24/24), 3.41 MiB | 8.2 MiB/s, done.", MUTED)],
            [("To git.philipsbek.dev:philipsbek/portfolio-3d.git", MUTED)],
            [("   9f2c1ab..e47d0c2  main -> main", GREEN)],
            [("philips@studio ", GREEN), ("~/office-starter (main) ", CYAN), ("$ ", TEXT)],
        ]
        for k, line in enumerate(lines):
            cx = ex + 18
            for txt, col in line:
                d.text((cx, ty + 56 + k * 34), txt, font=f, fill=col)
                cx += d.textlength(txt, font=f)
    # status bar
    d.rectangle([x0, y1 - 30, x1, y1], fill=(31, 111, 235))
    d.text((x0 + 70, y1 - 26), "main   0 errors   0 warnings", font=fs, fill=(255, 255, 255))
    d.text((x1 - 420, y1 - 26), "Ln 15, Col 42   TypeScript React", font=fs, fill=(255, 255, 255))


def repo(img, x0, y0, x1, y1, rng, compact=False):
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], fill=BG)
    ui, uib, big, small = font(24, mono=False), font(24, mono=False, bold=True), font(34, mono=False, bold=True), font(20, mono=False)
    # browser chrome
    d.rectangle([x0, y0, x1, y0 + 60], fill=(32, 34, 40))
    for k, c in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        d.ellipse([x0 + 20 + k * 30, y0 + 22, x0 + 36 + k * 30, y0 + 38], fill=c)
    d.rounded_rectangle([x0 + 140, y0 + 12, x1 - 40, y0 + 48], radius=18, fill=(18, 20, 24))
    d.text((x0 + 164, y0 + 18), "git.philipsbek.dev/philipsbek/portfolio-3d", font=small, fill=MUTED)
    # site header
    hy = y0 + 60
    d.rectangle([x0, hy, x1, hy + 64], fill=(1, 4, 9))
    d.rounded_rectangle([x0 + 24, hy + 14, x0 + 60, hy + 50], radius=9, fill=(240, 246, 252))
    d.polygon([(x0 + 34, hy + 40), (x0 + 42, hy + 22), (x0 + 50, hy + 40)], fill=(1, 4, 9))  # original mark: a little peak
    d.text((x0 + 76, hy + 18), "philipsbek", font=ui, fill=TEXT)
    d.text((x0 + 76 + d.textlength("philipsbek ", font=ui), hy + 18), "/ portfolio-3d", font=uib, fill=TEXT)
    bx = x0 + 76 + d.textlength("philipsbek / portfolio-3d", font=uib) + 28
    d.rounded_rectangle([bx, hy + 18, bx + 80, hy + 46], radius=14, outline=LINE, width=2)
    d.text((bx + 12, hy + 20), "Public", font=small, fill=MUTED)
    # tabs
    ty = hy + 64
    d.line([(x0, ty + 52), (x1, ty + 52)], fill=LINE, width=2)
    tx = x0 + 24
    for k, (n, cnt) in enumerate((("Code", ""), ("Issues", "3"), ("Pull requests", "1"), ("Actions", ""), ("Insights", ""))):
        d.text((tx, ty + 12), n, font=ui, fill=TEXT)
        w = d.textlength(n, font=ui)
        if cnt:
            d.rounded_rectangle([tx + w + 8, ty + 14, tx + w + 38, ty + 40], radius=12, fill=(48, 54, 61))
            d.text((tx + w + 17, ty + 15), cnt, font=small, fill=TEXT)
            w += 40
        if k == 0:
            d.line([(tx - 4, ty + 51), (tx + w + 4, ty + 51)], fill=ORANGE, width=4)
        tx += w + 40
    # main column: branch row + file table
    my = ty + 80
    main_r = x1 - (40 if compact else 470)
    d.rounded_rectangle([x0 + 24, my, x0 + 184, my + 44], radius=8, fill=PANEL, outline=LINE, width=2)
    d.text((x0 + 40, my + 8), "main  v", font=ui, fill=TEXT)
    d.rounded_rectangle([main_r - 150, my, main_r, my + 44], radius=8, fill=(35, 134, 54))
    d.text((main_r - 128, my + 8), "<> Code", font=uib, fill=(255, 255, 255))
    fy = my + 64
    d.rounded_rectangle([x0 + 24, fy, main_r, fy + 70 + 9 * 52], radius=8, outline=LINE, width=2, fill=BG)
    d.rectangle([x0 + 26, fy + 2, main_r - 2, fy + 68], fill=PANEL)
    d.ellipse([x0 + 44, fy + 18, x0 + 76, fy + 50], fill=(255, 120, 60))
    d.text((x0 + 90, fy + 20), "philipsbek", font=uib, fill=TEXT)
    d.text((x0 + 90 + d.textlength("philipsbek  ", font=uib), fy + 20), "Add the neon bar and the chill zone", font=ui, fill=MUTED)
    d.text((main_r - 190, fy + 20), "e47d0c2 · now", font=small, fill=MUTED)
    files = [("app", "Lab arcade: What I Build select screen", "2 hours ago", True),
             ("blender", "Bar: drinks, snacks, back bar", "now", True),
             ("components", "Section bubbles + glass hover", "1 hour ago", True),
             ("content", "Services rewrite: design, dev, growth", "3 hours ago", True),
             ("public", "Rebuild office.glb (v27)", "now", True),
             ("README.md", "Docs: how to rebuild the office", "yesterday", False),
             ("next.config.ts", "Initial commit", "last week", False),
             ("package.json", "Add three + r3f", "last week", False),
             ("tsconfig.json", "Initial commit", "last week", False)]
    for k, (n, msg, when, folder) in enumerate(files):
        yy = fy + 70 + k * 52
        d.line([(x0 + 26, yy), (main_r - 2, yy)], fill=LINE, width=1)
        if folder:
            d.rounded_rectangle([x0 + 44, yy + 16, x0 + 70, yy + 36], radius=3, fill=(84, 174, 255))
        else:
            d.rectangle([x0 + 48, yy + 12, x0 + 66, yy + 38], outline=MUTED, width=2)
        d.text((x0 + 90, yy + 12), n, font=ui, fill=TEXT)
        room = (main_r - 180) - (x0 + 360)
        while d.textlength(msg, font=ui) > room and len(msg) > 4:
            msg = msg[:-2].rstrip() + "…" if not msg.endswith("…") else msg[:-2] + "…"
        d.text((x0 + 360, yy + 12), msg, font=ui, fill=MUTED)
        d.text((main_r - 160, yy + 12), when, font=small, fill=MUTED)
    # README card
    ry = fy + 70 + 9 * 52 + 24
    if ry < y1 - 80:
        d.rounded_rectangle([x0 + 24, ry, main_r, y1 - 20], radius=8, outline=LINE, width=2)
        d.text((x0 + 48, ry + 16), "README.md", font=uib, fill=TEXT)
        d.text((x0 + 48, ry + 64), "Philips Bek — 3D Portfolio", font=big, fill=TEXT)
        d.text((x0 + 48, ry + 116), "My portfolio: an explorable cyberpunk office I built in Blender + React Three Fiber.", font=ui, fill=MUTED)
    if compact:
        return
    # sidebar: about, languages, contributions
    sx = x1 - 440
    d.text((sx, my + 4), "About", font=uib, fill=TEXT)
    d.text((sx, my + 48), "My portfolio site: a 3D office you", font=ui, fill=MUTED)
    d.text((sx, my + 80), "can walk around in the browser.", font=ui, fill=MUTED)
    for k, t in enumerate(("threejs", "react", "blender", "webgl")):
        tx = sx + k * 102
        d.rounded_rectangle([tx, my + 124, tx + 94, my + 156], radius=16, fill=(18, 38, 64))
        d.text((tx + 12, my + 127), t, font=small, fill=BLUE)
    ly = my + 200
    d.text((sx, ly), "Languages", font=uib, fill=TEXT)
    segs = [(0.62, (49, 120, 198)), (0.24, (255, 212, 59)), (0.1, (227, 76, 38)), (0.04, (86, 61, 124))]
    bx = sx
    for frac, col in segs:
        w = int(400 * frac)
        d.rectangle([bx, ly + 46, bx + w, ly + 58], fill=col)
        bx += w
    for k, (n, p, col) in enumerate((("TypeScript", "62%", (49, 120, 198)), ("Python", "24%", (255, 212, 59)), ("CSS", "10%", (227, 76, 38)))):
        yy = ly + 76 + k * 34
        d.ellipse([sx, yy + 6, sx + 14, yy + 20], fill=col)
        d.text((sx + 24, yy), f"{n}  {p}", font=small, fill=MUTED)
    gy = ly + 200
    d.text((sx, gy), "Contributions", font=uib, fill=TEXT)
    greens = [(22, 27, 34), (14, 68, 41), (0, 109, 50), (38, 166, 65), (57, 211, 83)]
    for cx in range(20):
        for cy in range(7):
            v = rng.choices(range(5), weights=(3, 3, 3, 2, 1))[0]
            d.rounded_rectangle([sx + cx * 20, gy + 44 + cy * 20, sx + cx * 20 + 16, gy + 60 + cy * 20], radius=3, fill=greens[v])


def main():
    rng = random.Random(4)
    os.makedirs(OUT_DIR, exist_ok=True)
    # screen 1: big editor (left 62%) + repo page in a narrow browser
    a = Image.new("RGB", (W, H), BG)
    editor(a, 0, 0, int(W * 0.62), H, rng)
    ImageDraw.Draw(a).rectangle([int(W * 0.62), 0, int(W * 0.62) + 6, H], fill=(0, 0, 0))
    repo(a, int(W * 0.62) + 6, 0, W, H, rng, compact=True)
    a.save(os.path.join(OUT_DIR, "dev_screen_code.png"))
    # screen 2: big repo page (left 64%) + editor without terminal
    b = Image.new("RGB", (W, H), BG)
    repo(b, 0, 0, int(W * 0.64), H, rng)
    ImageDraw.Draw(b).rectangle([int(W * 0.64), 0, int(W * 0.64) + 6, H], fill=(0, 0, 0))
    editor(b, int(W * 0.64) + 6, 0, W, H, rng, terminal=True, title="site.ts")
    b.save(os.path.join(OUT_DIR, "dev_screen_repo.png"))
    print("SAVED dev_screen_code.png, dev_screen_repo.png")


if __name__ == "__main__":
    main()
