"""
Cyberpunk ramen corner shop on a tiled street platform (style ref supplied by
the user: an isometric two-storey corner shop). Original model built here.

Ground floor: open ramen stall on the front (+Z) with a wooden counter, two
stools, red awning and a red neon ラーメン sign; a small shop on the right (+X)
with a lit door, a barred lit window and a tiled canopy roof; a big pipe down
the corner. Upper floor: a rounded concrete box over the stall with a wide
rounded window into a lit room; a taller block behind on the right with a big
round louvred vent; a roof-garden box with two bonsai trees at the back.
Around it: a tall glowing vertical sign 客商売 on the left with a street lamp,
roof AC units and cables, a utility pole with insulators, cables and a
地下鉄 metro sign, a metro stair entrance with railings and green glow,
cardboard boxes, a caution sign and a road barrier with a beacon.

    build_ramen_corner(parent=None, name="RamenCorner")
        origin on the ground at the centre of the building; platform 14 x 14 m.
    build_ramen_corner_preview(parent, name) -> model + coloured preview lights

Coordinates are three.js style (Y up).
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
from city_smooth import rounded_band, rounded_prism  # noqa: E402

JP_FONT = "C:/Windows/Fonts/YuGothB.ttc"


def _mats():
    return {
        "tile": mat("RcTile", "#5d5f66", 0.85),
        "tileDark": mat("RcTileDark", "#45474e", 0.9),
        "concrete": mat("RcConcrete", "#8a8c8f", 0.8),
        "concreteDark": mat("RcConcreteDark", "#5e6064", 0.85),
        "metal": mat("RcMetal", "#3a3d44", 0.4, metal=0.7),
        "pipe": mat("RcPipe", "#6b6e74", 0.35, metal=0.8),
        "wood": mat("RcWood", "#6a4128", 0.6),
        "woodDark": mat("RcWoodDark", "#3e2618", 0.7),
        "roofTile": mat("RcRoofTile", "#4a3a34", 0.7),
        "red": mat("RcAwning", "#9e1622", 0.6),
        "black": mat("RcBlack", "#121317", 0.4),
        "white": mat("RcWhite", "#e6e6ea", 0.5),
        "cardboard": mat("RcCardboard", "#9c7a56", 0.8),
        "yellow": mat("RcYellow", "#e6b21a", 0.5),
        "leaf": mat("RcLeaf", "#3f7a3a", 0.7),
        "leafLight": mat("RcLeafLight", "#5e9a48", 0.7),
        "trunk": mat("RcTrunk", "#4a3424", 0.8),
        "soil": mat("RcSoil", "#2a221c", 0.9),
        "warm": mat("RcWarmGlow", "#ffd2a0", emit="#ffb070", strength=3.0),
        "warmDim": mat("RcWarmDim", "#ffcf9a", emit="#ff9e58", strength=1.4),
        "roomFloor": mat("RcRoomFloor", "#9aa6b8", 0.4, emit="#6a7a99", strength=0.6),
        "roomBlue": mat("RcRoomBlue", "#2f5fb0", 0.6, emit="#2a4a90", strength=0.5),
        "roomYellow": mat("RcRoomYellow", "#e0b830", 0.6, emit="#a08010", strength=0.4),
        "tube": mat("RcTubeLight", "#ffffff", emit="#f2f6ff", strength=6.0),
        "neonRed": mat("RcNeonRed", "#ff2a40", emit="#ff2a40", strength=10.0),
        "neonPink": mat("RcNeonPink", "#ff5fa8", emit="#ff5fa8", strength=9.0),
        "signGlow": mat("RcSignGlow", "#d8fff4", emit="#b8ffea", strength=3.0),
        "signInk": mat("RcSignInk", "#0c1a18", 0.6),
        "metroGlow": mat("RcMetroGlow", "#ffc23a", emit="#ffb020", strength=8.0),
        "green": mat("RcGreenGlow", "#5affc8", emit="#3affb0", strength=4.0),
        "cyan": mat("RcLampCyan", "#c8fff6", emit="#a0fff0", strength=12.0),
        "beacon": mat("RcBeacon", "#ff8a1a", emit="#ff7a00", strength=12.0),
    }


def _text(name, body, c, size, m, parent, rot=(math.pi / 2, 0, 0), depth=0.03, jp=True):
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    if jp and os.path.exists(JP_FONT):
        t.data.font = bpy.data.fonts.load(JP_FONT, check_existing=True)
    t.data.body = body
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.size = size
    t.data.extrude = depth
    t.rotation_euler = rot
    t.location = P(*c)
    t.data.materials.append(m)
    bpy.ops.object.convert(target="MESH")
    t = bpy.context.active_object
    t.name = name
    t.parent = parent
    return t


def _vertical_text(name, chars, x, y_top, z, size, step, m, parent):
    for i, ch in enumerate(chars):
        _text(f"{name}{i}", ch, (x, y_top - i * step, z), size, m, parent)


def _sag_cable(name, a, b, sag, M, parent, r=0.025):
    pts = []
    for k in range(13):
        t = k / 12
        pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - sag * 4 * t * (1 - t), a[2] + (b[2] - a[2]) * t))
    tube(name, pts, r, M["black"], parent)


def _ac_unit(name, c, M, parent, face="z"):
    x, y, z = c
    if face == "z":
        block(f"{name}Body", (x, y, z), (1.1, 0.75, 0.45), M["white"], parent, r=0.03)
        disc(f"{name}Fan", (x - 0.18, y, z + 0.235), 0.27, 0.02, M["black"], parent, axis="z")
        for k in range(5):
            block(f"{name}Grill{k}", (x + 0.33, y - 0.24 + k * 0.12, z + 0.235), (0.28, 0.04, 0.02), M["metal"], parent)
    else:
        block(f"{name}Body", (x, y, z), (0.45, 0.75, 1.1), M["white"], parent, r=0.03)
        disc(f"{name}Fan", (x + 0.235, y, z + 0.18), 0.27, 0.02, M["black"], parent, axis="x")
        for k in range(5):
            block(f"{name}Grill{k}", (x + 0.235, y - 0.24 + k * 0.12, z - 0.33), (0.02, 0.04, 0.28), M["metal"], parent)


def _bonsai(name, c, s, M, parent, rng):
    x, y, z = c
    tube(f"{name}Trunk", [(x, y, z), (x + 0.15 * s, y + 0.7 * s, z), (x - 0.1 * s, y + 1.3 * s, z + 0.1 * s), (x + 0.05 * s, y + 1.8 * s, z)], 0.07 * s, M["trunk"], parent)
    for k, (dx, dy, dz, r) in enumerate(((0.3, 1.0, 0.0, 0.42), (-0.35, 1.45, 0.1, 0.4), (0.15, 1.95, -0.05, 0.5), (-0.1, 2.3, 0.1, 0.32))):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r * s, location=P(x + dx * s, y + dy * s, z + dz * s))
        b = bpy.context.active_object
        b.name = f"{name}Leaf{k}"
        b.scale = (1.35, 1.35, 0.55)  # flat cloud-pruned pads
        bpy.ops.object.shade_smooth()
        b.data.materials.append(M["leaf" if k % 2 else "leafLight"])
        b.parent = parent


def build_ramen_corner(parent=None, name="RamenCorner", seed=4):
    M = _mats()
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------------------------------------------------------------- tiled platform
    hole = (4.7, 6.9, 0.8, 5.2)  # metro stair opening x0, x1, z0, z1
    for i in range(7):
        for j in range(7):
            x0, z0 = -7 + i * 2, -7 + j * 2
            edge = i in (0, 6) or j in (0, 6)
            if edge and rng.random() < 0.3:
                continue  # broken, missing edge slabs like the reference
            if x0 + 2 > hole[0] and x0 < hole[1] and z0 + 2 > hole[2] and z0 < hole[3]:
                continue
            lift = rng.uniform(0, 0.03)
            slab(f"{name}Tile{i}{j}", x0 + 0.04, x0 + 1.96, -0.25, 0.0 + lift, z0 + 0.04, z0 + 1.96, M["tile" if (i + j) % 3 else "tileDark"], root)
    # a few loose slabs floating out past the edge
    for k, (x, z) in enumerate(((-8.6, 3.0), (7.8, 6.2), (-3.0, 8.4))):
        slab(f"{name}LooseTile{k}", x, x + 1.9, -0.25, 0.0, z, z + 1.9, M["tile"], root)

    # ---------------------------------------------------------------- ground floor
    GH = 3.2
    # back mass (behind the stall and the shop)
    slab(f"{name}BackMass", -4.0, 4.0, 0, GH, -4.0, -0.2, M["concreteDark"], root)
    # ramen stall (front-left, open to +Z)
    slab(f"{name}StallBack", -4.0, -0.2, 0, GH, -0.2, 0.1, M["woodDark"], root)
    slab(f"{name}StallGlow", -3.7, -0.5, 0.9, 2.6, 0.1, 0.13, M["warm"], root)
    slab(f"{name}StallSide", -4.0, -3.75, 0, GH, 0.1, 4.0, M["concreteDark"], root)
    slab(f"{name}Counter", -3.75, -0.3, 0, 1.05, 3.2, 3.8, M["wood"], root)
    slab(f"{name}CounterTop", -3.8, -0.25, 1.05, 1.12, 3.15, 3.9, M["woodDark"], root)
    for k, x in enumerate((-3.0, -2.0, -1.0)):
        slab(f"{name}Bowl{k}", x - 0.15, x + 0.15, 1.12, 1.24, 3.45, 3.65, M["white"], root)
    for k, x in enumerate((-2.9, -1.6)):
        disc(f"{name}StoolTop{k}", (x, 0.78, 4.45), 0.22, 0.08, M["black"], root, verts=20)
        disc(f"{name}StoolLeg{k}", (x, 0.4, 4.45), 0.04, 0.78, M["pipe"], root, verts=10)
        disc(f"{name}StoolFoot{k}", (x, 0.02, 4.45), 0.2, 0.04, M["pipe"], root, verts=20)
        disc(f"{name}StoolRing{k}", (x, 0.3, 4.45), 0.16, 0.02, M["pipe"], root, verts=20)
    for k, x in enumerate((-3.85, -0.35)):
        slab(f"{name}TubeLight{k}", x - 0.05, x + 0.05, 0.6, 2.6, 3.95, 4.05, M["tube"], root)
    # awning sloping out over the counter
    aw = block(f"{name}Awning", (-2.0, 2.35, 4.6), (4.4, 0.08, 1.5), M["red"], root)
    aw.rotation_euler = (math.radians(-22), 0, 0)
    slab(f"{name}AwningValance", -4.2, 0.2, 1.85, 2.1, 5.3, 5.35, M["red"], root)
    # fascia above with the red neon ラーメン sign and a pink neon loop
    # sign board hung under the upper floor's front edge, above the awning
    slab(f"{name}Fascia", -4.0, -0.2, 2.6, 3.15, 4.25, 4.45, M["black"], root)
    _text(f"{name}RamenNeon", "ラーメン", (-2.1, 2.88, 4.5), 0.6, M["neonRed"], root)
    tube(f"{name}NeonLoop", [(-4.05, 2.6, 4.1)] + [(-4.05 + 0.35 * math.sin(a / 8 * math.pi), 2.95 + 0.35 * math.cos(a / 8 * math.pi), 4.1) for a in range(9)], 0.05, M["neonPink"], root)
    # shop on the right (+X face): lit door, barred lit window, wall lamp, meter box
    slab(f"{name}ShopMass", -0.2, 4.0, 0, GH, -0.2, 4.0, M["concrete"], root)
    slab(f"{name}Door", 3.98, 4.04, 0.05, 2.3, 0.4, 1.5, M["warm"], root)
    slab(f"{name}DoorFrame", 3.97, 4.06, 2.3, 2.42, 0.3, 1.6, M["woodDark"], root)
    slab(f"{name}Window", 3.98, 4.04, 1.0, 2.3, 2.1, 3.5, M["warmDim"], root)
    for k in range(6):
        z = 2.2 + k * 0.24
        slab(f"{name}Bar{k}", 4.04, 4.1, 0.95, 2.35, z - 0.03, z + 0.03, M["metal"], root)
    slab(f"{name}Meter", 4.0, 4.18, 1.2, 1.85, -0.05, 0.3, M["metal"], root)
    disc(f"{name}MeterLight", (4.19, 1.6, 0.12), 0.05, 0.02, M["beacon"], root, axis="x")
    # tiled canopy roof over the shop front
    for k in range(7):
        b = block(f"{name}RoofTile{k}", (4.55, 2.85 - k * 0.0, -0.05 + k * 0.65), (1.4, 0.07, 0.62), M["roofTile"], root)
        b.rotation_euler = (0, math.radians(-24), 0)
        tube(f"{name}RoofRib{k}", [(3.95, 3.1, -0.3 + k * 0.65), (5.2, 2.55, -0.3 + k * 0.65)], 0.04, M["woodDark"], root)
    slab(f"{name}RoofBeam", 5.15, 5.3, 2.35, 2.55, -0.4, 4.2, M["woodDark"], root)
    _ac_unit(f"{name}ShopAC", (4.3, 2.95, -1.4), M, root, face="x")
    # big pipe down the front corner, with an elbow into the wall
    tube(f"{name}CornerPipe", [(-0.05, 0.0, 4.1), (-0.05, 3.3, 4.1), (-0.05, 3.55, 3.85)], 0.17, M["pipe"], root)

    # ---------------------------------------------------------------- upper floor
    UY0, UY1 = 3.4, 6.5
    # rounded concrete box over the stall, with the wide window into a lit room
    rounded_prism(f"{name}UpFloor", (-1.9, UY0 - 0.25, 1.5), 5.6, 6.0, 1.1, 0.35, M["concrete"], root, seg=8, cap_m=M["concrete"])
    rounded_prism(f"{name}UpRoof", (-1.9, UY1, 1.5), 5.8, 6.2, 1.2, 0.4, M["concrete"], root, seg=8, cap_m=M["concreteDark"])
    rounded_band(f"{name}UpBelly", (-1.9, UY0 - 0.35, 1.5), 5.65, 6.05, 1.12, 0.12, M["pipe"], root, seg=8)
    # walls: left side, back, and the front wall framing the window
    slab(f"{name}UpLeft", -4.7, -4.4, UY0, UY1, -1.2, 3.9, M["concrete"], root)
    slab(f"{name}UpBack", -4.4, 0.9, UY0, UY1, -1.5, -1.2, M["concrete"], root)
    slab(f"{name}UpFrontL", -4.4, -4.0, UY0, UY1, 4.2, 4.5, M["concrete"], root)
    slab(f"{name}UpFrontR", 0.3, 0.9, UY0, UY1, 4.2, 4.5, M["concrete"], root)
    slab(f"{name}UpFrontSill", -4.4, 0.9, UY0, UY0 + 0.45, 4.2, 4.5, M["concrete"], root)
    slab(f"{name}UpFrontHead", -4.4, 0.9, UY1 - 0.4, UY1, 4.2, 4.5, M["concrete"], root)
    slab(f"{name}UpRight", 0.6, 0.9, UY0, UY1, -1.2, 4.2, M["concrete"], root)
    # window frame (thick, softly rounded) + the lit room behind it
    # window frame: a thin dark trim round the opening (the opening itself stays open)
    for k, (x0, x1, y0, y1) in enumerate(((-4.0, 0.3, UY0 + 0.45, UY0 + 0.55), (-4.0, 0.3, UY1 - 0.5, UY1 - 0.4),
                                           (-4.0, -3.9, UY0 + 0.45, UY1 - 0.4), (0.2, 0.3, UY0 + 0.45, UY1 - 0.4))):
        slab(f"{name}WinTrim{k}", x0, x1, y0, y1, 4.45, 4.55, M["concreteDark"], root)
    slab(f"{name}RoomFloor", -4.4, 0.6, UY0, UY0 + 0.05, -1.2, 4.2, M["roomFloor"], root)
    for k in range(9):
        x = -4.2 + k * 0.6
        slab(f"{name}RoomFloorLine{k}", x, x + 0.02, UY0 + 0.05, UY0 + 0.06, -1.2, 4.2, M["metal"], root)
    slab(f"{name}RoomWallBlue", -4.4, 0.6, UY0, UY1, -1.2, -1.1, M["roomBlue"], root)
    slab(f"{name}RoomWallYellow", 0.4, 0.6, UY0, UY1 - 0.5, -1.1, 2.0, M["roomYellow"], root)
    slab(f"{name}RoomCeil", -4.4, 0.6, UY1 - 0.05, UY1, -1.2, 4.2, M["white"], root)
    slab(f"{name}RoomCeilLight", -3.2, -0.6, UY1 - 0.08, UY1 - 0.05, 0.6, 1.4, M["tube"], root)
    # sofa / day bed
    block(f"{name}SofaBase", (-1.7, UY0 + 0.3, 0.3), (3.0, 0.5, 1.2), M["white"], root, r=0.08)
    block(f"{name}SofaBack", (-1.7, UY0 + 0.75, -0.2), (3.0, 0.6, 0.3), M["white"], root, r=0.08)
    block(f"{name}SofaArm", (-0.1, UY0 + 0.55, 0.3), (0.3, 0.55, 1.2), M["roomYellow"], root, r=0.06)
    block(f"{name}Cushion", (-2.6, UY0 + 0.62, 0.35), (0.8, 0.18, 0.7), M["roomBlue"], root, r=0.06)
    # taller block behind on the right, with the big round louvred vent on +X
    slab(f"{name}RightBlock", 0.6, 4.0, UY0 - 0.25, UY1 + 1.2, -4.0, 0.9, M["concreteDark"], root)
    disc(f"{name}VentDisc", (4.02, 5.1, -1.5), 1.25, 0.06, M["black"], root, axis="x", verts=40)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.3, minor_radius=0.13, major_segments=40, minor_segments=10)
    ring = bpy.context.active_object
    ring.name = f"{name}VentRing"
    ring.location = P(4.06, 5.1, -1.5)
    ring.rotation_euler = (0, math.pi / 2, 0)
    bpy.ops.object.shade_smooth()
    ring.data.materials.append(M["pipe"])
    ring.parent = root
    for k in range(8):
        y = 4.2 + k * 0.25
        half = math.sqrt(max(0.0, 1.2 ** 2 - (y - 5.1) ** 2))
        b = block(f"{name}Louver{k}", (4.08, y, -1.5), (0.06, 0.05, 2 * half), M["metal"], root)
        b.rotation_euler = (math.radians(25), 0, 0)
    # wall lamp + small balcony shelf by the vent
    slab(f"{name}VentShelf", 4.0, 4.6, 3.6, 3.7, 0.0, 0.9, M["metal"], root)
    block(f"{name}CageLamp", (4.3, 3.95, 0.45), (0.22, 0.34, 0.22), M["warm"], root, r=0.04)

    # ---------------------------------------------------------------- roof
    # roof-garden box at the back with two bonsai trees
    slab(f"{name}GardenBox", -4.4, 0.6, UY1 + 0.4, UY1 + 1.1, -4.0, -1.5, M["concreteDark"], root)
    slab(f"{name}GardenSoil", -4.2, 0.4, UY1 + 1.1, UY1 + 1.18, -3.8, -1.7, M["soil"], root)
    slab(f"{name}GardenUnder", -4.4, 0.6, UY0 - 0.25, UY1 + 0.4, -4.0, -1.5, M["concreteDark"], root)
    _bonsai(f"{name}BonsaiA", (-3.0, UY1 + 1.18, -2.7), 1.25, M, root, rng)
    _bonsai(f"{name}BonsaiB", (-0.9, UY1 + 1.18, -2.6), 1.0, M, root, rng)
    for k in range(10):  # moss / shrubs at the trees' feet
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rng.uniform(0.12, 0.25),
                                              location=P(rng.uniform(-4.0, 0.3), UY1 + 1.2, rng.uniform(-3.7, -1.8)))
        b = bpy.context.active_object
        b.name = f"{name}Moss{k}"
        b.data.materials.append(M["leafLight"])
        b.parent = root
    # AC units and cables on the roofs
    _ac_unit(f"{name}RoofAC0", (-1.6, UY1 + 0.78, 2.2), M, root)
    _ac_unit(f"{name}RoofAC1", (-3.3, UY1 + 1.55, -1.1), M, root)
    _ac_unit(f"{name}RoofAC2", (2.2, UY1 + 1.6, -1.8), M, root)
    tube(f"{name}RoofCable0", [(-1.0, UY1 + 0.45, 2.0), (0.0, UY1 + 0.42, 1.0), (0.9, UY1 + 0.42, 0.6), (2.0, UY1 + 1.22, 0.0)], 0.04, M["black"], root)
    tube(f"{name}RoofCable1", [(-2.4, UY1 + 0.45, 3.6), (-0.4, UY1 + 0.42, 3.9), (0.6, UY1 + 0.42, 3.0)], 0.035, M["black"], root)

    # ---------------------------------------------------------------- tall vertical sign + lamp (left)
    slab(f"{name}SignBox", -6.5, -5.5, 5.6, 10.0, 1.6, 2.0, M["signGlow"], root)
    slab(f"{name}SignCap", -6.6, -5.4, 10.0, 10.3, 1.5, 2.1, M["metal"], root)
    _vertical_text(f"{name}SignChar", "客商売", -6.0, 9.3, 2.04, 0.85, 1.25, M["signInk"], root)
    slab(f"{name}SignArm", -5.5, -4.7, 7.4, 7.6, 1.7, 1.9, M["metal"], root)
    slab(f"{name}SignArm2", -5.5, -4.7, 6.0, 6.2, 1.7, 1.9, M["metal"], root)
    tube(f"{name}LampArm", [(-4.4, 5.0, 2.6), (-5.6, 5.0, 2.6), (-6.2, 4.8, 2.6)], 0.05, M["metal"], root)
    block(f"{name}LampHead", (-6.3, 4.72, 2.6), (0.9, 0.12, 0.3), M["metal"], root, r=0.03)
    slab(f"{name}LampLight", -6.7, -5.9, 4.64, 4.66, 2.5, 2.7, M["cyan"], root)

    # ---------------------------------------------------------------- utility pole + metro sign
    px, pz = 6.2, -2.0
    disc(f"{name}Pole", (px, 4.6, pz), 0.14, 9.2, M["metal"], root, verts=12)
    disc(f"{name}PoleBase", (px, 0.4, pz), 0.3, 0.8, M["concreteDark"], root, verts=12)
    slab(f"{name}CrossArm", px - 1.2, px + 1.2, 8.6, 8.75, pz - 0.08, pz + 0.08, M["metal"], root)
    for k, dx in enumerate((-1.0, 0.0, 1.0)):
        disc(f"{name}Insulator{k}", (px + dx, 8.95, pz), 0.12, 0.35, M["white"], root, verts=12)
    _sag_cable(f"{name}Cable0", (px - 1.0, 9.0, pz), (3.9, UY1 + 1.2, -0.8), 0.6, M, root)
    _sag_cable(f"{name}Cable1", (px, 9.0, pz), (0.9, UY1 + 0.4, 1.6), 0.9, M, root)
    _sag_cable(f"{name}Cable2", (px + 1.0, 9.0, pz), (8.5, 7.5, 6.0), 0.8, M, root)
    tube(f"{name}SignArmPole", [(px, 6.4, pz), (px, 6.4, pz + 1.2), (px, 6.1, pz + 1.6)], 0.06, M["metal"], root)
    slab(f"{name}MetroSign", px - 0.15, px + 0.15, 5.3, 6.1, pz + 0.9, pz + 3.9, M["black"], root)
    slab(f"{name}MetroIcon", px + 0.15, px + 0.17, 5.45, 5.95, pz + 3.25, pz + 3.75, M["metroGlow"], root)
    _text(f"{name}MetroText", "地下鉄", (px + 0.18, 5.7, pz + 2.05), 0.56, M["metroGlow"], root, rot=(math.pi / 2, 0, math.pi / 2))
    block(f"{name}PoleLamp", (px - 0.25, 4.2, pz + 0.25), (0.22, 0.34, 0.22), M["warm"], root, r=0.04)

    # ---------------------------------------------------------------- metro stair entrance
    hx0, hx1, hz0, hz1 = hole
    steps = 12
    for k in range(steps):
        z = hz0 + (hz1 - hz0) * k / steps
        y = -0.25 * (k + 1)
        slab(f"{name}Step{k}", hx0, hx1, y - 0.25, y, z, hz1, M["tileDark"], root)
    for k, x in enumerate((hx0 - 0.15, hx1)):
        slab(f"{name}StairWall{k}", x, x + 0.15, -3.2, 0.0, hz0, hz1, M["concreteDark"], root)
    slab(f"{name}StairEnd", hx0, hx1, -3.2, 0.0, hz0 - 0.15, hz0, M["concreteDark"], root)
    slab(f"{name}StairGlow", hx0 + 0.2, hx1 - 0.2, -3.1, -1.4, hz0, hz0 + 0.05, M["green"], root)
    for k, x in enumerate((hx0 + 0.05, hx1 - 0.05)):
        slab(f"{name}StairStrip{k}", x - 0.03, x + 0.03, -2.6, -0.4, hz0 + 0.3, hz0 + 0.7, M["green"], root)
    rail_y = 1.05
    tube(f"{name}RailBack", [(hx0, rail_y, hz1), (hx0, rail_y, hz0), (hx1, rail_y, hz0), (hx1, rail_y, hz1)], 0.05, M["pipe"], root)
    for k, (x, z) in enumerate(((hx0, hz1), (hx0, hz0), (hx1, hz0), (hx1, hz1), (hx0, (hz0 + hz1) / 2), (hx1, (hz0 + hz1) / 2))):
        tube(f"{name}RailPost{k}", [(x, 0.0, z), (x, rail_y, z)], 0.045, M["pipe"], root)

    # ---------------------------------------------------------------- props
    for k, (x, y, z, s, rot) in enumerate(((-5.9, 0.35, -2.8, 0.7, 10), (-5.1, 0.3, -2.0, 0.6, -14), (-5.6, 0.95, -2.5, 0.6, 30))):
        b = block(f"{name}Box{k}", (x, y, z), (s, s * 0.85, s), M["cardboard"], root, r=0.02)
        b.rotation_euler = (0, 0, math.radians(rot))
    for k, s in enumerate((-1, 1)):  # caution A-frame sign
        b = block(f"{name}Caution{k}", (-5.6, 0.55, 3.2 + s * 0.2), (0.9, 1.1, 0.04), M["yellow"], root)
        b.rotation_euler = (math.radians(s * 12), 0, 0)
    _text(f"{name}CautionMark", "!", (-5.6, 0.6, 3.42 + 0.05), 0.55, M["black"], root, jp=False, rot=(math.radians(78), 0, 0))
    # road barrier with a blinking beacon
    for k, x in enumerate((-1.4, 1.6)):
        tube(f"{name}BarrierLegA{k}", [(x - 0.35, 0.0, 6.0), (x, 1.0, 6.0)], 0.04, M["metal"], root)
        tube(f"{name}BarrierLegB{k}", [(x + 0.35, 0.0, 6.0), (x, 1.0, 6.0)], 0.04, M["metal"], root)
    for k in range(8):
        x = -1.4 + k * 0.375
        slab(f"{name}BarrierStripe{k}", x, x + 0.375, 0.9, 1.15, 5.95, 6.05, M["yellow" if k % 2 else "black"], root)
    disc(f"{name}BarrierBeacon", (-1.2, 1.28, 6.0), 0.1, 0.2, M["beacon"], root, verts=12)
    return root


def build_ramen_corner_preview(parent=None, name="RamenCornerPreview"):
    root = build_ramen_corner(parent, name)
    for n, pos, col, e, sz in (("Stall", (-2.0, 2.0, 5.5), (1.0, 0.55, 0.35), 600, 1.0), ("Room", (-1.8, 5.6, 2.5), (0.85, 0.9, 1.0), 70, 1.0),
                               ("Teal", (16, 18, 20), (0.35, 0.8, 0.85), 30000, 10), ("TealBack", (-14, 14, -6), (0.3, 0.6, 0.8), 12000, 10), ("Green", (8, 6, 2), (0.4, 1.0, 0.7), 900, 3),
                               ("Shop", (5.5, 2.0, 1.5), (1.0, 0.6, 0.4), 350, 1.0), ("Sign", (-6.5, 7, 3.5), (0.6, 1.0, 0.95), 500, 1.5)):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = col
        ld.energy = e
        ld.shadow_soft_size = sz
        lo = bpy.data.objects.new(n, ld)
        lo.visible_glossy = False
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)
    return root
