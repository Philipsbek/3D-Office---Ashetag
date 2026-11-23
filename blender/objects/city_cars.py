"""
Cyberpunk supercar for the outside city (style ref: low wedge supercar,
orange-red paint over a dark lower body, vertical LED bars on the front
corners, solid aero discs on the front wheels, dark spoked rear rims).
Original design, not a copy of any specific vehicle.

    build_street_car(parent=None, name="StreetCar", paint="#c23a1c", hover=False)
        ~4.7 m long; hover=True swaps wheels for glowing thruster pods
        (sky-lane variant).
    build_cars_preview(parent, name) -> orange car, dark car, hover car

Origin on the ground under the middle of the car; the car faces +X.
Coordinates are three.js style (Y up).
"""

import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import disc  # noqa: E402
from loft_room import block, mat  # noqa: E402
from city_street import _M as street_mats  # noqa: E402

# body stations from nose (+X) to tail: x, half width, bottom, belt, roof-edge half width, top
STATIONS = [
    (2.32, 0.86, 0.22, 0.50, 0.70, 0.56),
    (2.10, 0.97, 0.16, 0.62, 0.82, 0.68),
    (1.60, 1.00, 0.15, 0.74, 0.84, 0.77),
    (1.05, 0.99, 0.15, 0.78, 0.80, 0.81),
    (0.62, 0.97, 0.15, 0.80, 0.72, 0.86),
    (0.05, 0.96, 0.15, 0.82, 0.58, 1.13),
    (-0.55, 0.98, 0.15, 0.84, 0.56, 1.12),
    (-1.15, 1.03, 0.15, 0.88, 0.70, 0.99),
    (-1.75, 1.05, 0.16, 0.92, 0.86, 0.95),
    (-2.22, 1.00, 0.20, 0.90, 0.86, 0.92),
    (-2.36, 0.94, 0.26, 0.86, 0.80, 0.88),
]
WHEEL_X, WHEEL_R = 1.47, 0.37


def _root(name, parent):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    return root


def _body_mesh(name, paint, lower, glass, parent):
    bm = bmesh.new()
    rings = []
    for x, hw, bot, belt, tw, top in STATIONS:
        pts = [(0, top), (tw, top - 0.03), (hw, belt), (hw, bot + 0.14), (hw - 0.12, bot), (0, bot - 0.01)]
        pts = pts + [(-pz, py) for pz, py in reversed(pts[1:-1])]
        rings.append([bm.verts.new(P(x, py, pz)) for pz, py in pts])
    n = len(rings[0])
    for i in range(len(rings) - 1):
        xm = (STATIONS[i][0] + STATIONS[i + 1][0]) / 2
        for j in range(n):
            f = bm.faces.new((rings[i][j], rings[i][(j + 1) % n], rings[i + 1][(j + 1) % n], rings[i + 1][j]))
            band = j if j < n // 2 else n - 1 - j  # mirrored band index
            mi = 0
            if band in (3, 4):
                mi = 1  # dark lower body
            elif band == 1 and -1.75 < xm < 0.62:
                mi = 2  # side glass
            elif band == 0 and (0.0 < xm < 0.62 or -1.15 < xm < -0.55):
                mi = 2  # windscreen / rear glass
            f.material_index = mi
    for r in (rings[0], rings[-1]):
        bm.faces.new(r).material_index = 1
    # sharp character lines: roof edge, belt line, sill and the nose / tail outlines
    crease = bm.edges.layers.float.get("crease_edge") or bm.edges.layers.float.new("crease_edge")
    sharp_j = {1, 2, 3, n - 2, n - 3, n - 4}
    for i in range(len(rings) - 1):
        for j in sharp_j:
            e = bm.edges.get((rings[i][j], rings[i + 1][j]))
            if e:
                e[crease] = 0.85
    for r in (rings[0], rings[-1]):
        for j in range(n):
            e = bm.edges.get((r[j], r[(j + 1) % n]))
            if e:
                e[crease] = 1.0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    for m in (paint, lower, glass):
        me.materials.append(m)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    sub = o.modifiers.new("Sub", "SUBSURF")
    sub.levels = 2
    bpy.ops.object.modifier_apply(modifier="Sub")
    # wheel arches cut out with cylinders
    for sx in (1, -1):
        for sz in (1, -1):
            bpy.ops.mesh.primitive_cylinder_add(radius=WHEEL_R + 0.07, depth=0.5, vertices=48)
            c = bpy.context.active_object
            c.location = P(sx * WHEEL_X, WHEEL_R + 0.02, sz * 1.02)
            c.rotation_euler = (math.pi / 2, 0, 0)
            bpy.context.view_layer.objects.active = o
            b = o.modifiers.new("Arch", "BOOLEAN")
            b.operation = "DIFFERENCE"
            b.object = c
            bpy.ops.object.modifier_apply(modifier="Arch")
            bpy.data.objects.remove(c, do_unlink=True)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
    o.parent = parent
    return o


def _sport_wheel(name, c, M, parent, cover, tyre, side):
    x, y, z = c
    disc(f"{name}Tyre", (x, y, z), WHEEL_R, 0.3, tyre, parent, axis="z", verts=40)
    face = z + side * 0.15
    if cover:  # solid aero disc in body colour with a dark hub
        disc(f"{name}Cover", (x, y, face - side * 0.01), WHEEL_R - 0.06, 0.02, cover, parent, axis="z", verts=40)
        disc(f"{name}CoverHub", (x, y, face + side * 0.02), 0.1, 0.02, M["trim"], parent, axis="z", verts=24)
    else:  # dark five-spoke rim
        disc(f"{name}Rim", (x, y, face - side * 0.02), WHEEL_R - 0.08, 0.02, M["trim"], parent, axis="z", verts=40)
        for k in range(5):
            a = 2 * math.pi * k / 5
            sp = block(f"{name}Spoke{k}", (x + 0.14 * math.cos(a), y + 0.14 * math.sin(a), face - side * 0.02), (0.26, 0.05, 0.02), M["metal"], parent)
            sp.rotation_euler = (0, 0, a)
        disc(f"{name}Hub", (x, y, face + side * 0.01), 0.07, 0.03, M["metal"], parent, axis="z", verts=24)


def build_street_car(parent=None, name="StreetCar", paint="#c23a1c", hover=False):
    M = street_mats()
    body = mat(f"CarPaint{paint[1:]}", paint, 0.22, metal=0.6)
    lower = mat("CarLower", "#121317", 0.4, metal=0.3)
    glass = mat("CarGlass", "#06080d", 0.04, metal=0.7)
    tyre = mat("CarTyre", "#0c0c0e", 0.85)
    led = mat("CarLED", "#ffffff", emit="#eaf4ff", strength=14.0)
    amber = mat("CarAmber", "#ffb040", emit="#ff9a20", strength=10.0)
    red = mat("CarTail", "#ff2030", emit="#ff2030", strength=10.0)
    thrust = mat("CarThrust", "#ff5cf0", emit="#ff5cf0", strength=10.0)
    root = _root(name, parent)
    _body_mesh(f"{name}Body", body, lower, glass, root)
    # dark front fascia + twin vertical LED bars on each front corner
    block(f"{name}Fascia", (2.27, 0.36, 0), (0.06, 0.2, 1.2), lower, root, r=0.02)
    for s in (-1, 1):
        for k, dz in enumerate((0.0, 0.11)):
            block(f"{name}LED{s}{k}", (2.33 - k * 0.03, 0.4, s * (0.6 + dz)), (0.06, 0.2, 0.03), led, root)
        block(f"{name}Amber{s}", (1.95, 0.32, s * 0.9), (0.18, 0.03, 0.03), amber, root)
        # dark lower door panel, intake behind the cockpit, side marker, mirror
        block(f"{name}DoorPanel{s}", (-0.15, 0.34, s * 0.95), (1.4, 0.22, 0.06), lower, root, r=0.01)
        block(f"{name}Intake{s}", (-0.95, 0.62, s * 1.0), (0.08, 0.32, 0.05), lower, root)
        block(f"{name}SideLight{s}", (-1.25, 0.72, s * 1.03), (0.1, 0.03, 0.02), amber, root)
        block(f"{name}Mirror{s}", (0.5, 0.87, s * 0.93), (0.12, 0.05, 0.08), lower, root, r=0.01)
    # thin red tail bar + rear diffuser
    block(f"{name}TailBar", (-2.37, 0.78, 0), (0.03, 0.05, 1.5), red, root)
    block(f"{name}Diffuser", (-2.25, 0.25, 0), (0.25, 0.12, 1.4), lower, root)
    for k, (sx, sz) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        if not hover:
            _sport_wheel(f"{name}Wheel{k}", (sx * WHEEL_X, WHEEL_R, sz * 0.8), M, root,
                         body if sx > 0 else None, tyre, sz)
        else:
            x, z = sx * WHEEL_X, sz * 0.8
            disc(f"{name}Pod{k}", (x, 0.3, z), 0.33, 0.24, lower, root, verts=32)
            disc(f"{name}PodRing{k}", (x, 0.3, z), 0.35, 0.05, M["metal"], root, verts=32)
            disc(f"{name}PodGlow{k}", (x, 0.17, z), 0.26, 0.02, thrust, root, verts=32)
    return root


def build_cars_preview(parent=None, name="CarsPreview"):
    root = _root(name, parent)
    M = street_mats()
    block(f"{name}Road", (0, 0.01, 0), (26, 0.02, 9), M["trim"], root)
    for k in range(6):
        block(f"{name}Lane{k}", (-11 + k * 4.4, 0.025, 0), (2.0, 0.01, 0.15), M["light"], root)
    for k, (paint, hover) in enumerate((("#c23a1c", False), ("#1d1f27", False), ("#c9ccd4", True))):
        car = build_street_car(root, f"{name}Car{k}", paint, hover)
        car.location = P(-k * 1.2, 1.4 if hover else 0, 3.2 - k * 3.2)

    for n, pos, col, e in (("FillL", (-5, 4, 6), (1.0, 0.8, 0.7), 2500), ("FillR", (6, 5, 6), (0.6, 0.6, 1.0), 2500),
                           ("Top", (0, 9, 0), (0.8, 0.75, 1.0), 2500), ("Rim", (0, 3, -8), (0.6, 0.4, 1.0), 2000)):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = col
        ld.energy = e
        ld.shadow_soft_size = 2.0
        lo = bpy.data.objects.new(n, ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)
    return root


def build_car_hero_preview(parent=None, name="CarHero", paint="#c23a1c", hover=False):
    """Single car on a road slab for a close 3/4 review shot."""
    root = _root(name, parent)
    M = street_mats()
    block(f"{name}Road", (0, 0.01, 0), (30, 0.02, 14), M["trim"], root)
    build_street_car(root, f"{name}Car", paint, hover)
    for n, pos, col, e in (("Key", (5, 4, 5), (1.0, 0.85, 0.75), 1500), ("Fill", (-4, 3, 4), (0.6, 0.6, 1.0), 900),
                           ("Top", (0, 6, 0), (0.9, 0.85, 1.0), 900), ("Back", (-3, 3, -5), (0.7, 0.4, 1.0), 1200)):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = col
        ld.energy = e
        ld.shadow_soft_size = 2.5
        lo = bpy.data.objects.new(n, ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)
    return root
