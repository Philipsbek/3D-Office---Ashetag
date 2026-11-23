"""
Two-level industrial loft: the new room structure for the ASHETAG office.
Layout and lighting are inspired by a cutaway "dollhouse" loft (two floors,
open stairs, pipework, colour-zoned neon), but it's a normal room here: floor,
back wall and left wall, open to the front and right where the camera sits.
With glass_left=True (the default since 2026-11-22) the left wall is the approved
B1 floor-to-ceiling glass; the back wall stays solid concrete and brick.

    build_loft_room(parent=None, name="LoftRoom") -> root empty

Coordinates are three.js style (Y up, +Z toward the camera), metres:
- footprint  x -7..7, z -6..4      ground floor at y = 0
- mezzanine  x -7..7, z -6..-2.5   top at y = 3.3, copper railing on its edge
- stairs     x ≈ 4.6, climbing from z = 1.6 (ground) to the mezzanine edge

Zones (filled with objects in later steps; each has its own light colour):
  upper left   workstation        teal        upper middle  arcades      blue/red
  upper right  big window + board yellow      lower left    kitchen/neon red
  lower middle bar + alcove       blue        lower right   doorway      orange

Empties named Zone_* mark where each zone's furniture and light go.
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, _hex  # noqa: E402
from gaming_desk import tube  # noqa: E402

X0, X1 = -7.0, 7.0  # room width
Z0, Z1 = -6.0, 4.0  # back wall .. open front
WALL_H = 6.8
MEZ_Z = -2.5  # front edge of the mezzanine
MEZ_Y = 3.3  # mezzanine floor height (top)
MEZ_T = 0.3  # slab thickness
STAIR_X, STAIR_W = 4.6, 1.1
COPPER = "#b8642e"

_M = {}


def mat(name, color, rough=0.7, metal=0.0, emit=None, strength=1.0):
    key = "Loft_" + name
    if key in _M:
        return _M[key]
    m = bpy.data.materials.new(key)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*_hex(color), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*_hex(emit), 1)
        b.inputs["Emission Strength"].default_value = strength
    m.diffuse_color = (*_hex(color), 1)
    _M[key] = m
    return m


def block(name, c, size, m, parent, r=0.0):
    """Plain box centred at c (three.js coords); r > 0 adds a small edge bevel."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.location = P(*c)
    o.scale = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if r > 0:
        bev = o.modifiers.new("Bevel", "BEVEL")
        bev.width = r
        bev.segments = 2
        bev.limit_method = "ANGLE"
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def slab(name, x0, x1, y0, y1, z0, z1, m, parent, r=0.0):
    """Axis-aligned box from min/max corners (three.js coords)."""
    return block(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), m, parent, r)


def empty(name, pos, parent):
    e = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(e)
    e.location = P(*pos)
    e.parent = parent
    return e


def _glass_mat():
    """Clear window glass with a faint cool tint (alpha-blended)."""
    m = bpy.data.materials.get("Loft_WindowGlass")
    if m:
        return m
    m = bpy.data.materials.new("Loft_WindowGlass")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*_hex("#9fb4d8"), 1)
    b.inputs["Roughness"].default_value = 0.04
    b.inputs["Alpha"].default_value = 0.12
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, attr, val)
        except Exception:
            pass
    m.diffuse_color = (*_hex("#9fb4d8"), 0.12)
    _M["Loft_WindowGlass"] = m
    return m


def build_loft_room(parent=None, name="LoftRoom", glass_left=True):
    CONCRETE = mat("Concrete", "#2a2a2c", 0.85)
    FLOOR = mat("FloorTile", "#1d1f22", 0.45)
    SLAB = mat("SlabConcrete", "#232325", 0.8)
    BRICK = mat("Brick", "#3a1f1c", 0.9)
    STEEL = mat("Steel", "#2c2e31", 0.4, metal=0.85)
    PIPE = mat("Pipe", "#3b3d40", 0.35, metal=0.9)
    RUST = mat("RustPipe", "#5a3a26", 0.55, metal=0.6)
    CU = mat("Copper", COPPER, 0.35, metal=0.9)
    DUCT = mat("Duct", "#3a3c3f", 0.45, metal=0.7)
    VENT = mat("Vent", "#0c0c0d", 0.6)
    BLUE_WALL = mat("BlueWall", "#1e6e9e", 0.8)
    WINDOW = mat("WindowGlow", "#ffd21a", emit="#ffd21a", strength=4.0)
    DOOR_GLOW = mat("DoorGlow", "#ff7a14", emit="#ff7a14", strength=3.0)
    STRIP_TEAL = mat("StripTeal", "#3fe0c8", emit="#3fe0c8", strength=6.0)
    STRIP_WHITE = mat("StripWhite", "#cfe8ff", emit="#cfe8ff", strength=5.0)
    STRIP_PINK = mat("StripPink", "#ff5fb0", emit="#ff5fb0", strength=6.0)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------------------------------------------------------------- floor + walls
    slab("Floor", X0, X1 + 1.5, -0.12, 0, Z0, Z1, FLOOR, root)
    # floor tile seams: thin dark strips every 1 m (cheap stand-in until textures)
    SEAM = mat("TileSeam", "#0e0f10", 0.6)
    for i, x in enumerate(range(int(X0) + 1, int(X1) + 1)):
        slab(f"SeamX{i}", x - 0.008, x + 0.008, 0, 0.002, Z0, Z1, SEAM, root)
    for i, z in enumerate(range(int(Z0) + 1, int(Z1))):
        slab(f"SeamZ{i}", X0, X1 + 1.5, 0, 0.002, z - 0.008, z + 0.008, SEAM, root)

    slab("BackWall", X0 - 0.3, X1 + 1.5, 0, WALL_H, Z0 - 0.3, Z0, CONCRETE, root)
    if glass_left:
        # approved B1 glazing on the left wall: floor-to-ceiling glass, one slim black
        # mullion, thin black sill and head, butting into the solid back wall
        GLASS = _glass_mat()
        FRAME = mat("GlassFrame", "#2c2e36", 0.35, metal=0.6)
        gx = X0 - 0.15  # centred in the old wall thickness
        slab("LeftGlass", gx - 0.01, gx + 0.01, 0.06, WALL_H - 0.06, Z0, Z1, GLASS, root)
        slab("LeftGlassSill", gx - 0.04, gx + 0.04, 0, 0.06, Z0, Z1, FRAME, root)
        slab("LeftGlassHead", gx - 0.04, gx + 0.04, WALL_H - 0.06, WALL_H, Z0, Z1, FRAME, root)
        zm = (Z0 + Z1) / 2
        slab("LeftGlassMullion", gx - 0.04, gx + 0.04, 0, WALL_H, zm - 0.03, zm + 0.03, FRAME, root)
    else:
        slab("LeftWall", X0 - 0.3, X0, 0, WALL_H, Z0, Z1, CONCRETE, root)
    # brick face on the upper left (workstation) and lower left (kitchen) walls
    slab("BrickUpperBack", X0, -2.4, MEZ_Y, WALL_H - 0.9, Z0, Z0 + 0.04, BRICK, root)
    if not glass_left:
        slab("BrickLower", X0 + 0.0, X0 + 0.04, 0, MEZ_Y - MEZ_T, Z0, MEZ_Z + 1.0, BRICK, root)
    slab("BrickLowerBack", X0, -3.2, 0, MEZ_Y - MEZ_T, Z0, Z0 + 0.04, BRICK, root)

    # ---------------------------------------------------------------- mezzanine
    slab("Mezzanine", X0, X1, MEZ_Y - MEZ_T, MEZ_Y, Z0, MEZ_Z, SLAB, root)
    slab("MezzanineFascia", X0, X1, MEZ_Y - MEZ_T - 0.02, MEZ_Y + 0.02, MEZ_Z - 0.05, MEZ_Z + 0.03, STEEL, root)
    # light strip tucked under the slab edge (lights the lower level's front)
    slab("UnderEdgeStrip", X0 + 0.3, X1 - 0.3, MEZ_Y - MEZ_T - 0.05, MEZ_Y - MEZ_T - 0.02, MEZ_Z - 0.2, MEZ_Z - 0.12, STRIP_WHITE, root)
    # support columns (clear of the stairs)
    for i, x in enumerate((-3.4, 1.0)):
        slab(f"Column{i}", x - 0.14, x + 0.14, 0, MEZ_Y - MEZ_T, MEZ_Z - 0.32, MEZ_Z - 0.04, STEEL, root)

    # copper pipe railing along the edge, open where the stairs arrive
    gap0, gap1 = STAIR_X - STAIR_W / 2 - 0.05, STAIR_X + STAIR_W / 2 + 0.05
    rz = MEZ_Z - 0.12
    for k, (a, b) in enumerate(((X0 + 0.3, gap0), (gap1, X1 - 0.15))):
        tube(f"RailTop{k}", [(a, MEZ_Y + 1.0, rz), (b, MEZ_Y + 1.0, rz)], 0.03, CU, root)
        tube(f"RailMid{k}", [(a, MEZ_Y + 0.5, rz), (b, MEZ_Y + 0.5, rz)], 0.018, CU, root)
        n = max(1, round((b - a) / 1.3))
        for j in range(n + 1):
            x = a + (b - a) * j / n
            tube(f"RailPost{k}_{j}", [(x, MEZ_Y, rz), (x, MEZ_Y + 1.0, rz)], 0.024, CU, root)

    # ---------------------------------------------------------------- open stairs
    steps = 11
    rise = MEZ_Y / steps
    run = 0.37
    z_top = MEZ_Z
    z_bot = z_top + run * steps
    for i in range(steps - 1):
        y = rise * (i + 1)
        z = z_bot - run * (i + 1) + run / 2
        slab(f"Tread{i}", STAIR_X - STAIR_W / 2 + 0.06, STAIR_X + STAIR_W / 2 - 0.06, y - 0.06, y, z - run / 2 - 0.02, z + run / 2, STEEL, root)
    # sloped copper stringers + handrail
    for k, sx in enumerate((STAIR_X - STAIR_W / 2, STAIR_X + STAIR_W / 2)):
        tube(f"Stringer{k}", [(sx, 0.0, z_bot + 0.05), (sx, MEZ_Y, z_top)], 0.05, CU, root)
        tube(f"Handrail{k}", [(sx, 0.95, z_bot - 0.1), (sx, MEZ_Y + 0.95, z_top - 0.05), (sx, MEZ_Y + 1.0, z_top - 0.12)], 0.025, CU, root)

    # ---------------------------------------------------------------- ducts + vents (ceiling level)
    slab("DuctBack", X0, X1 + 1.5, WALL_H - 0.85, WALL_H - 0.25, Z0, Z0 + 0.6, DUCT, root, r=0.03)
    if not glass_left:
        slab("DuctLeft", X0, X0 + 0.6, WALL_H - 0.85, WALL_H - 0.25, Z0, Z1, DUCT, root, r=0.03)
    for i, x in enumerate((-5.2, -2.6, 0.2)):
        slab(f"DuctGrille{i}", x - 0.6, x + 0.6, WALL_H - 0.75, WALL_H - 0.35, Z0 + 0.6, Z0 + 0.62, VENT, root)
        for j in range(5):
            slab(f"DuctSlat{i}_{j}", x - 0.58, x + 0.58, WALL_H - 0.72 + j * 0.075, WALL_H - 0.7 + j * 0.075, Z0 + 0.62, Z0 + 0.64, DUCT, root)
    # round wall vents
    for i, (x, y) in enumerate(((0.9, 4.7), (6.6, 4.3), (-1.0, 1.9))):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.08, vertices=8)
        o = bpy.context.active_object
        o.name = f"WallVent{i}"
        o.location = P(x, y, Z0 + 0.04)
        o.rotation_euler = (math.pi / 2, 0, math.pi / 8)
        o.data.materials.append(VENT)
        o.parent = root

    # ---------------------------------------------------------------- pipework
    # lower-level ceiling run along the back wall, dropping into the right corner
    tube("PipeBackLow", [(X0, MEZ_Y - MEZ_T - 0.15, Z0 + 0.2), (6.4, MEZ_Y - MEZ_T - 0.15, Z0 + 0.2), (6.6, MEZ_Y - MEZ_T - 0.35, Z0 + 0.2), (6.6, 0.0, Z0 + 0.2)], 0.07, PIPE, root)
    tube("PipeBackLow2", [(X0, MEZ_Y - MEZ_T - 0.32, Z0 + 0.38), (6.1, MEZ_Y - MEZ_T - 0.32, Z0 + 0.38), (6.3, MEZ_Y - MEZ_T - 0.5, Z0 + 0.38), (6.3, 0.0, Z0 + 0.38)], 0.09, PIPE, root)
    # thick vertical pair in the lower right corner
    for k, x in enumerate((6.75, 6.45)):
        tube(f"RiserPipe{k}", [(x, 0, Z0 + 0.9 + k * 0.3), (x, MEZ_Y - MEZ_T, Z0 + 0.9 + k * 0.3)], 0.14, PIPE, root)
    # pipe running under the slab edge and bending down a column
    tube("PipeEdge", [(X0, MEZ_Y - MEZ_T - 0.1, MEZ_Z - 0.4), (0.7, MEZ_Y - MEZ_T - 0.1, MEZ_Z - 0.4), (0.85, MEZ_Y - MEZ_T - 0.25, MEZ_Z - 0.4), (0.85, 0.06, MEZ_Z - 0.4)], 0.06, RUST, root)
    # upper level: pipes along the top of the back wall and down the left corner
    tube("PipeUpperBack", [(X0 + 0.2, WALL_H - 1.05, Z0 + 0.25), (X1 + 1.5, WALL_H - 1.05, Z0 + 0.25)], 0.08, PIPE, root)
    tube("PipeUpperCorner", [(X0 + 0.25, MEZ_Y, Z0 + 0.25), (X0 + 0.25, WALL_H - 1.05, Z0 + 0.25)], 0.08, PIPE, root)
    tube("PipeUpperRight", [(1.5, MEZ_Y + 0.25, Z0 + 0.2), (6.9, MEZ_Y + 0.25, Z0 + 0.2)], 0.06, RUST, root)
    tube("PipeUpperRight2", [(1.5, MEZ_Y + 0.42, Z0 + 0.2), (6.9, MEZ_Y + 0.42, Z0 + 0.2)], 0.06, RUST, root)

    # ---------------------------------------------------------------- big window (upper right, yellow glow)
    wx0, wx1, wy0, wy1 = 1.8, 6.4, 4.0, 6.0
    c = 0.35  # chamfered corners
    slab("WindowGlow", wx0, wx1, wy0, wy1, Z0 - 0.02, Z0 + 0.005, WINDOW, root)
    FR = STEEL
    slab("WindowFrameTop", wx0, wx1, wy1, wy1 + 0.2, Z0, Z0 + 0.22, FR, root)
    slab("WindowFrameBottom", wx0, wx1, wy0 - 0.2, wy0, Z0, Z0 + 0.28, FR, root)
    slab("WindowFrameLeft", wx0 - 0.2, wx0, wy0 - 0.2, wy1 + 0.2, Z0, Z0 + 0.22, FR, root)
    slab("WindowFrameRight", wx1, wx1 + 0.2, wy0 - 0.2, wy1 + 0.2, Z0, Z0 + 0.22, FR, root)
    for i, (cx, cy, rot) in enumerate(((wx0, wy1, -45), (wx1, wy1, 45), (wx0, wy0, 45), (wx1, wy0, -45))):
        o = block(f"WindowChamfer{i}", (cx, cy, Z0 + 0.11), (c * 1.45, 0.22, 0.22), FR, root)
        o.rotation_euler = (0, math.radians(rot), 0)

    # ---------------------------------------------------------------- lower level features
    # orange-lit doorway (lower right), recessed into the back wall
    dx0, dx1 = 4.6, 6.0
    slab("DoorwayGlow", dx0, dx1, 0, 2.5, Z0 - 0.29, Z0 - 0.27, DOOR_GLOW, root)
    slab("DoorJambL", dx0 - 0.12, dx0, 0, 2.62, Z0 - 0.3, Z0 + 0.06, STEEL, root)
    slab("DoorJambR", dx1, dx1 + 0.12, 0, 2.62, Z0 - 0.3, Z0 + 0.06, STEEL, root)
    slab("DoorHead", dx0 - 0.12, dx1 + 0.12, 2.5, 2.62, Z0 - 0.3, Z0 + 0.06, STEEL, root)
    # blue alcove (lower middle): painted wall section + side fins
    slab("BlueAlcove", -0.6, 2.4, 0, MEZ_Y - MEZ_T, Z0, Z0 + 0.03, BLUE_WALL, root)
    slab("AlcoveFinL", -0.72, -0.6, 0, MEZ_Y - MEZ_T, Z0, Z0 + 0.9, CONCRETE, root)
    # pink strip on the lower left wall (kitchen accent) + teal shelf strip upstairs
    if not glass_left:
        slab("KitchenStrip", X0 + 0.04, X0 + 0.07, 1.55, 1.58, -5.6, -3.2, STRIP_PINK, root)
    slab("ShelfStripTeal", -6.6, -3.0, MEZ_Y + 1.6, MEZ_Y + 1.63, Z0 + 0.04, Z0 + 0.07, STRIP_TEAL, root)

    # ---------------------------------------------------------------- zone markers (for placing furniture + lights)
    zones = {
        "Zone_Workstation": (-4.6, MEZ_Y, -4.6),
        "Zone_Arcades": (-0.9, MEZ_Y, -5.3),
        "Zone_Window": (4.1, MEZ_Y, -4.3),
        "Zone_Kitchen": (-6.1, 0, -4.2),
        "Zone_Bar": (-1.2, 0, -1.4),
        "Zone_Alcove": (0.9, 0, -5.4),
        "Zone_Doorway": (5.3, 0, -4.6),
        "Zone_Front": (0.5, 0, 1.8),
    }
    for n, pos in zones.items():
        empty(n, pos, root)

    return root
