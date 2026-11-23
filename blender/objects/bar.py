"""
Neon bar for the loft's lower floor, ORIGINAL designs only (no real brands or labels):

  build_bar_counter(parent, name, length)  straight bar counter: gloss-black top with a rounded
                               front lip, ribbed dark front with a magenta under-glow, cyan neon
                               edge strip, chrome foot rail; bartender side has a work shelf
  build_back_bar(parent, name, length)     wall shelving behind the bar: three glass shelves on
                               black uprights, warm amber backlight panel, a small neon "BAR" sign
  build_bottle(parent, name, kind, glass, label)  one original bottle (lathed), plain label band
  build_back_bar_drinks(parent, name, length)      rows of bottles + upturned glasses for the shelves
  build_counter_drinks(parent, name)               cocktails, a shaker and cans for the counter top
  build_bar_snacks(parent, name)                   crisps, popcorn bucket, nachos, nuts for the counter
  build_bar_preview(parent, name)          counter + back bar together, as they'll stand
  build_bar_area(parent, name)             the placed set: counter (origin) + drinks + snacks, back bar
                               with its bottles 1.36 m behind it (-Z), leaving a bartender walkway

Coordinates are three.js style (Y up). Customers stand at +Z; the back bar's shelves face +Z.
Origin at the centre of each piece's footprint on the floor.
"""

import math
import os
import random
import sys

import bmesh

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat, slab  # noqa: E402

COUNTER_H = 1.05
COUNTER_D = 0.62


def _root(name, parent):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    return root


def build_bar_counter(parent=None, name="BarCounter", length=2.4):
    BODY = mat("BarBody", "#121117", 0.55)
    RIB = mat("BarRib", "#1c1a22", 0.45, metal=0.3)
    TOP = mat("BarTop", "#07070a", 0.08, metal=0.4)  # glossy black
    CHROME = mat("BarChrome", "#b6bcc4", 0.15, metal=1.0)
    PINK = mat("BarNeonPink", "#ff2bd6", emit="#ff2bd6", strength=7.0)
    CYAN = mat("BarNeonCyan", "#22e4ff", emit="#22e4ff", strength=7.0)
    SHELF = mat("BarWorkShelf", "#22202a", 0.5)

    root = _root(name, parent)
    L, D, H = length, COUNTER_D, COUNTER_H
    kick = 0.08  # recessed toe kick so the under-glow spills on the floor

    block(f"{name}Kick", (0, kick / 2, -0.04), (L - 0.1, kick, D - 0.16), BODY, root)
    block(f"{name}Body", (0, kick + (H - kick - 0.05) / 2, -0.03), (L, H - kick - 0.05, D - 0.12), BODY, root, r=0.01)
    # ribbed front: vertical fins across the customer side
    n = int(L / 0.08)
    for k in range(n):
        x = -L / 2 + 0.06 + k * (L - 0.12) / (n - 1)
        block(f"{name}Rib{k}", (x, kick + (H - kick - 0.12) / 2 + 0.02, D / 2 - 0.08), (0.035, H - kick - 0.14, 0.03), RIB, root, r=0.004)
    # magenta under-glow along the toe kick
    slab(f"{name}UnderGlow", -L / 2 + 0.06, L / 2 - 0.06, kick - 0.012, kick - 0.004, D / 2 - 0.12, D / 2 - 0.1, PINK, root)
    # glossy top with an overhang toward the customers, cyan neon strip under its front lip
    block(f"{name}Top", (0, H - 0.025, 0.02), (L + 0.08, 0.05, D + 0.04), TOP, root, r=0.015)
    slab(f"{name}TopNeon", -L / 2 - 0.02, L / 2 + 0.02, H - 0.058, H - 0.05, D / 2 + 0.02, D / 2 + 0.035, CYAN, root)
    # chrome foot rail on short posts
    ry, rz = 0.22, D / 2 + 0.12
    tube(f"{name}FootRail", [(-L / 2 + 0.1, ry, rz), (L / 2 - 0.1, ry, rz)], 0.02, CHROME, root)
    for k, x in enumerate((-L / 2 + 0.2, 0.0, L / 2 - 0.2)):
        tube(f"{name}RailPost{k}", [(x, ry, rz), (x, ry, D / 2 - 0.09)], 0.014, CHROME, root)
    # bartender side: a recessed work shelf
    slab(f"{name}WorkShelf", -L / 2 + 0.08, L / 2 - 0.08, H - 0.32, H - 0.3, -D / 2 - 0.01, -D / 2 + 0.2, SHELF, root)
    return root


def build_back_bar(parent=None, name="BackBar", length=2.4):
    UPRIGHT = mat("BackBarUpright", "#0d0c11", 0.4, metal=0.6)
    GLASS = mat("BackBarShelfGlass", "#9fb6c8", 0.05, metal=0.0)
    PANEL = mat("BackBarBacking", "#1d140f", 0.6)  # dark wood
    AMBER = mat("BackBarAmber", "#ffb35a", emit="#ff9a3c", strength=6.0)
    CAB = mat("BackBarCabinet", "#141219", 0.5)
    TOP = mat("BackBarTop", "#07070a", 0.1, metal=0.4)
    SIGN = mat("BackBarSign", "#ff2bd6", emit="#ff2bd6", strength=9.0)
    TRIM = mat("BackBarTrim", "#22e4ff", emit="#22e4ff", strength=5.0)

    root = _root(name, parent)
    L, D = length, 0.4
    # low cabinet with a black top
    block(f"{name}Cabinet", (0, 0.45, 0), (L, 0.9, D), CAB, root, r=0.01)
    block(f"{name}CabTop", (0, 0.915, 0.01), (L + 0.04, 0.03, D + 0.04), TOP, root, r=0.008)
    for k in range(4):  # cabinet door seams
        x = -L / 2 + (k + 1) * L / 5
        slab(f"{name}Seam{k}", x - 0.004, x + 0.004, 0.06, 0.86, D / 2, D / 2 + 0.004, UPRIGHT, root)
    # warm backlight panel + three glass shelves on black uprights above the cabinet
    zb = -D / 2 + 0.04
    block(f"{name}Backing", (0, 1.55, zb), (L - 0.1, 1.1, 0.02), PANEL, root)
    for s in (-1, 1):
        block(f"{name}Upright{s}", (s * (L / 2 - 0.03), 1.6, -0.08), (0.05, 1.3, 0.24), UPRIGHT, root, r=0.006)
    for k, y in enumerate((1.3, 1.68, 2.06)):
        block(f"{name}Shelf{k}", (0, y, -0.07), (L - 0.06, 0.018, 0.24), GLASS, root, r=0.004)
        slab(f"{name}ShelfTrim{k}", -L / 2 + 0.06, L / 2 - 0.06, y - 0.012, y - 0.008, 0.048, 0.052, TRIM, root)
        # warm LED strip under each shelf, washing the bottles below and the backing
        slab(f"{name}ShelfLed{k}", -L / 2 + 0.08, L / 2 - 0.08, y - 0.02, y - 0.012, -0.15, -0.13, AMBER, root)
    # and a soft amber strip along the top of the cabinet, against the backing
    slab(f"{name}BaseLed", -L / 2 + 0.08, L / 2 - 0.08, 0.932, 0.94, zb + 0.012, zb + 0.03, AMBER, root)
    block(f"{name}Crown", (0, 2.27, -0.07), (L, 0.06, 0.26), UPRIGHT, root, r=0.008)
    # small neon "BAR" sign on the crown
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    t.name = f"{name}Sign"
    t.data.body = "BAR"
    t.data.align_x = "CENTER"
    t.data.size = 0.16
    t.data.extrude = 0.008
    t.location = P(0, 2.31, 0.06)
    t.rotation_euler = (math.pi / 2, 0, 0)
    t.data.materials.append(SIGN)
    for c in list(t.users_collection):
        c.objects.unlink(t)
    bpy.context.collection.objects.link(t)
    t.parent = root
    return root


def lathe(name, profile, m, parent, segs=24, smooth=True):
    """Spin a (radius, height) profile, bottom to top, around Y into a closed solid."""
    bm = bmesh.new()
    rings = []
    for r, y in profile:
        if r <= 1e-5:
            rings.append([bm.verts.new(P(0, y, 0))])
        else:
            rings.append([bm.verts.new(P(r * math.cos(2 * math.pi * i / segs), y, r * math.sin(2 * math.pi * i / segs))) for i in range(segs)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for i in range(segs):
                bm.faces.new((a[0], b[(i + 1) % segs], b[i]))
        elif len(b) == 1:
            for i in range(segs):
                bm.faces.new((a[i], a[(i + 1) % segs], b[0]))
        else:
            for i in range(segs):
                bm.faces.new((a[i], a[(i + 1) % segs], b[(i + 1) % segs], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    o.parent = parent
    return o


# bottle silhouettes: (radius, height) from the base up, in metres
BOTTLES = {
    "wine": [(0, 0), (0.037, 0), (0.038, 0.2), (0.033, 0.235), (0.014, 0.26), (0.013, 0.31), (0.015, 0.315), (0, 0.316)],
    "round": [(0, 0), (0.05, 0), (0.055, 0.06), (0.052, 0.14), (0.03, 0.17), (0.016, 0.19), (0.016, 0.22), (0, 0.22)],
    "tall": [(0, 0), (0.03, 0), (0.031, 0.25), (0.024, 0.28), (0.011, 0.31), (0.011, 0.35), (0, 0.35)],
    "flask": [(0, 0), (0.045, 0), (0.046, 0.13), (0.04, 0.16), (0.017, 0.175), (0.017, 0.205), (0.02, 0.21), (0, 0.212)],
    "stubby": [(0, 0), (0.042, 0), (0.043, 0.12), (0.03, 0.15), (0.02, 0.165), (0.02, 0.18), (0, 0.18)],
}


def build_bottle(parent=None, name="Bottle", kind="wine", glass="#3c8a4a", label="#e8e0cc", cap="#151515"):
    """One original bottle: tinted glossy glass, a plain label band (no text), a cap."""
    GLASS = mat(f"BottleGlass{glass[1:]}", glass, 0.05, metal=0.1, emit=glass, strength=0.18)
    LABEL = mat(f"BottleLabel{label[1:]}", label, 0.7)
    CAP = mat(f"BottleCap{cap[1:]}", cap, 0.4, metal=0.6)
    root = _root(name, parent)
    prof = BOTTLES[kind]
    lathe(f"{name}Body", prof, GLASS, root)
    top = prof[-1][1]
    neck_r = max(r for r, y in prof if y > top * 0.8)
    body_r = max(r for r, _ in prof)
    lathe(f"{name}Cap", [(0, top - 0.025), (neck_r + 0.002, top - 0.025), (neck_r + 0.002, top + 0.004), (0, top + 0.004)], CAP, root, segs=16)
    y0, y1 = top * 0.25, top * 0.25 + min(0.08, top * 0.3)
    lathe(f"{name}Label", [(0, y0), (body_r + 0.0015, y0), (body_r + 0.0015, y1), (0, y1)], LABEL, root)
    return root


# a varied palette of glass tints and label colours (all plain, no branding)
_GLASS = ["#5a2a0a", "#1d3d22", "#3d0a14", "#2a2a30", "#7f939c", "#14324a", "#6b4a10", "#4a1a2a"]
_LABEL = ["#e8e0cc", "#e8e0cc", "#151515", "#151515", "#d8b46a", "#f0f0f0", "#8a1c2a"]


def build_back_bar_drinks(parent=None, name="BackBarDrinks", length=2.4, seed=5):
    """Bottles across the cabinet top and the two lower shelves; upturned glasses on the top shelf."""
    rng = random.Random(seed)
    root = _root(name, parent)
    kinds = list(BOTTLES)
    rows = ((0.93, -0.1, 0.13), (1.31, -0.08, 0.125), (1.69, -0.08, 0.13))  # (surface y, z, spacing)
    for r, (y, z, gap) in enumerate(rows):
        n = int((length - 0.3) / gap)
        for k in range(n):
            if rng.random() < 0.12:
                continue  # a few gaps look real
            x = -length / 2 + 0.17 + k * gap + rng.uniform(-0.015, 0.015)
            b = build_bottle(root, f"{name}R{r}B{k}", rng.choice(kinds), rng.choice(_GLASS), rng.choice(_LABEL))
            b.location = P(x, y, z + rng.uniform(-0.02, 0.02))
    # top shelf: a row of upturned glasses
    GLASSW = mat("BarGlassware", "#cfe6f2", 0.05, emit="#9fd8ff", strength=0.25)
    for k in range(int((length - 0.3) / 0.09)):
        x = -length / 2 + 0.17 + k * 0.09
        lathe(f"{name}Glass{k}", [(0, 2.07), (0.03, 2.07), (0.034, 2.17), (0.0, 2.17)], GLASSW, root, segs=16).location = P(x, 0, -0.08)
    return root


def build_counter_drinks(parent=None, name="CounterDrinks"):
    """Cocktails, a shaker and a few cans on the counter top (origin at the top surface)."""
    GLASSW = mat("BarGlasswareClear", "#dff1fa", 0.04, emit="#bfe8ff", strength=0.2)
    PINKD = mat("DrinkPink", "#ff4fb8", 0.2, emit="#ff4fb8", strength=1.6)
    CYAND = mat("DrinkCyan", "#22e4ff", 0.2, emit="#22e4ff", strength=1.6)
    AMBERD = mat("DrinkAmber", "#e08a2a", 0.2, emit="#e08a2a", strength=1.0)
    ICE = mat("DrinkIce", "#e8f7ff", 0.05, emit="#cfefff", strength=0.4)
    STRAW = mat("DrinkStraw", "#b6ff3b", 0.4)
    LIME = mat("DrinkLime", "#8fd14f", 0.5)
    CHROME = mat("BarChrome", "#b6bcc4", 0.15, metal=1.0)
    root = _root(name, parent)

    # 1) coupe/martini glass with a pink cocktail + lime wheel
    g = _root(f"{name}Martini", root)
    g.location = P(-0.55, 0, 0.05)
    disc(f"{name}MartiniFoot", (0, 0.003, 0), 0.035, 0.006, GLASSW, g, axis="y", verts=20)
    tube(f"{name}MartiniStem", [(0, 0.005, 0), (0, 0.104, 0)], 0.0065, GLASSW, g)
    ring(f"{name}MartiniRim", (0, 0.165, 0), 0.055, 0.002, GLASSW, g, axis="y")
    lathe(f"{name}MartiniDrink", [(0, 0.104), (0.008, 0.104), (0.048, 0.157), (0, 0.157)], PINKD, g, segs=20)
    disc(f"{name}MartiniLime", (0.045, 0.16, 0), 0.016, 0.004, LIME, g, axis="z", verts=16)

    # 2) highball with a cyan drink, ice and a lime straw
    h = _root(f"{name}Highball", root)
    h.location = P(-0.25, 0, 0.0)
    disc(f"{name}HighballBase", (0, 0.003, 0), 0.032, 0.006, GLASSW, h, axis="y", verts=20)
    ring(f"{name}HighballRim", (0, 0.15, 0), 0.034, 0.002, GLASSW, h, axis="y")
    lathe(f"{name}HighballDrink", [(0, 0.006), (0.03, 0.006), (0.0315, 0.125), (0, 0.125)], CYAND, h, segs=20)
    for k, (dx, dz) in enumerate(((0.008, 0.006), (-0.01, -0.004))):
        block(f"{name}Ice{k}", (dx, 0.13, dz), (0.022, 0.02, 0.022), ICE, h, r=0.004)
    tube(f"{name}Straw", [(0.01, 0.03, 0.0), (0.03, 0.2, 0.012)], 0.004, STRAW, h)

    # 3) rocks glass with an amber drink and one big ice cube
    rk = _root(f"{name}Rocks", root)
    rk.location = P(0.05, 0, 0.08)
    disc(f"{name}RocksBase", (0, 0.004, 0), 0.04, 0.008, GLASSW, rk, axis="y", verts=20)
    ring(f"{name}RocksRim", (0, 0.085, 0), 0.042, 0.002, GLASSW, rk, axis="y")
    lathe(f"{name}RocksDrink", [(0, 0.008), (0.038, 0.008), (0.039, 0.05), (0, 0.05)], AMBERD, rk, segs=20)
    block(f"{name}RocksIce", (0, 0.055, 0), (0.042, 0.04, 0.042), ICE, rk, r=0.006)

    # 4) chrome cocktail shaker
    sh = _root(f"{name}Shaker", root)
    sh.location = P(0.32, 0, -0.08)
    lathe(f"{name}ShakerBody", [(0, 0), (0.036, 0), (0.042, 0.15), (0.03, 0.19), (0.018, 0.215), (0.018, 0.24), (0, 0.245)], CHROME, sh)

    # 5) three cans (plain neon colours, no branding), one lying on its side
    for k, (x, z, col) in enumerate(((0.62, 0.0, "#b6ff3b"), (0.72, 0.06, "#ff4fd8"), (0.68, -0.08, "#22e4ff"))):
        CAN = mat(f"Can{col[1:]}", col, 0.25, metal=0.7)
        c = _root(f"{name}Can{k}", root)
        c.location = P(x, 0, z)
        lathe(f"{name}CanBody{k}", [(0, 0), (0.028, 0), (0.033, 0.012), (0.033, 0.11), (0.028, 0.122), (0, 0.122)], CAN, c, segs=20)
        lathe(f"{name}CanTop{k}", [(0, 0.12), (0.027, 0.12), (0.027, 0.124), (0, 0.124)], CHROME, c, segs=20)
        if k == 2:
            c.rotation_euler = (math.radians(90), 0, math.radians(30))
            c.location = P(x, 0.033, z)
    return root


def _bits(name, n, centre, radius, height, size, mats, parent, rng, flat=False, kind="ico"):
    """Heap n little pieces in a dome over a bowl: popcorn, nuts, chips."""
    objs = []
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi)
        r = radius * math.sqrt(rng.random())
        y = centre[1] + height * (1 - (r / radius) ** 2) * rng.uniform(0.5, 1.0)
        x, z = centre[0] + r * math.cos(a), centre[2] + r * math.sin(a)
        if kind == "ico":
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=size * rng.uniform(0.8, 1.25))
        else:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=size * rng.uniform(0.85, 1.2), depth=size * 0.18)
        o = bpy.context.active_object
        o.location = P(x, y, z)
        o.rotation_euler = (rng.uniform(0, 3.14), rng.uniform(0, 3.14), rng.uniform(0, 3.14))
        if flat:
            o.scale = (1, 1, 0.35) if kind == "ico" else (1, rng.uniform(0.7, 1.0), 1)
        o.name = f"{name}{k}"
        for c in list(o.users_collection):
            c.objects.unlink(o)
        bpy.context.collection.objects.link(o)
        o.data.materials.append(rng.choice(mats))
        o.parent = parent
        objs.append(o)
    return objs


def build_bar_snacks(parent=None, name="BarSnacks", seed=11):
    """Snacks for the counter top (origin at the top surface): a bowl of crisps, a striped
    popcorn bucket, a slate of nachos with cheese and jalapenos, and a small bowl of nuts.
    All original (no packaging or branding)."""
    rng = random.Random(seed)
    BOWL = mat("SnackBowl", "#16151b", 0.35, metal=0.2)
    BOWL_IN = mat("SnackBowlRim", "#d8d2c4", 0.5)
    CRISP = [mat("SnackCrisp", "#e8b448", 0.6), mat("SnackCrispDark", "#d19a32", 0.6)]
    POP = [mat("SnackPopcorn", "#f6eccc", 0.8), mat("SnackPopcornButter", "#f2d98c", 0.8)]
    WHITE = mat("PopBucketWhite", "#f2f0ea", 0.6)
    RED = mat("PopBucketRed", "#d8283c", 0.55)
    SLATE = mat("SnackSlate", "#1d1f24", 0.8)
    CHIP = [mat("SnackNacho", "#eab54a", 0.6), mat("SnackNachoDark", "#d79a36", 0.6)]
    CHEESE = mat("SnackCheese", "#ffa51f", 0.35, emit="#ff9a1a", strength=0.25)
    JALA = mat("SnackJalapeno", "#3f9a3a", 0.5)
    NUT = [mat("SnackNut", "#b07a3e", 0.6), mat("SnackNutDark", "#8a5a2a", 0.6)]
    root = _root(name, parent)

    # 1) bowl of crisps (front left)
    c = _root(f"{name}Crisps", root)
    c.location = P(-0.95, 0, 0.12)
    lathe(f"{name}CrispBowl", [(0, 0), (0.05, 0), (0.09, 0.055), (0.092, 0.06), (0, 0.06)], BOWL, c, segs=28)
    ring(f"{name}CrispRim", (0, 0.06, 0), 0.09, 0.004, BOWL_IN, c, axis="y")
    _bits(f"{name}Crisp", 26, (0, 0.05, 0), 0.082, 0.05, 0.022, CRISP, c, rng, flat=True, kind="disc")

    # 2) striped popcorn bucket (right end), popcorn heaped over the top + a few spilled
    pb = _root(f"{name}Popcorn", root)
    pb.location = P(1.0, 0, -0.05)
    bucket = lathe(f"{name}Bucket", [(0, 0), (0.055, 0), (0.075, 0.18), (0, 0.18)], WHITE, pb, segs=32, smooth=False)
    bucket.data.materials.append(RED)
    for poly in bucket.data.polygons:  # red/white stripes round the sides (not the caps)
        if abs(poly.normal.z) < 0.9:
            c = poly.center
            k = int(((math.atan2(c.y, c.x) + math.pi) / (2 * math.pi)) * 16) % 16
            poly.material_index = 1 if k % 2 == 0 else 0
    _bits(f"{name}Pop", 40, (0, 0.18, 0), 0.07, 0.06, 0.013, POP, pb, rng)
    for k in range(4):
        _bits(f"{name}Spill{k}_", 1, (rng.uniform(-0.14, -0.08), 0.008, rng.uniform(-0.05, 0.08)), 0.001, 0.0, 0.012, POP, pb, rng)

    # 3) slate of nachos with melted cheese and jalapeno slices (front, middle-right)
    nb = _root(f"{name}Nachos", root)
    nb.location = P(0.25, 0, 0.17)
    block(f"{name}Slate", (0, 0.006, 0), (0.3, 0.012, 0.2), SLATE, nb, r=0.004)
    for k in range(16):
        x, z = rng.uniform(-0.1, 0.1), rng.uniform(-0.06, 0.06)
        tri = [(0.0, 0.03, 0.0), (0.026, -0.015, 0.0), (-0.026, -0.015, 0.0)]
        me = bpy.data.meshes.new(f"{name}Nacho{k}")
        me.from_pydata(tri + [(x2, y2, 0.004) for x2, y2, _ in tri], [], [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])
        me.update()
        o = bpy.data.objects.new(f"{name}Nacho{k}", me)
        bpy.context.collection.objects.link(o)
        me.materials.append(rng.choice(CHIP))
        o.location = P(x, 0.016 + rng.uniform(0, 0.03), z)
        o.rotation_euler = (rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), rng.uniform(0, 6.28))
        o.parent = nb
    _bits(f"{name}Cheese", 9, (0, 0.035, 0), 0.08, 0.02, 0.016, [CHEESE], nb, rng, flat=True)
    _bits(f"{name}Jala", 6, (0, 0.045, 0), 0.08, 0.015, 0.011, [JALA], nb, rng, flat=True, kind="disc")

    # 4) small bowl of mixed nuts (beside the cans)
    nu = _root(f"{name}Nuts", root)
    nu.location = P(0.55, 0, 0.18)
    lathe(f"{name}NutBowl", [(0, 0), (0.035, 0), (0.06, 0.04), (0.062, 0.045), (0, 0.045)], BOWL, nu, segs=24)
    ring(f"{name}NutRim", (0, 0.045, 0), 0.06, 0.003, BOWL_IN, nu, axis="y")
    _bits(f"{name}Nut", 22, (0, 0.038, 0), 0.052, 0.03, 0.01, NUT, nu, rng, flat=True)
    return root


def build_bar_preview(parent=None, name="BarPreview"):
    root = _root(name, parent)
    build_back_bar(root, name + "Back").location = P(0, 0, -1.25)
    build_back_bar_drinks(root, name + "BackDrinks").location = P(0, 0, -1.25)
    build_bar_counter(root, name + "Counter")
    build_counter_drinks(root, name + "CounterDrinks").location = P(0, COUNTER_H, 0.05)
    build_bar_snacks(root, name + "Snacks").location = P(0, COUNTER_H, 0.0)
    return root


def build_snacks_preview(parent=None, name="SnacksPreview"):
    """The snacks on their own, 4x size, for a close look."""
    root = _root(name, parent)
    build_bar_snacks(root, name + "S")
    root.scale = (4, 4, 4)
    return root


def build_bar_area(parent=None, name="Bar"):
    root = _root(name, parent)
    back_z = -(COUNTER_D / 2 + 0.85 + 0.2)  # counter back face, a walkway, then the back bar's centre
    build_back_bar(root, name + "Back").location = P(0, 0, back_z)
    build_back_bar_drinks(root, name + "BackDrinks").location = P(0, 0, back_z)
    build_bar_counter(root, name + "Counter")
    build_counter_drinks(root, name + "CounterDrinks").location = P(0, COUNTER_H, 0.05)
    build_bar_snacks(root, name + "Snacks").location = P(0, COUNTER_H, 0.0)
    return root
