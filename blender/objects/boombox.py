"""
Cyberpunk boombox for the loft's lower floor: a black body with two big
speakers ringed in magenta light, a central tape deck under a cyan equaliser
display, a row of piano-key buttons on top, a chrome carry handle and a
telescopic antenna.

    build_boombox(parent=None, name="Boombox") -> root empty

Coordinates are three.js style (Y up, speakers face +Z, origin at the centre
of the base on the floor). Equaliser bars are named "<name>EQ<n>" so the site
could animate them.
"""

import math
import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

BW, BH, BD = 0.62, 0.32, 0.16


def build_boombox(parent=None, name="Boombox"):
    BODY = mat("BoomBody", "#101114", 0.35, metal=0.4)
    TRIM = mat("BoomTrim", "#26282d", 0.3, metal=0.85)
    CHROME = mat("BoomChrome", "#9aa0a6", 0.15, metal=1.0)
    CONE = mat("BoomCone", "#08080a", 0.7)
    GRILLE = mat("BoomGrille", "#1a1b1f", 0.5, metal=0.6)
    MAG = mat("BoomMagenta", "#ff2bd6", emit="#ff2bd6", strength=8.0)
    CYAN = mat("BoomCyan", "#22e4ff", emit="#22e4ff", strength=6.0)
    SCREEN = mat("BoomScreen", "#041014", 0.2)
    TAPE = mat("BoomTapeWindow", "#0a1520", 0.1, emit="#1a4f6a", strength=0.6)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    yc = BH / 2 + 0.02  # body centre (sits on two little feet)
    zf = BD / 2
    block(f"{name}Body", (0, yc, 0), (BW, BH, BD), BODY, root, r=0.025)
    for s in (-1, 1):
        block(f"{name}Foot{s}", (s * (BW / 2 - 0.07), 0.01, 0), (0.08, 0.02, BD - 0.03), TRIM, root, r=0.004)

    # ---------- speakers: cone, chrome surround, magenta light ring, grille bars
    for s in (-1, 1):
        cx = s * 0.19
        disc(f"{name}Cone{s}", (cx, yc - 0.01, zf - 0.005), 0.1, 0.02, CONE, root, axis="z", verts=40)
        disc(f"{name}DustCap{s}", (cx, yc - 0.01, zf + 0.008), 0.03, 0.01, TRIM, root, axis="z", verts=24)
        ring(f"{name}Surround{s}", (cx, yc - 0.01, zf + 0.004), 0.105, 0.01, CHROME, root, axis="z")
        ring(f"{name}SpeakerGlow{s}", (cx, yc - 0.01, zf + 0.002), 0.122, 0.006, MAG, root, axis="z")
        for k in range(5):  # horizontal grille bars across the cone
            y = yc - 0.01 - 0.08 + k * 0.04
            half = math.sqrt(max(0.0, 0.1 ** 2 - (y - yc + 0.01) ** 2))
            if half > 0.02:
                block(f"{name}Grille{s}_{k}", (cx, y, zf + 0.014), (2 * half, 0.006, 0.006), GRILLE, root)
        # small tweeter above each speaker
        disc(f"{name}Tweeter{s}", (s * 0.27, yc + 0.11, zf + 0.002), 0.018, 0.01, TRIM, root, axis="z")

    # ---------- centre: EQ display above a tape deck
    block(f"{name}Display", (0, yc + 0.075, zf + 0.002), (0.15, 0.07, 0.006), SCREEN, root, r=0.003)
    rng = random.Random(4)
    for k in range(8):
        h = rng.uniform(0.012, 0.055)
        block(f"{name}EQ{k}", (-0.06 + k * 0.017, yc + 0.045 + h / 2, zf + 0.006), (0.011, h, 0.003), CYAN, root)
    block(f"{name}TapeDoor", (0, yc - 0.035, zf + 0.002), (0.15, 0.1, 0.008), TRIM, root, r=0.004)
    block(f"{name}TapeWindow", (0, yc - 0.03, zf + 0.007), (0.1, 0.04, 0.003), TAPE, root, r=0.002)
    for s in (-1, 1):
        disc(f"{name}Reel{s}", (s * 0.025, yc - 0.03, zf + 0.009), 0.012, 0.003, CHROME, root, axis="z", verts=12)
    block(f"{name}CenterGlow", (0, yc - 0.105, zf + 0.004), (0.13, 0.006, 0.004), MAG, root)

    # ---------- top: piano-key buttons, volume knob, handle, antenna
    for k in range(6):
        block(f"{name}Key{k}", (-0.07 + k * 0.028, BH + 0.03, 0.02), (0.022, 0.016, 0.05), CHROME if k != 2 else MAG, root, r=0.003)
    disc(f"{name}Knob", (0.16, BH + 0.032, 0.02), 0.022, 0.02, TRIM, root)
    ring(f"{name}KnobGlow", (0.16, BH + 0.043, 0.02), 0.022, 0.003, CYAN, root)
    tube(f"{name}Handle", [(-0.24, BH + 0.02, -0.03), (-0.22, BH + 0.1, -0.03), (0.22, BH + 0.1, -0.03), (0.24, BH + 0.02, -0.03)], 0.012, CHROME, root)
    tube(f"{name}Antenna", [(-0.27, BH + 0.02, -0.05), (-0.36, BH + 0.42, -0.08)], 0.004, CHROME, root)
    disc(f"{name}AntennaTip", (-0.362, BH + 0.425, -0.081), 0.008, 0.012, CHROME, root)

    # preview-only magenta glow on the floor (lights aren't exported)
    ld = bpy.data.lights.new(f"{name}GlowLight", "POINT")
    ld.color = (1.0, 0.17, 0.84)
    ld.energy = 6
    ld.shadow_soft_size = 0.2
    lo = bpy.data.objects.new(f"{name}GlowLight", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = P(0, yc, zf + 0.25)
    lo.parent = root
    return root
