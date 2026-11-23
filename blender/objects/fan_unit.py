"""
Industrial wall fan unit: a tall steel cabinet with two big exhaust fans
stacked on its front, wire grilles, side louvres, corner bolts, a conduit and
a red status light. Stands in the upper-left workstation corner of the loft.

    build_fan_unit(parent=None, name="FanUnit") -> root empty

Coordinates are three.js style (Y up, fans face +Z, origin at the centre of
the base on the floor). Each fan's blades sit under an empty named
"FanRotor0" / "FanRotor1" whose local Y axis (Blender) is the spin axis, so
the website can spin them.
"""

import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

W, H, D = 1.3, 2.4, 0.62  # cabinet width, height, depth
FAN_R = 0.5  # blade tip radius


def _open_cylinder(name, c, r, depth, thickness, m, parent):
    """Hollow fan shroud: an open-ended tube facing +Z."""
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=48, end_fill_type="NOTHING")
    o = bpy.context.active_object
    o.name = name
    o.location = P(*c)
    o.rotation_euler = (math.pi / 2, 0, 0)
    sol = o.modifiers.new("Wall", "SOLIDIFY")
    sol.thickness = thickness
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    o.parent = parent
    return o


def _blade(name, m):
    """One fan blade: a thin slab along +X (Blender), thickness along Y, width along Z."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = (FAN_R - 0.1, 0.012, 0.15)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # taper: narrow at the hub, wide at the tip, with rounded edges
    for v in o.data.vertices:
        t = (v.co.x + 0.5 * (FAN_R - 0.1)) / (FAN_R - 0.1)  # 0 at hub end, 1 at tip
        v.co.z *= 0.45 + 0.55 * t
    bev = o.modifiers.new("Round", "BEVEL")
    bev.width = 0.004
    bev.segments = 2
    o.data.materials.append(m)
    return o


def _fan(i, cy, root, M):
    cz = D / 2  # front face of the cabinet
    # recessed square bay + dark back plate so you can't see into the cabinet
    block(f"FanBay{i}", (0, cy, cz - 0.01), (W - 0.14, W - 0.14, 0.04), M["bay"], root, r=0.01)
    disc(f"FanBackPlate{i}", (0, cy, cz + 0.01), FAN_R + 0.04, 0.01, M["void"], root, axis="z", verts=48)
    _open_cylinder(f"FanShroud{i}", (0, cy, cz + 0.08), FAN_R + 0.05, 0.16, 0.025, M["steel"], root)
    ring(f"FanLip{i}", (0, cy, cz + 0.16), FAN_R + 0.065, 0.025, M["steel"], root, axis="z")
    # bolts in the bay corners
    for k, (bx, by) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        disc(f"FanBolt{i}_{k}", (bx * (W / 2 - 0.13), cy + by * (W / 2 - 0.13), cz + 0.02), 0.025, 0.02, M["bolt"], root, axis="z", verts=6)

    # rotor: hub + 9 pitched blades, under an empty the site can spin
    rotor = bpy.data.objects.new(f"FanRotor{i}", None)
    bpy.context.collection.objects.link(rotor)
    rotor.location = P(0, cy, cz + 0.07)
    rotor.parent = root
    disc(f"FanHub{i}", (0, 0, 0), 0.1, 0.07, M["hub"], rotor, axis="z", verts=32)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, segments=24, ring_count=12)
    nose = bpy.context.active_object
    nose.name = f"FanNose{i}"
    nose.scale = (1, 0.6, 1)
    nose.location = (0, -0.035, 0)
    bpy.ops.object.shade_smooth()
    nose.data.materials.append(M["hub"])
    nose.parent = rotor
    blades = 9
    pitch = math.radians(28)
    for b in range(blades):
        bl = _blade(f"FanBlade{i}_{b}", M["blade"])
        bl.parent = rotor
        ang = 2 * math.pi * b / blades
        # spin axis is Blender Y (the fan faces -Y in Blender = +Z in three.js)
        bl.matrix_basis = (
            Matrix.Rotation(ang, 4, "Y")
            @ Matrix.Translation(((FAN_R - 0.1) / 2 + 0.07, 0, 0))
            @ Matrix.Rotation(pitch, 4, "X")
        )

    # wire grille in front: concentric rings + spokes
    gz = cz + 0.17
    for k, r in enumerate((0.12, 0.24, 0.36, 0.48)):
        ring(f"FanGrilleRing{i}_{k}", (0, cy, gz), r, 0.006, M["grille"], root, axis="z")
    for k in range(8):
        a = math.pi * k / 4
        tube(f"FanGrilleSpoke{i}_{k}", [(0.06 * math.cos(a), cy + 0.06 * math.sin(a), gz),
                                        ((FAN_R + 0.05) * math.cos(a), cy + (FAN_R + 0.05) * math.sin(a), gz)],
             0.006, M["grille"], root)
    disc(f"FanGrilleBadge{i}", (0, cy, gz + 0.004), 0.06, 0.01, M["grille"], root, axis="z", verts=24)


def build_fan_unit(parent=None, name="FanUnit"):
    M = {
        "body": mat("FanBody", "#2b2d30", 0.55, metal=0.6),
        "bay": mat("FanBay", "#1a1b1d", 0.6, metal=0.4),
        "void": mat("FanVoid", "#050505", 0.9),
        "steel": mat("FanSteel", "#45484c", 0.35, metal=0.85),
        "blade": mat("FanBlade", "#b9bcbf", 0.3, metal=0.8),
        "hub": mat("FanHub", "#6d7074", 0.3, metal=0.9),
        "grille": mat("FanGrille", "#16171a", 0.4, metal=0.7),
        "bolt": mat("FanBolt", "#7a7d80", 0.3, metal=0.9),
        "louvre": mat("FanLouvre", "#202224", 0.5, metal=0.5),
        "led": mat("FanLED", "#ff2a2a", emit="#ff2a2a", strength=8),
        "conduit": mat("FanConduit", "#1c1d1f", 0.5, metal=0.6),
    }
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # cabinet: plinth, body, top lip, front frame edges
    block("FanPlinth", (0, 0.05, 0), (W - 0.06, 0.1, D - 0.06), M["void"], root, r=0.01)
    block("FanCabinet", (0, H / 2 + 0.05, 0), (W, H - 0.1, D), M["body"], root, r=0.015)
    block("FanTopLip", (0, H + 0.01, 0), (W + 0.04, 0.04, D + 0.04), M["steel"], root, r=0.01)
    block("FanMidRail", (0, 0.1 + (H - 0.1) / 2, D / 2 + 0.01), (W, 0.05, 0.03), M["steel"], root, r=0.005)

    # two fans, one in each half of the front
    half = (H - 0.1) / 2
    _fan(0, 0.1 + half * 0.5, root, M)
    _fan(1, 0.1 + half * 1.5, root, M)

    # side louvres (both sides)
    for s, sx in enumerate((-1, 1)):
        for k in range(10):
            y = 0.45 + k * 0.17
            louv = block(f"FanLouvre{s}_{k}", (sx * (W / 2 + 0.012), y, 0), (0.025, 0.035, D - 0.18), M["louvre"], root, r=0.004)
            louv.rotation_euler = (0, 0, 0)

    # status panel with a red LED, and a conduit running up from the side
    block("FanPanel", (W / 2 - 0.16, H - 0.12, D / 2 + 0.012), (0.2, 0.1, 0.02), M["bay"], root, r=0.004)
    block("FanLED", (W / 2 - 0.1, H - 0.12, D / 2 + 0.026), (0.025, 0.025, 0.01), M["led"], root)
    tube("FanConduit", [(W / 2 + 0.04, 0.0, -D / 2 + 0.12), (W / 2 + 0.04, H - 0.3, -D / 2 + 0.12),
                        (W / 2 + 0.04, H + 0.25, -D / 2 + 0.12)], 0.035, M["conduit"], root)
    for k, y in enumerate((0.6, 1.4, 2.1)):
        block(f"FanConduitClip{k}", (W / 2 + 0.03, y, -D / 2 + 0.12), (0.05, 0.04, 0.09), M["steel"], root)
    # stub exhaust pipes out of the top
    disc("FanTopPipe0", (-0.3, H + 0.15, -0.1), 0.07, 0.3, M["steel"], root, axis="y")
    disc("FanTopPipe1", (0.0, H + 0.12, -0.1), 0.05, 0.24, M["steel"], root, axis="y")

    return root
