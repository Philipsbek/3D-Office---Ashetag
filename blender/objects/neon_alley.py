"""
Neon courtyard block (style ref supplied by the user: an isometric night block of
two buildings round a small yard). Original model built here; the sign texts
and the car are our own (no real brands).

Left: a two-storey garage/showroom with a big cyan neon "NEON MOTORS" sign and a
pink script line, lit blinds windows, a pink neon arrow by the door and an open
garage bay. Right: a taller three-storey building with roof AC units, a vertical
pink-red "HOTEL" sign, a wide cyan-lit shuttered window band, warm windows above,
a "Bar" neon and lit door on the ground floor. Between them: a wet asphalt yard
with the approved supercar parked (cyan underglow), a utility pole with a
tangle of cables, rusty barrels, a crowd-control fence, trash and puddles, all on
a raised square base.

    build_neon_alley(parent=None, name="NeonAlley") -> root; base 16 x 16 m.
    build_neon_alley_preview(parent, name)

Coordinates are three.js style (Y up); the yard opens toward +X/+Z.
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
from loft_room import block, mat, slab  # noqa: E402
from ramen_corner import _ac_unit, _sag_cable, _text  # noqa: E402


def _mats():
    return {
        "base": mat("NaBase", "#2a2830", 0.85),
        "asphalt": mat("NaAsphalt", "#1c1b22", 0.25),  # wet
        "puddle": mat("NaPuddle", "#0c0c12", 0.02, metal=0.3),
        "wallL": mat("NaWallLeft", "#6e5a66", 0.85),
        "wallR": mat("NaWallRight", "#5d5664", 0.85),
        "trim": mat("NaTrim", "#2c2a33", 0.6),
        "metal": mat("NaMetal", "#3a3d44", 0.4, metal=0.7),
        "black": mat("RcBlack", "#121317", 0.4),
        "white": mat("RcWhite", "#e6e6ea", 0.5),
        "rust": mat("NaRust", "#7a3c1e", 0.7, metal=0.3),
        "rustDark": mat("NaRustDark", "#4a2414", 0.8),
        "fence": mat("NaFence", "#9aa0aa", 0.35, metal=0.8),
        "trash": mat("NaTrash", "#d8d8dc", 0.7),
        "warm": mat("RcWarmGlow", "#ffd2a0", emit="#ffb070", strength=3.0),
        "blinds": mat("NaBlinds", "#c8f6ff", emit="#9eefff", strength=3.5),
        "cyan": mat("NaNeonCyan", "#22e4ff", emit="#22e4ff", strength=10.0),
        "pink": mat("NaNeonPink", "#ff4fb0", emit="#ff4fb0", strength=10.0),
        "red": mat("NaNeonRed", "#ff3048", emit="#ff3048", strength=10.0),
        "signBox": mat("NaSignBox", "#1a1820", 0.5),
        "doorRed": mat("NaDoorRed", "#5a1820", 0.6),
    }


def _windows_row(name, x0, x1, y, h, z, n, M, root, lit=True, face="z", blinds=True):
    """A row of n framed windows on a +Z (or +X) facing wall."""
    span = (x1 - x0) / n
    for k in range(n):
        a = x0 + span * (k + 0.18)
        b = x0 + span * (k + 0.82)
        if face == "z":
            slab(f"{name}Frame{k}", a - 0.08, b + 0.08, y - 0.08, y + h + 0.08, z, z + 0.08, M["trim"], root)
            slab(f"{name}Pane{k}", a, b, y, y + h, z + 0.08, z + 0.1, M["blinds" if blinds else "warm"] if lit else M["black"], root)
            if blinds and lit:
                for j in range(int(h / 0.18)):
                    slab(f"{name}Slat{k}_{j}", a, b, y + 0.09 + j * 0.18, y + 0.11 + j * 0.18, z + 0.1, z + 0.12, M["trim"], root)
        else:
            slab(f"{name}Frame{k}", z, z + 0.08, y - 0.08, y + h + 0.08, a - 0.08, b + 0.08, M["trim"], root)
            slab(f"{name}Pane{k}", z + 0.08, z + 0.1, y, y + h, a, b, M["blinds" if blinds else "warm"] if lit else M["black"], root)


def build_neon_alley(parent=None, name="NeonAlley", seed=6):
    import city_cars

    M = _mats()
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------------------------------------------------------------- base + yard
    slab(f"{name}Base", -8, 8, -0.8, 0.0, -8, 8, M["base"], root)
    slab(f"{name}Yard", -2.2, 7.8, 0.0, 0.03, -1.0, 7.8, M["asphalt"], root)
    for k in range(7):
        x, z, r = rng.uniform(-1.5, 7), rng.uniform(0, 7.5), rng.uniform(0.4, 1.1)
        disc(f"{name}Puddle{k}", (x, 0.035, z), r, 0.005, M["puddle"], root, verts=20)
    for k in range(14):
        x, z = rng.uniform(-1.5, 7.5), rng.uniform(0, 7.5)
        b = block(f"{name}Trash{k}", (x, 0.06, z), (rng.uniform(0.15, 0.4), 0.05, rng.uniform(0.1, 0.3)), M["trash"], root)
        b.rotation_euler = (0, 0, rng.uniform(0, math.pi))

    # ---------------------------------------------------------------- left building: NEON MOTORS
    L0, L1, LZ0, LZ1, LH = -8.0, -2.2, -8.0, 7.8, 7.4
    slab(f"{name}LMass", L0, L1, 0, LH, LZ0, LZ1, M["wallL"], root)
    slab(f"{name}LParapet", L0 - 0.1, L1 + 0.1, LH, LH + 0.4, LZ0 - 0.1, LZ1 + 0.1, M["trim"], root)
    slab(f"{name}LBelt", L1, L1 + 0.12, 3.5, 3.7, LZ0, LZ1, M["trim"], root)
    # garage bay on the yard side (+X face): dark opening with a lit interior strip
    slab(f"{name}Bay", L1 - 0.02, L1 + 0.02, 0.0, 3.0, 1.0, 5.6, M["black"], root)
    slab(f"{name}BayLight", L1 - 0.05, L1 - 0.03, 2.75, 2.85, 1.2, 5.4, M["cyan"], root)
    slab(f"{name}BayLintel", L1, L1 + 0.15, 3.0, 3.25, 0.8, 5.8, M["trim"], root)
    # big sign on the +X face upper floor: NEON MOTORS in cyan + pink script line
    slab(f"{name}SignBack", L1 + 0.02, L1 + 0.12, 4.2, 6.9, -2.8, 3.8, M["signBox"], root)
    _text(f"{name}SignTop", "NEON", (L1 + 0.16, 6.15, 0.5), 1.05, M["cyan"], root, rot=(math.pi / 2, 0, math.pi / 2), jp=False, depth=0.06)
    _text(f"{name}SignMid", "MOTORS", (L1 + 0.16, 5.05, 0.5), 1.05, M["cyan"], root, rot=(math.pi / 2, 0, math.pi / 2), jp=False, depth=0.06)
    _text(f"{name}SignScript", "night service", (L1 + 0.16, 4.45, 2.5), 0.38, M["pink"], root, rot=(math.pi / 2, 0, math.pi / 2), jp=False, depth=0.03)
    # windows: lit blinds on the front (+Z) face, both floors; one on the yard side
    _windows_row(f"{name}LWinUp", L0 + 0.4, L1 - 0.4, 4.4, 1.6, LZ1, 2, M, root)
    _windows_row(f"{name}LWinLow", L0 + 0.4, L1 - 0.4, 1.1, 1.5, LZ1, 2, M, root, blinds=False)
    _windows_row(f"{name}LWinSide", -6.6, -4.8, 4.4, 1.6, L1 + 0.01, 1, M, root, face="x")
    # pink neon arrow by the bay
    tube(f"{name}Arrow", [(L1 + 0.15, 2.2, 6.4), (L1 + 0.15, 2.2, 7.3), (L1 + 0.15, 2.5, 7.0), (L1 + 0.15, 2.2, 7.3), (L1 + 0.15, 1.9, 7.0)], 0.05, M["pink"], root)
    # roof clutter
    _ac_unit(f"{name}LAC0", (-5.5, LH + 0.8, -5.0), M, root)
    slab(f"{name}LHatch", -7.0, -6.0, LH + 0.4, LH + 1.0, 2.0, 3.2, M["trim"], root)

    # ---------------------------------------------------------------- right building: HOTEL
    R0, R1, RZ0, RZ1, RH = 0.6, 8.0, -8.0, -1.0, 10.4
    slab(f"{name}RMass", R0, R1, 0, RH, RZ0, RZ1, M["wallR"], root)
    slab(f"{name}RParapet", R0 - 0.1, R1 + 0.1, RH, RH + 0.45, RZ0 - 0.1, RZ1 + 0.1, M["trim"], root)
    for k, y in enumerate((3.4, 6.9)):
        slab(f"{name}RBelt{k}", R0 - 0.06, R1 + 0.06, y, y + 0.18, RZ1, RZ1 + 0.12, M["trim"], root)
    # wide cyan-lit shuttered window band on the 2nd floor (+Z face)
    slab(f"{name}ShutterBack", R0 + 1.4, R1 - 0.5, 3.9, 6.5, RZ1, RZ1 + 0.06, M["blinds"], root)
    for j in range(14):
        y = 4.0 + j * 0.18
        slab(f"{name}Shutter{j}", R0 + 1.4, R1 - 0.5, y, y + 0.06, RZ1 + 0.06, RZ1 + 0.1, M["trim"], root)
    slab(f"{name}ShutterBox", R0 + 1.3, R1 - 0.4, 6.5, 6.8, RZ1, RZ1 + 0.35, M["metal"], root)
    # warm windows on the top floor
    _windows_row(f"{name}RWinTop", R0 + 1.4, R1 - 0.4, 7.6, 1.7, RZ1, 3, M, root, blinds=False)
    # ground floor: lit cyan window, red door, Bar neon
    slab(f"{name}RShopWin", R0 + 1.6, R0 + 3.6, 0.9, 2.7, RZ1, RZ1 + 0.06, M["blinds"], root)
    slab(f"{name}RDoor", R1 - 2.6, R1 - 1.4, 0.0, 2.5, RZ1, RZ1 + 0.06, M["doorRed"], root)
    slab(f"{name}RDoorFrame", R1 - 2.7, R1 - 1.3, 2.5, 2.65, RZ1, RZ1 + 0.1, M["trim"], root)
    _text(f"{name}BarNeon", "Bar", (R1 - 2.0, 3.0, RZ1 + 0.1), 0.5, M["pink"], root, jp=False, depth=0.03)
    # vertical HOTEL sign on the left edge of the face
    slab(f"{name}VSign", R0 - 0.2, R0 + 0.8, 3.6, 9.4, RZ1 + 0.25, RZ1 + 0.55, M["signBox"], root)
    for i, ch in enumerate("HOTEL"):
        _text(f"{name}VSignChar{i}", ch, (R0 + 0.3, 8.7 - i * 1.12, RZ1 + 0.58), 0.95, M["red"], root, jp=False, depth=0.05)
    slab(f"{name}VSignEdge", R0 - 0.22, R0 + 0.82, 9.4, 9.5, RZ1 + 0.23, RZ1 + 0.57, M["red"], root)
    # yard-side face (-X) of the right block: a lit window and a fire-escape ladder
    _windows_row(f"{name}RWinSide", -6.5, -3.0, 4.2, 1.6, R0 - 0.09, 1, M, root, face="x", blinds=False)
    for k in range(10):
        slab(f"{name}Ladder{k}", R0 - 0.35, R0 - 0.3, 0.6 + k * 0.6, 0.65 + k * 0.6, -6.0, -5.2, M["metal"], root)
    for k, z in enumerate((-6.0, -5.2)):
        slab(f"{name}LadderRail{k}", R0 - 0.36, R0 - 0.3, 0.3, 6.6, z - 0.03, z + 0.03, M["metal"], root)
    # roof: AC units, a dish, a vent stack
    _ac_unit(f"{name}RAC0", (2.4, RH + 0.85, -6.0), M, root)
    _ac_unit(f"{name}RAC1", (4.0, RH + 0.85, -6.0), M, root)
    _ac_unit(f"{name}RAC2", (6.2, RH + 0.85, -3.5), M, root)
    disc(f"{name}VentStack", (2.0, RH + 0.9, -2.6), 0.45, 1.0, M["metal"], root, verts=20)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, segments=20, ring_count=10, location=P(6.6, RH + 1.0, -6.6))
    dish = bpy.context.active_object
    dish.name = f"{name}Dish"
    dish.scale = (1.0, 0.35, 1.0)
    dish.rotation_euler = (math.radians(30), 0, math.radians(-30))
    dish.data.materials.append(M["white"])
    dish.parent = root

    # ---------------------------------------------------------------- yard: car, pole, cables, barrels, fence
    car = city_cars.build_street_car(root, f"{name}Car", "#8a8e98")
    car.location = P(0.4, 0.03, 3.4)
    car.rotation_euler = (0, 0, math.radians(-90))  # nose toward +Z (out of the yard)
    slab(f"{name}CarGlow", -0.6, 1.4, 0.04, 0.05, 1.2, 5.6, M["cyan"], root)  # underglow pool
    px, pz = 2.8, 1.2
    disc(f"{name}Pole", (px, 4.6, pz), 0.14, 9.2, M["rustDark"], root, verts=12)
    for k, (dy, w) in enumerate(((8.6, 2.4), (7.9, 1.8))):
        slab(f"{name}Cross{k}", px - w / 2, px + w / 2, dy, dy + 0.14, pz - 0.07, pz + 0.07, M["rustDark"], root)
    for k, dx in enumerate((-1.1, -0.4, 0.4, 1.1)):
        disc(f"{name}Insulator{k}", (px + dx, 8.95, pz), 0.1, 0.3, M["white"], root, verts=10)
    disc(f"{name}Transformer", (px - 0.45, 7.0, pz + 0.2), 0.35, 1.0, M["metal"], root, verts=16)
    targets = [(L1 + 0.1, 6.8, -1.5), (L1 + 0.1, 6.2, 4.0), (R0, 9.6, RZ1), (R0 + 3, 8.2, RZ1), (8.6, 6.5, 6.5), (L1 + 0.1, 5.2, -4.5), (R1, 7.8, RZ1 + 0.2)]
    starts = [(px - 1.1, 9.0, pz), (px - 0.4, 9.0, pz), (px + 0.4, 9.0, pz), (px + 1.1, 9.0, pz), (px + 1.1, 9.0, pz), (px - 1.1, 8.3, pz), (px + 0.9, 8.3, pz)]
    for k, (a, b) in enumerate(zip(starts, targets)):
        _sag_cable(f"{name}Cable{k}", a, b, rng.uniform(0.4, 1.0), M, root, r=0.022)
    for k, (x, z) in enumerate(((4.6, 6.9), (5.4, 6.6), (4.9, 7.4))):
        disc(f"{name}Barrel{k}", (x, 0.5, z), 0.33, 1.0, M["rust" if k % 2 else "rustDark"], root, verts=20)
        for j, y in enumerate((0.25, 0.75)):
            disc(f"{name}BarrelRing{k}{j}", (x, y, z), 0.345, 0.06, M["rustDark"], root, verts=20)
    for k in range(3):  # crowd-control fence along the right edge of the yard
        x0 = 4.2 + k * 1.2
        tube(f"{name}FenceTop{k}", [(x0, 1.0, 1.0), (x0 + 1.1, 1.0, 1.0)], 0.03, M["fence"], root)
        tube(f"{name}FenceBot{k}", [(x0, 0.25, 1.0), (x0 + 1.1, 0.25, 1.0)], 0.03, M["fence"], root)
        for j in range(6):
            xx = x0 + 0.05 + j * 0.2
            tube(f"{name}FenceBar{k}{j}", [(xx, 0.25, 1.0), (xx, 1.0, 1.0)], 0.012, M["fence"], root)
        for xx in (x0 + 0.1, x0 + 1.0):
            tube(f"{name}FenceFoot{k}{xx:.1f}", [(xx, 0.0, 0.75), (xx, 0.25, 1.0), (xx, 0.0, 1.25)], 0.02, M["fence"], root)
    return root


def build_neon_alley_preview(parent=None, name="NeonAlleyPreview"):
    root = build_neon_alley(parent, name)
    for n, pos, col, e, sz in (("Magenta", (16, 12, 18), (0.9, 0.35, 0.8), 20000, 10), ("Blue", (-14, 16, 10), (0.3, 0.4, 1.0), 14000, 10),
                               ("YardCyan", (1.0, 2.5, 3.5), (0.3, 0.9, 1.0), 500, 2), ("SignRed", (1.5, 6.5, 1.0), (1.0, 0.25, 0.35), 400, 2),
                               ("Sign", (0.5, 5.5, 0.5), (0.3, 0.9, 1.0), 350, 2)):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = col
        ld.energy = e
        ld.shadow_soft_size = sz
        lo = bpy.data.objects.new(n, ld)
        lo.visible_glossy = False
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)
    return root
