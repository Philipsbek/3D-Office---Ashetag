"""
Upright arcade cabinet for the loft's Lab zone: coloured side panels with a
proper cabinet silhouette, glowing neon edge trim, a lit marquee with 3D text,
a slanted screen in a black bezel, a control deck with joystick and glowing
buttons, and a coin door with lit slots.

    build_arcade_cabinet(parent=None, name="ArcadeCabinet", body="#1d3fae",
                         glow="#38b6ff", marquee="WHAT I BUILD",
                         screen_name="ArcadeScreen", seed=1) -> root empty
    build_arcade_pair(parent=None, name="ArcadePair") -> the blue + red pair

Coordinates are three.js style (Y up, the player stands at +Z, origin at the
centre of the base). The screen is a plane named `screen_name` with 0..1 UVs
(aspect 1.3:1), so the website can put the live game on it.
"""

import math
import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, _hex  # noqa: E402
from gaming_desk import disc, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

W = 0.74  # cabinet width
SIDE_T = 0.025  # side panel thickness

# side silhouette in (z, y): z forward (player side), y up
PROFILE = [
    (-0.42, 0.0), (0.36, 0.0), (0.36, 0.80),       # back, floor, kick panel
    (0.54, 0.88), (0.50, 0.98),                    # control deck nose
    (0.27, 1.03),                                  # back of the deck
    (0.17, 1.55),                                  # top of the screen (leans back)
    (0.38, 1.60), (0.38, 1.90), (-0.42, 1.90),     # marquee box, roof
]
SCREEN_BOTTOM, SCREEN_TOP = PROFILE[5], PROFILE[6]
DECK_FRONT, DECK_BACK = PROFILE[4], PROFILE[5]


def prism(name, profile, x0, x1, m, parent):
    """Extrude a (z, y) silhouette across x0..x1 into a closed solid."""
    n = len(profile)
    verts = [P(x, y, z) for x in (x0, x1) for (z, y) in profile]
    faces = [list(range(n))[::-1], list(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    # make sure normals point outwards whatever the winding
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    o.data.materials.append(m)
    o.parent = parent
    return o


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _attract_image(name, seed, palette):
    """A little 'attract mode' picture for the preview (the site replaces it live)."""
    img = bpy.data.images.get(name)
    if img:
        return img
    w, h = 130, 100
    img = bpy.data.images.new(name, w, h)
    rng = random.Random(seed)
    px = [0.0] * (w * h * 4)
    bg = (0.01, 0.01, 0.03)
    for i in range(w * h):
        px[i * 4:i * 4 + 4] = (*bg, 1)
    for _ in range(26):  # falling blocks
        bx, by = rng.randrange(4, w - 10), rng.randrange(18, h - 8)
        c = _hex(rng.choice(palette))
        for y in range(by, by + 6):
            for x in range(bx, bx + 6):
                px[(y * w + x) * 4:(y * w + x) * 4 + 4] = (*c, 1)
    paddle = _hex(palette[0])
    for y in range(6, 10):  # the catcher paddle
        for x in range(50, 80):
            px[(y * w + x) * 4:(y * w + x) * 4 + 4] = (*paddle, 1)
    img.pixels = px
    img.pack()
    return img


def _emissive_image_mat(name, img, strength=1.6):
    m = bpy.data.materials.get("Arcade_" + name)
    if m:
        return m
    m = bpy.data.materials.new("Arcade_" + name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"  # crisp pixels
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    return m


def _text(name, body, c, height, m, parent, max_width):
    """Flat 3D text facing +Z, centred on c, scaled to fit max_width."""
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    t.data.body = body
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.extrude = 0.004
    t.data.size = height
    bpy.context.view_layer.update()
    if t.dimensions.x > max_width:
        t.data.size = height * max_width / t.dimensions.x
    t.rotation_euler = (math.pi / 2, 0, 0)
    t.location = P(*c)
    t.data.materials.append(m)
    bpy.ops.object.convert(target="MESH")
    t = bpy.context.active_object
    t.name = name
    t.parent = parent
    return t


def build_arcade_cabinet(parent=None, name="ArcadeCabinet", body="#1d3fae", glow="#38b6ff",
                         marquee="WHAT I BUILD", screen_name="ArcadeScreen", seed=1):
    key = name
    SIDE = mat(f"ArcadeSide_{body}", body, 0.45)
    BLACK = mat("ArcadeBlack", "#0b0b0d", 0.55)
    BEZEL = mat("ArcadeBezel", "#050506", 0.3)
    METAL = mat("ArcadeMetal", "#55585c", 0.3, metal=0.9)
    NEON = mat(f"ArcadeNeon_{glow}", glow, emit=glow, strength=7.0)
    MARQ = mat(f"ArcadeMarquee_{glow}", body, emit=glow, strength=1.2)
    MARQ_TXT = mat("ArcadeMarqueeText", "#ffffff", emit="#ffffff", strength=5.0)
    SLOT = mat("ArcadeCoinSlot", "#ff8a1a", emit="#ff8a1a", strength=6.0)
    STRIPE = mat(f"ArcadeStripe_{glow}", glow, 0.4)
    btn_cols = ["#ff2e3e", "#ffd21a", "#2ee86a", "#2a8cff", "#ffffff", "#ff2e3e"]
    BTN = [mat(f"ArcadeBtn_{c}", c, 0.3, emit=c, strength=2.5) for c in btn_cols]

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # body: black core + coloured side panels slightly proud of it
    prism(f"{key}Core", PROFILE, -W / 2 + SIDE_T, W / 2 - SIDE_T, BLACK, root)
    for s, sx in enumerate((-1, 1)):
        x0 = sx * W / 2 - (SIDE_T if sx > 0 else 0)
        prism(f"{key}Side{s}", PROFILE, x0, x0 + SIDE_T, SIDE, root)
        # neon trim along the front edge of each side panel
        front = PROFILE[1:9]
        tube(f"{key}EdgeNeon{s}", [(sx * (W / 2 + 0.004), y, z + 0.004) for (z, y) in front], 0.007, NEON, root)
        # side art: three diagonal stripes
        for k in range(3):
            st = block(f"{key}SideStripe{s}_{k}", (sx * (W / 2 + 0.002), 0.55 + k * 0.12, -0.05), (0.004, 0.045, 0.75), STRIPE, root)
            st.rotation_euler = (math.radians(-28), 0, 0)

    # kick panel: coin door with lit slots, and a dark plinth
    block(f"{key}Plinth", (0, 0.04, 0.37), (W - 0.02, 0.08, 0.02), METAL, root)
    block(f"{key}CoinDoor", (0, 0.45, 0.365), (0.3, 0.34, 0.015), BLACK, root, r=0.004)
    # asymmetric like a real coin door: two coin mechs stacked on the left,
    # a tall coin-return flap on the right
    for k, cy in enumerate((0.535, 0.395)):
        block(f"{key}CoinPlate{k}", (-0.06, cy, 0.376), (0.12, 0.1, 0.012), METAL, root, r=0.004)
        block(f"{key}CoinSlot{k}", (-0.085, cy + 0.01, 0.383), (0.006, 0.045, 0.004), SLOT, root)
        block(f"{key}CoinPrice{k}", (-0.035, cy + 0.01, 0.383), (0.03, 0.018, 0.004), BLACK, root)
    block(f"{key}CoinReturn", (0.08, 0.45, 0.376), (0.07, 0.24, 0.014), METAL, root, r=0.004)
    block(f"{key}CoinReturnLip", (0.08, 0.36, 0.384), (0.05, 0.008, 0.004), BLACK, root)

    # control deck: joystick + 6 buttons + 2 start buttons, sitting on the deck slope
    dz0, dy0 = DECK_FRONT
    dz1, dy1 = DECK_BACK
    tilt = math.atan2(dy1 - dy0, dz0 - dz1)  # deck rises toward the screen

    def on_deck(x, t, lift):
        z, y = _lerp(DECK_FRONT, DECK_BACK, t)
        return (x, y + lift, z)

    stick = on_deck(-0.2, 0.5, 0.0)
    tube(f"{key}StickShaft", [stick, (stick[0], stick[1] + 0.08, stick[2])], 0.008, METAL, root)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.026, segments=20, ring_count=10)
    ball = bpy.context.active_object
    ball.name = f"{key}StickBall"
    ball.location = P(stick[0], stick[1] + 0.09, stick[2])
    bpy.ops.object.shade_smooth()
    ball.data.materials.append(BTN[0])
    ball.parent = root
    disc(f"{key}StickBase", (stick[0], stick[1] + 0.004, stick[2]), 0.035, 0.008, BLACK, root)
    for k in range(6):
        col, row = k % 3, k // 3
        x = 0.0 + col * 0.075
        t = 0.32 + row * 0.33
        c = on_deck(x, t, 0.008)
        b = disc(f"{key}Button{k}", c, 0.021, 0.016, BTN[k], root)
        b.rotation_euler = (tilt, 0, 0)
    for k, x in enumerate((0.25, 0.3)):
        b = disc(f"{key}Start{k}", on_deck(x, 0.75, 0.006), 0.012, 0.012, BTN[4], root)
        b.rotation_euler = (tilt, 0, 0)

    # screen: black bezel face + the screen plane, both on the slanted front
    (sz0, sy0), (sz1, sy1) = SCREEN_BOTTOM, SCREEN_TOP
    lean = math.atan2(sz0 - sz1, sy1 - sy0)  # leans back from vertical
    mid = ((sz0 + sz1) / 2, (sy0 + sy1) / 2)
    slope_len = math.hypot(sz0 - sz1, sy1 - sy0)
    nz, ny = math.cos(lean), math.sin(lean)  # outward normal in (z, y)
    bez = block(f"{key}Bezel", (0, mid[1] + ny * 0.004, mid[0] + nz * 0.004), (W - 2 * SIDE_T, slope_len, 0.008), BEZEL, root)
    bez.rotation_euler = (-lean, 0, 0)
    bpy.ops.mesh.primitive_plane_add(size=1)
    scr = bpy.context.active_object
    scr.name = screen_name
    scr.scale = (0.56, 0.43, 1)
    scr.location = P(0, mid[1] + ny * 0.0095, mid[0] + nz * 0.0095)
    scr.rotation_euler = (math.pi / 2 - lean, 0, 0)
    palette = [glow, "#ff2e3e", "#ffd21a", "#2ee86a", "#c77dff"]
    scr.data.materials.append(_emissive_image_mat(f"Attract_{screen_name}", _attract_image(f"Attract_{screen_name}", seed, palette)))
    scr.parent = root
    # glowing frame around the screen
    for k, (dx, dy, sx_, sy_) in enumerate(((0, 0.225, 0.6, 0.008), (0, -0.225, 0.6, 0.008), (-0.3, 0, 0.008, 0.458), (0.3, 0, 0.008, 0.458))):
        fr = block(f"{key}ScreenGlow{k}", (dx, mid[1] + dy * math.cos(lean) + ny * 0.011, mid[0] - dy * math.sin(lean) + nz * 0.011), (sx_, sy_, 0.004), NEON, root)
        fr.rotation_euler = (-lean, 0, 0)

    # marquee: lit panel + white 3D text
    mz = PROFILE[7][0]
    my = (PROFILE[7][1] + PROFILE[8][1]) / 2
    block(f"{key}MarqueePanel", (0, my, mz + 0.004), (W - 2 * SIDE_T, 0.26, 0.008), MARQ, root)
    if marquee:
        _text(f"{key}MarqueeText", marquee, (0, my, mz + 0.012), 0.11, MARQ_TXT, root, max_width=W - 0.16)
    else:
        # no title: three retro stripes across the lit panel
        for k, (dy, h) in enumerate(((0.06, 0.03), (0.0, 0.03), (-0.06, 0.03))):
            block(f"{key}MarqueeStripe{k}", (0, my + dy, mz + 0.01), (W - 0.16 - k * 0.12, h, 0.004), MARQ_TXT, root)
    # speaker grilles under the marquee overhang
    for k, x in enumerate((-0.2, 0.2)):
        disc(f"{key}Speaker{k}", (x, 1.575, 0.3), 0.04, 0.01, BLACK, root, axis="y")

    return root


def build_arcade_pair(parent=None, name="ArcadePair"):
    """The two cabinets as they'll stand in the Lab: playable blue + decorative red (striped, no title)."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    a = build_arcade_cabinet(root, name=f"{name}Blue", body="#1d3fae", glow="#38b6ff",
                             marquee="WHAT I BUILD", screen_name="ArcadeScreen", seed=1)
    a.location = P(-0.42, 0, 0)
    b = build_arcade_cabinet(root, name=f"{name}Red", body="#9e1622", glow="#ff3a4a",
                             marquee="", screen_name="ArcadeScreen2", seed=5)
    b.location = P(0.42, 0, 0)
    return root
