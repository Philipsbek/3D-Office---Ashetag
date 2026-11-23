"""
Razer-style ergonomic RGB gaming mouse (Basilisk / DeathAdder-inspired):
right-handed sculpted shell with a rear hump and thumb groove, split main
buttons, RGB scroll wheel, DPI button, two thumb buttons, a glowing palm
emblem (plain shape, no logo) and Chroma underglow around the base.

    build_razer_mouse(parent=None, name="RazerMouse") -> root empty

Coordinates are three.js style (Y up, the user is on the +Z side so the
mouse points toward -Z, origin on the desk under the mouse's centre).
Glowing parts use the shared "Razer_ChromaRGB" rainbow material.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from gaming_desk import tube  # noqa: E402
from razer_keyboard import chroma_mat, uv_by_x  # noqa: E402
from razer_monitor import mat  # noqa: E402

L, W, H = 0.128, 0.068, 0.043  # length, width, height (m)


def _shell(name, m):
    """Sculpt a UV sphere into an ergonomic right-handed mouse shell."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=64, ring_count=32)
    ob = bpy.context.active_object
    ob.name = name
    for v in ob.data.vertices:
        # unit sphere in three.js terms: X right, Y up, Z toward the user (rear of the mouse)
        X, Y, Z = v.co.x, v.co.z, -v.co.y
        if Y < -0.35:  # flat base
            Y = -0.35 + (Y + 0.35) * 0.08
        Y += 0.36
        Y *= 0.52 + 0.48 * math.exp(-((Z - 0.28) / 0.72) ** 2)  # hump toward the palm
        X *= 0.8 + 0.2 * (Z + 1) / 2  # narrower nose, wider palm
        if X < 0:  # thumb groove on the left flank
            X *= 1 - 0.16 * math.exp(-((Z - 0.0) / 0.42) ** 2) * math.exp(-((Y - 0.42) / 0.28) ** 2)
        elif Y < 0.35:  # slight flare under the ring/pinky fingers
            X *= 1.05
        X, Y, Z = X * W / 2, Y * H / 1.36, Z * L / 2
        v.co = (X, -Z, Y)
    bpy.ops.object.shade_smooth()
    sub = ob.modifiers.new("Smooth", "SUBSURF")
    sub.levels = 1  # 64x32 sphere is already round; level 2 quadrupled the size for no visible gain
    bpy.ops.object.modifier_apply(modifier="Smooth")  # apply first so parts placed by ray-cast sit flush
    ob.data.materials.append(m)
    return ob


def _hit(ob, origin, direction):
    """Ray-cast in three.js coords against the shell; returns (point, normal) in three.js coords."""
    o, d = P(*origin), P(*direction)
    ok, loc, nor, _ = ob.ray_cast(o, d.normalized())
    if not ok:
        raise RuntimeError(f"ray missed the mouse shell from {origin}")
    return (loc.x, loc.z, -loc.y), Vector((nor.x, nor.z, -nor.y))


def top(ob, x, z):
    return _hit(ob, (x, 1.0, z), (0, -1, 0))


def side(ob, sgn, y, z):
    return _hit(ob, (sgn * 1.0, y, z), (-sgn, 0, 0))


def _oriented(o, point, normal, lift=0.0):
    p = Vector(point) + normal * lift
    o.location = P(*p)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = P(*normal).to_track_quat("Z", "Y")


def build_razer_mouse(parent=None, name="RazerMouse"):
    BODY = mat("MouseBody", "#0b0b0c", 0.55)
    GROOVE = mat("MouseGroove", "#000000", 0.8)
    RUBBER = mat("MouseRubber", "#141416", 0.85)
    RGB = chroma_mat(5.0)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)

    shell = _shell("MouseShell", BODY)
    bpy.context.view_layer.update()

    parts = []

    # split line between the two main buttons, and the button/palm seam
    pts = [top(shell, 0.0, -L / 2 * k)[0] for k in (0.97, 0.8, 0.6, 0.4, 0.22)]
    parts.append(tube("ButtonSplit", [(x, y + 0.0004, z) for x, y, z in pts], 0.0007, GROOVE, None))
    seam = []
    for i in range(13):  # stays on the top surface (wider would run down the flanks)
        x = -W / 2 * 0.5 + (W * 0.5) * i / 12
        p, _ = top(shell, x, -L / 2 * 0.2 + 0.006 * math.cos(x / W * math.pi))
        seam.append((p[0], p[1] + 0.0004, p[2]))
    parts.append(tube("ButtonSeam", seam, 0.0006, GROOVE, None))

    # scroll wheel sitting in a slot, with an RGB stripe
    wz = -L / 2 * 0.58
    (wx, wy, _), _ = top(shell, 0.0, wz)
    bpy.ops.mesh.primitive_cube_add(size=1)
    slot = bpy.context.active_object
    slot.name = "WheelSlot"
    slot.location = P(0, wy - 0.0024, wz)  # sunk into the shell: only a dark rim shows
    slot.scale = (0.0105, 0.021, 0.004)  # blender: x, y(=three z), z(=three y)
    slot.data.materials.append(GROOVE)
    slot.scale = (0.0095, 0.018, 0.003)
    parts.append(slot)
    for nm, r, width, m in (("ScrollWheel", 0.0105, 0.0075, RUBBER), ("WheelRGB", 0.0107, 0.0016, RGB)):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=width, vertices=40)
        c = bpy.context.active_object
        c.name = nm
        c.location = P(0, wy - 0.0035, wz)
        c.rotation_euler = (0, math.pi / 2, 0)
        bpy.ops.object.shade_smooth()
        c.data.materials.append(m)
        parts.append(c)

    # DPI button behind the wheel
    (dx, dy, dz), dn = top(shell, 0.0, -L / 2 * 0.3)
    bpy.ops.mesh.primitive_cube_add(size=1)
    dpi = bpy.context.active_object
    dpi.name = "DPIButton"
    _oriented(dpi, (dx, dy, dz), dn, 0.0006)
    dpi.scale = (0.0045, 0.0075, 0.0012)
    dpi.data.materials.append(RUBBER)
    parts.append(dpi)

    # two thumb buttons on the left flank
    for i, z in enumerate((-0.022, 0.004)):
        p, n = side(shell, -1, H * 0.62, z)
        bpy.ops.mesh.primitive_cube_add(size=1)
        b = bpy.context.active_object
        b.name = f"ThumbButton{i}"
        _oriented(b, p, n, 0.0012)
        b.scale = (0.011, 0.005, 0.0022)
        mod = b.modifiers.new("Round", "BEVEL")
        mod.width = 0.0015
        mod.segments = 2
        b.data.materials.append(RUBBER)
        parts.append(b)

    # glowing palm emblem (plain rounded shape, no logo)
    p, n = top(shell, 0.0, L / 2 * 0.42)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0062, depth=0.0008, vertices=6)
    emb = bpy.context.active_object
    emb.name = "PalmGlow"
    _oriented(emb, p, n, 0.0006)
    emb.scale = (1.0, 1.25, 1.0)
    emb.data.materials.append(RGB)
    parts.append(emb)

    # Chroma underglow ring hugging the base
    ring = []
    for i in range(96):
        a = 2 * math.pi * i / 96
        d = (math.sin(a), 0.0, math.cos(a))
        pnt, _ = _hit(shell, (d[0] * 0.3, 0.003, d[2] * 0.3), (-d[0], 0, -d[2]))
        ring.append((pnt[0] + d[0] * 0.0012, 0.0022, pnt[2] + d[2] * 0.0012))
    ring.append(ring[0])
    glow = tube("MouseUnderglow", ring, 0.0016, RGB, None)
    uv_by_x(glow, -W / 2, W / 2)
    parts.append(glow)

    # parent everything
    for o in [shell] + parts:
        o.parent = root
    if parent:
        root.parent = parent
    return root
