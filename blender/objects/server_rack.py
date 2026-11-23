"""
Cyberpunk server racks: tall black 42U cabinets with a tinted glass door in a
steel frame, stacked servers covered in status LEDs (green / cyan / amber),
a patch panel with colourful cables, top vents, castor feet and a cyan light
strip down the front edge.

    build_server_rack(parent=None, name="ServerRack", seed=1) -> root empty
    build_server_rack_pair(parent=None, name="ServerRacks") -> two racks side by side

Coordinates are three.js style (Y up, the door faces +Z, origin at the centre
of the base on the floor). All LEDs of a rack are merged into one mesh.
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
from gaming_desk import disc, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402
from bookshelf import _join  # noqa: E402
from glass_room import glass_mat  # noqa: E402

W, H, D = 0.62, 2.0, 0.95


def build_server_rack(parent=None, name="ServerRack", seed=1):
    BODY = mat("RackBody", "#0c0d10", 0.4, metal=0.6)
    FRAME = mat("RackFrame", "#24262b", 0.3, metal=0.9)
    UNIT = mat("RackUnit", "#17181c", 0.35, metal=0.7)
    UNIT2 = mat("RackUnitAlt", "#1e2026", 0.35, metal=0.7)
    VENT = mat("RackVent", "#050506", 0.6)
    CYAN = mat("RackCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    LEDS = [mat("RackLEDGreen", "#2bff7a", emit="#2bff7a", strength=8.0),
            mat("RackLEDCyan", "#22e4ff", emit="#22e4ff", strength=8.0),
            mat("RackLEDAmber", "#ffb020", emit="#ffb020", strength=8.0)]
    CABLES = [mat(f"RackCable_{c}", c, 0.5) for c in ("#1f6fd0", "#d02b8a", "#2bbf6a", "#d0a02b")]
    GLASS = glass_mat("RackDoor", "#5a7a99", 0.22)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    rng = random.Random(seed)

    base = 0.08
    zf = D / 2
    # ---------- cabinet shell (open front) on castors
    block(f"{name}Back", (0, base + H / 2, -D / 2 + 0.02), (W, H, 0.04), BODY, root)
    for s in (-1, 1):
        block(f"{name}Side{s}", (s * (W / 2 - 0.02), base + H / 2, 0), (0.04, H, D), BODY, root, r=0.004)
    block(f"{name}Top", (0, base + H - 0.02, 0), (W, 0.04, D), BODY, root, r=0.004)
    block(f"{name}Bottom", (0, base + 0.02, 0), (W, 0.04, D), BODY, root)
    for k in range(5):  # top vent slots
        block(f"{name}TopVent{k}", (0, base + H + 0.001, -0.3 + k * 0.15), (W - 0.16, 0.004, 0.04), VENT, root)
    for k, (sx, sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        disc(f"{name}Castor{k}", (sx * (W / 2 - 0.07), 0.04, sz * (D / 2 - 0.08)), 0.035, 0.03, FRAME, root, axis="x")

    # ---------- servers: units of 1-4U with LED rows; a patch panel with cables
    u = (H - 0.12) / 42
    y = base + 0.06
    leds = []
    k = 0
    while y < base + H - 0.1:
        size = rng.choice((1, 1, 2, 2, 3, 4))
        hgt = size * u
        if y + hgt > base + H - 0.08:
            break
        kind = rng.random()
        if k == 6:  # patch panel with cables looping down
            block(f"{name}Patch", (0, y + u / 2, zf - 0.1), (W - 0.1, u * 0.9, 0.04), UNIT2, root)
            for c in range(12):
                x = -W / 2 + 0.08 + c * (W - 0.16) / 11
                m = CABLES[c % 4]
                tube(f"{name}PatchCable{c}", [(x, y + u / 2, zf - 0.07), (x, y - 0.03, zf - 0.04), (x * 0.6, y - 0.12, zf - 0.05)], 0.005, m, root)
            y += u + 0.01
            k += 1
            continue
        block(f"{name}Unit{k}", (0, y + hgt / 2, zf - 0.12), (W - 0.1, hgt - 0.006, 0.05), UNIT if kind < 0.6 else UNIT2, root)
        # LEDs: a row on the left + drive bays on taller units
        for i in range(rng.randint(2, 6)):
            leds.append(block(f"{name}LED{k}_{i}", (-W / 2 + 0.09 + i * 0.022, y + hgt / 2, zf - 0.094), (0.009, 0.009, 0.004), rng.choice(LEDS), None))
        if size >= 2:
            for i in range(rng.randint(3, 8)):
                leds.append(block(f"{name}Bay{k}_{i}", (0.02 + i * 0.03, y + hgt / 2, zf - 0.094), (0.018, hgt * 0.55, 0.003), LEDS[1] if rng.random() < 0.3 else UNIT2, None))
        y += hgt
        k += 1
    if leds:
        _join(leds, f"{name}LEDs", root)

    # ---------- glass door in a steel frame + handle, cyan edge strip
    block(f"{name}DoorGlass", (0, base + H / 2, zf - 0.01), (W - 0.08, H - 0.1, 0.01), GLASS, root)
    for k, (x, yy, w, h) in enumerate(((0, base + H - 0.04, W, 0.04), (0, base + 0.04, W, 0.04), (-W / 2 + 0.02, base + H / 2, 0.04, H), (W / 2 - 0.02, base + H / 2, 0.04, H))):
        block(f"{name}DoorFrame{k}", (x, yy, zf - 0.008), (w, h, 0.03), FRAME, root)
    tube(f"{name}Handle", [(W / 2 - 0.06, base + H / 2 - 0.2, zf + 0.02), (W / 2 - 0.06, base + H / 2 + 0.2, zf + 0.02)], 0.01, FRAME, root)
    block(f"{name}EdgeGlow", (-W / 2 + 0.002, base + H / 2, zf + 0.004), (0.01, H - 0.1, 0.01), CYAN, root)
    block(f"{name}TopGlow", (0, base + H - 0.075, zf + 0.008), (W - 0.12, 0.012, 0.006), CYAN, root)

    # preview-only glow (lights aren't exported)
    ld = bpy.data.lights.new(f"{name}GlowLight", "POINT")
    ld.color = (0.2, 0.9, 1.0)
    ld.energy = 12
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new(f"{name}GlowLight", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = P(W * 0.9, base + 0.3, zf + 0.5)  # low and to the side: no reflections on the glass
    lo.parent = root
    return root


def build_server_rack_pair(parent=None, name="ServerRacks"):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    for k, (x, seed) in enumerate(((-W / 2 - 0.01, 1), (W / 2 + 0.01, 5))):
        r = build_server_rack(root, f"{name}{k}", seed=seed)
        r.location = P(x, 0, 0)
    return root
