"""
Racing-style gaming chair: black leather shell with winged high back,
quilted-look centre panels, red piping, 4D-style armrests, gas lift and a
5-star base with twin-wheel casters. No brand logos.

    build_gaming_chair(parent=None, name="GamingChair") -> root empty

Coordinates are three.js style (Y up, chair faces +Z, origin on the floor
under the gas lift). Seat top is at ~0.51 m so the seated characters fit.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from character import P, _hex, capsule, rounded_box  # noqa: E402

SEAT_TOP = 0.51

_M = {}


def mat(name, color, rough=0.5, metal=0.0, sheen=False):
    key = "Chair_" + name
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
    if sheen and "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = 0.15  # faint leather gloss
        b.inputs["Coat Roughness"].default_value = 0.35
    m.diffuse_color = (*_hex(color), 1)
    _M[key] = m
    return m


def _link(o, name, m, parent):
    o.name = name
    if m:
        o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def _curve_from_outline(name, outline, cyclic=True):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D" if cyclic else "3D"
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(outline) - 1)
    for bp, (x, y) in zip(sp.bezier_points, outline):
        bp.co = (x, y, 0)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    sp.use_cyclic_u = cyclic
    return cu


def _to_mesh(ob):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.shade_smooth()
    return bpy.context.active_object


def slab(name, outline, half_thickness, bevel, m, parent, loc, orient="upright", tilt=0.0):
    """
    A cushion-like slab: a smooth 2D outline, given thickness, with rounded edges.
    orient="upright": outline is (x, y) in the chair's front plane, thickness along +Z (front).
    orient="flat":    outline is (x, z) on the ground plane, thickness along +Y (up).
    tilt: lean back angle (radians) for upright slabs, pivoting at the slab's local origin.
    """
    if orient == "flat":
        outline = [(x, -z) for x, z in outline]  # three z -> blender -y
    cu = _curve_from_outline(name, outline)
    cu.fill_mode = "BOTH"
    cu.extrude = half_thickness
    cu.bevel_depth = bevel
    cu.bevel_resolution = 4
    ob = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(ob)
    ob.location = P(*loc)
    if orient == "upright":
        ob.rotation_euler = (math.pi / 2 + tilt, 0, 0)
    ob = _to_mesh(ob)
    return _link(ob, name, m, parent)


def piping(name, outline, radius, m, parent, loc, orient="upright", tilt=0.0, offset=0.0, closed=True):
    """Thin tube following an outline: the red stitching / piping. offset pushes it off the face."""
    if orient == "flat":
        outline = [(x, -z) for x, z in outline]
    cu = _curve_from_outline(name, outline, cyclic=closed)
    cu.dimensions = "3D"
    for bp in cu.splines[0].bezier_points:
        bp.co.z = offset
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    ob = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(ob)
    ob.location = P(*loc)
    if orient == "upright":
        ob.rotation_euler = (math.pi / 2 + tilt, 0, 0)
    ob = _to_mesh(ob)
    return _link(ob, name, m, parent)


def scaled(outline, sx, sy, dy=0.0):
    return [(x * sx, y * sy + dy) for x, y in outline]


def cylinder(name, c, r, h, m, parent, axis="y", yaw=0.0, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts)
    o = bpy.context.active_object
    o.location = P(*c)
    if axis == "x":  # wheel axle across the leg
        o.rotation_euler = (0, math.pi / 2, yaw)
    else:
        o.rotation_euler = (0, 0, yaw)
    bpy.ops.object.shade_smooth()
    return _link(o, name, m, parent)


# ---------------------------------------------------------------- outlines
# Backrest silhouette (x, y), y=0 at the bottom of the back. Racing-seat shape:
# narrow waist, flared shoulder wings, tall head section.
BACK = [
    (0.0, -0.01), (0.22, 0.0), (0.245, 0.12), (0.23, 0.3), (0.25, 0.46),
    (0.275, 0.6), (0.27, 0.68), (0.2, 0.72), (0.175, 0.8), (0.17, 0.9),
    (0.12, 0.95), (0.0, 0.96),
    (-0.12, 0.95), (-0.17, 0.9), (-0.175, 0.8), (-0.2, 0.72), (-0.27, 0.68),
    (-0.275, 0.6), (-0.25, 0.46), (-0.23, 0.3), (-0.245, 0.12), (-0.22, 0.0),
]
# centre panel of the backrest (the inset with the piping round it)
BACK_INSET = [
    (0.0, 0.05), (0.13, 0.06), (0.15, 0.3), (0.155, 0.52), (0.13, 0.64),
    (0.11, 0.72), (0.11, 0.86), (0.0, 0.89),
    (-0.11, 0.86), (-0.11, 0.72), (-0.13, 0.64), (-0.155, 0.52), (-0.15, 0.3), (-0.13, 0.06),
]
# seat (x, z), z+ = front edge
SEAT = [
    (0.0, -0.25), (0.22, -0.24), (0.26, -0.1), (0.255, 0.12), (0.22, 0.25),
    (0.0, 0.27), (-0.22, 0.25), (-0.255, 0.12), (-0.26, -0.1), (-0.22, -0.24),
]
SEAT_INSET = [
    (0.0, -0.2), (0.14, -0.19), (0.155, 0.05), (0.14, 0.2), (0.0, 0.22),
    (-0.14, 0.2), (-0.155, 0.05), (-0.14, -0.19),
]


def build_gaming_chair(parent=None, name="GamingChair", accent="#8a1820"):
    LEATHER = mat("Leather", "#0a0a0b", 0.38, sheen=True)
    PANEL = mat("PanelFabric", "#151517", 0.9)
    PIPING = mat("Piping", accent, 0.5)
    PLASTIC = mat("Plastic", "#0d0d0e", 0.55)
    METAL = mat("Metal", "#2b2b2e", 0.3, metal=0.9)
    CHROME = mat("Chrome", "#9a9aa0", 0.15, metal=1.0)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- seat cushion with raised side bolsters
    seat_y = SEAT_TOP - 0.055
    slab("Seat", SEAT, 0.035, 0.03, LEATHER, root, (0, seat_y, 0), orient="flat")
    slab("SeatInset", SEAT_INSET, 0.006, 0.012, PANEL, root, (0, seat_y + 0.062, 0), orient="flat")
    piping("SeatPiping", scaled(SEAT_INSET, 1.06, 1.05), 0.0035, PIPING, root,
           (0, seat_y + 0.066, 0), orient="flat")
    for s in (-1, 1):
        capsule(f"SeatBolster{s}", (s * 0.215, SEAT_TOP + 0.005, -0.2), (s * 0.215, SEAT_TOP + 0.01, 0.19),
                0.04, LEATHER, root)
    # seat pan underneath
    rounded_box("SeatPan", (0, seat_y - 0.06, -0.01), (0.46, 0.05, 0.46), 0.02, PLASTIC, root)

    # ---------- backrest (tilted back), with centre panel + piping + rear shell
    tilt = -0.16
    back_loc = (0, SEAT_TOP - 0.02, -0.27)
    slab("Backrest", BACK, 0.035, 0.025, LEATHER, root, back_loc, tilt=tilt)
    # Directions of the leaned-back backrest, in three.js axes
    fwd = Vector((0, math.sin(-tilt), math.cos(-tilt)))  # out of the front face
    up = Vector((0, math.cos(-tilt), -math.sin(-tilt)))  # along the back, toward the headrest

    def bpt(x, y, f):
        """Point on the backrest: x across, y up the back, f out of the front face."""
        v = Vector(back_loc) + up * y + fwd * f
        return (x, v.y, v.z)

    front = 0.058
    inset_loc = bpt(0, 0, front)
    slab("BackInset", BACK_INSET, 0.006, 0.012, PANEL, root, inset_loc, tilt=tilt)
    piping("BackPiping", scaled(BACK_INSET, 1.07, 1.02, -0.01), 0.0035, PIPING, root,
           inset_loc, tilt=tilt, offset=0.02)
    # racing-seat side bolsters that wrap around the torso
    for s in (-1, 1):
        capsule(f"BackBolsterLow{s}", bpt(s * 0.205, 0.07, 0.055), bpt(s * 0.198, 0.3, 0.06), 0.048, LEATHER, root,
                r2=0.045)
        capsule(f"BackBolsterHigh{s}", bpt(s * 0.198, 0.3, 0.06), bpt(s * 0.232, 0.56, 0.05), 0.045, LEATHER, root,
                r2=0.036)
        piping(f"BolsterPiping{s}", [(s * 0.165, 0.07), (s * 0.16, 0.3), (s * 0.19, 0.56)], 0.003, PIPING, root,
               back_loc, tilt=tilt, offset=0.1, closed=False)
    rear = 0.04
    slab("BackShell", scaled(BACK, 0.97, 0.985, 0.008), 0.01, 0.012, PLASTIC, root, bpt(0, 0, -rear), tilt=tilt)
    # recline brackets joining seat and back
    for s in (-1, 1):
        rounded_box(f"BackBracket{s}", (s * 0.235, SEAT_TOP - 0.1, -0.2), (0.025, 0.16, 0.16), 0.01, METAL, root)

    # ---------- armrests (post + pad)
    for s in (-1, 1):
        x = s * 0.3
        rounded_box(f"ArmBracket{s}", (s * 0.255, SEAT_TOP - 0.13, -0.04), (0.11, 0.03, 0.09), 0.01, METAL, root)
        rounded_box(f"ArmPost{s}", (x, SEAT_TOP + 0.02, -0.04), (0.045, 0.28, 0.07), 0.012, PLASTIC, root)
        rounded_box(f"ArmPad{s}", (x, SEAT_TOP + 0.175, -0.01), (0.095, 0.035, 0.26), 0.015, PLASTIC, root)

    # ---------- mechanism, gas lift, base, casters
    rounded_box("Mechanism", (0, SEAT_TOP - 0.15, -0.02), (0.22, 0.06, 0.26), 0.015, METAL, root)
    rounded_box("TiltLever", (0.15, SEAT_TOP - 0.16, 0.06), (0.12, 0.012, 0.025), 0.005, PLASTIC, root)
    cylinder("GasLift", (0, 0.27, 0), 0.026, 0.2, CHROME, root)
    cylinder("GasShroud", (0, 0.17, 0), 0.042, 0.16, PLASTIC, root)
    cylinder("BaseHub", (0, 0.11, 0), 0.06, 0.06, PLASTIC, root)

    for i in range(5):
        a = i * 2 * math.pi / 5
        dx, dz = math.sin(a), math.cos(a)
        leg = rounded_box(f"BaseLeg{i}", (0.18 * dx, 0.1, 0.18 * dz), (0.065, 0.045, 0.34), 0.018, PLASTIC, root,
                          rx=0.1)
        leg.rotation_euler = (0.1, 0, a)
        # caster: fork + twin wheels
        cx, cz = 0.33 * dx, 0.33 * dz
        rounded_box(f"CasterFork{i}", (cx, 0.07, cz), (0.045, 0.04, 0.05), 0.008, PLASTIC, root).rotation_euler = (0, 0, a)
        for w in (-1, 1):
            ox, oz = w * 0.016 * dz, -w * 0.016 * dx  # spread wheels across the leg
            cylinder(f"Wheel{i}_{w}", (cx + ox, 0.032, cz + oz), 0.032, 0.018, PLASTIC, root, axis="x", yaw=a)

    return root
