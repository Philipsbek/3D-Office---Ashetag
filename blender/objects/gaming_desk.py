"""
Gaming desk on a sit-stand frame, with its accessories ready at the sides:
a headphone hook with RGB headphones hanging on the right, and a cup holder
with a drink can on the left. Large desk mat on top, height-control panel
under the front edge. Monitor / keyboard / mouse are separate assets.

    build_gaming_desk(parent=None, name="GamingDesk", width=1.6, depth=0.75) -> root empty

Coordinates are three.js style (Y up, the user sits on the +Z side, origin on
the floor at the desk's centre). Desk top surface is at 0.75 m.
"""

import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from character import P, _hex, capsule, rounded_box  # noqa: E402

TOP_Y = 0.75

_M = {}


def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=1.0):
    key = "Desk_" + name
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


def _to_mesh(ob):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.shade_smooth()
    return bpy.context.active_object


def tube(name, pts, r, m, parent):
    """A round tube through a list of three.js points (headband, wires, brackets)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, pt in zip(sp.points, pts):
        v = P(*pt)
        p.co = (v.x, v.y, v.z, 1)
    ob = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(ob)
    ob = _to_mesh(ob)
    ob.name = name
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


def disc(name, c, r, h, m, parent, axis="y", verts=32):
    """Cylinder; axis 'y' = upright, 'z' = facing front/back, 'x' = facing sideways."""
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts)
    o = bpy.context.active_object
    o.location = P(*c)
    o.rotation_euler = {"y": (0, 0, 0), "z": (math.pi / 2, 0, 0), "x": (0, math.pi / 2, 0)}[axis]
    bpy.ops.object.shade_smooth()
    o.name = name
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def ring(name, c, major, minor, m, parent, axis="y"):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=40, minor_segments=12)
    o = bpy.context.active_object
    o.location = P(*c)
    o.rotation_euler = {"y": (0, 0, 0), "z": (math.pi / 2, 0, 0), "x": (0, math.pi / 2, 0)}[axis]
    bpy.ops.object.shade_smooth()
    o.name = name
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def build_headphones(root, hx, hook_y, hz, M):
    """Over-ear headphones hanging by the headband from a hook arm at height hook_y."""
    R = 0.085  # headband radius
    band_r = 0.011
    cy = hook_y + 0.008 + band_r - R  # band's inner top rests on the arm
    pts = []
    for i in range(29):
        th = -0.45 + (math.pi + 0.9) * i / 28  # a bit more than a half circle
        pts.append((hx, cy + R * math.sin(th), hz + R * math.cos(th)))
    tube("HeadphoneBand", pts, band_r, M["plastic"], root)
    # padded cushion under the top of the band
    pts_pad = [(hx, cy + (R - 0.014) * math.sin(th), hz + (R - 0.014) * math.cos(th))
               for th in [0.6 + (math.pi - 1.2) * i / 12 for i in range(13)]]
    tube("HeadphonePad", pts_pad, 0.009, M["leather"], root)
    # ear cups
    cup_y = cy + R * math.sin(-0.45) - 0.045
    for s in (-1, 1):
        cz = hz + s * (R * math.cos(-0.45) + 0.005)
        tube(f"HeadphoneYoke{s}", [(hx, cup_y + 0.075, cz), (hx, cup_y + 0.045, cz)], 0.006, M["metal"], root)
        disc(f"EarCup{s}", (hx, cup_y, cz + s * 0.012), 0.05, 0.034, M["plastic"], root, axis="z")
        ring(f"EarCushion{s}", (hx, cup_y, cz - s * 0.008), 0.036, 0.016, M["leather"], root, axis="z")
        ring(f"EarRGB{s}", (hx, cup_y, cz + s * 0.03), 0.04, 0.0035, M["rgb"], root, axis="z")
        disc(f"EarLogo{s}", (hx, cup_y, cz + s * 0.03), 0.022, 0.004, M["metal"], root, axis="z")
    # mic boom curling forward from the left cup
    lz = hz - (R * math.cos(-0.45) + 0.005) - 0.03
    tube("MicBoom", [(hx, cup_y - 0.02, lz), (hx + 0.02, cup_y - 0.07, lz - 0.01),
                     (hx + 0.05, cup_y - 0.1, lz + 0.02), (hx + 0.07, cup_y - 0.11, lz + 0.05)],
         0.004, M["plastic"], root)


def build_gaming_desk(parent=None, name="GamingDesk", width=1.6, depth=0.75, accent="#c4202c", mount="side"):
    W, D = width, depth
    M = {
        "top": mat("Top", "#111113", 0.55),
        "mat": mat("DeskMat", "#0a0a0b", 0.95),
        "mat_edge": mat("DeskMatEdge", "#1c1c1e", 0.7),
        "frame": mat("Frame", "#0c0c0d", 0.4, metal=0.4),
        "plastic": mat("Plastic", "#151517", 0.5),
        "leather": mat("Cushion", "#0d0d0e", 0.6),
        "metal": mat("Metal", "#6b6b72", 0.3, metal=0.9),
        "rgb": mat("RGB", accent, 0.4, emit=accent, strength=6),
        "screen": mat("PanelScreen", "#000000", 0.3, emit=accent, strength=3),
        "button": mat("PanelButton", "#d8d8d8", 0.4),
        "can": mat("Can", "#1f7a46", 0.3, metal=0.6),
        "can_top": mat("CanTop", "#b8b8bd", 0.25, metal=1.0),
    }

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---------- top + desk mat
    t = 0.025
    rounded_box("DeskTop", (0, TOP_Y - t / 2, 0), (W, t, D), 0.008, M["top"], root)
    mw, md = W * 0.62, D * 0.52
    mz = D / 2 - md / 2 - 0.03
    rounded_box("DeskMatEdge", (-0.05, TOP_Y + 0.002, mz), (mw + 0.012, 0.004, md + 0.012), 0.003, M["mat_edge"], root)
    rounded_box("DeskMat", (-0.05, TOP_Y + 0.0035, mz), (mw, 0.004, md), 0.003, M["mat"], root)

    # ---------- sit-stand frame: two telescoping columns on T-feet
    lx = W / 2 - 0.22
    for s in (-1, 1):
        x = s * lx
        rounded_box(f"Foot{s}", (x, 0.028, 0), (0.07, 0.045, 0.66), 0.012, M["frame"], root)
        for e in (-1, 1):
            disc(f"FootPad{s}_{e}", (x, 0.004, e * 0.29), 0.022, 0.008, M["plastic"], root)
        rounded_box(f"ColumnLower{s}", (x, 0.3, 0), (0.078, 0.5, 0.058), 0.008, M["frame"], root)
        rounded_box(f"ColumnUpper{s}", (x, 0.62, 0), (0.066, 0.22, 0.048), 0.006, M["frame"], root)
        rounded_box(f"SideRail{s}", (x, TOP_Y - t - 0.016, 0), (0.06, 0.03, D - 0.08), 0.006, M["frame"], root)
    rounded_box("CrossBeam", (0, TOP_Y - t - 0.02, -0.05), (2 * lx, 0.035, 0.05), 0.006, M["frame"], root)

    # ---------- height control panel under the front edge (right side)
    px, pz = W / 2 - 0.42, D / 2 - 0.04
    rounded_box("ControlPanel", (px, TOP_Y - t - 0.012, pz), (0.13, 0.022, 0.05), 0.006, M["plastic"], root)
    rounded_box("ControlScreen", (px - 0.035, TOP_Y - t - 0.012, pz + 0.026), (0.03, 0.012, 0.002), 0.001,
                M["screen"], root)
    for i in range(4):
        disc(f"ControlButton{i}", (px + 0.0 + i * 0.016, TOP_Y - t - 0.012, pz + 0.026), 0.004, 0.003,
             M["button"], root, axis="z")

    # ---------- accessories
    # Each accessory is built around a mount point on the desk edge, with its arm
    # sticking out along local +x (headphones) / -x (cup). The mount is then placed:
    #   mount="side"  -> on the left/right ends (the approved look, for a lone desk)
    #   mount="front" -> hung under the front edge, so desks can sit edge to edge
    if mount == "side":
        hp = _mount("HeadphoneMount", (W / 2, 0, 0.08), 0.0, root)
        cup = _mount("CupMount", (-W / 2, 0, 0.08), 0.0, root)
    else:
        hp = _mount("HeadphoneMount", (W / 2 - 0.22, 0, D / 2), -math.pi / 2, root)
        cup = _mount("CupMount", (-W / 2 + 0.16, 0, D / 2), math.pi / 2, root)

    # headphone hook + hanging headphones
    hook_y = TOP_Y - t - 0.03
    rounded_box("HookClamp", (-0.02, TOP_Y - t - 0.015, 0), (0.05, 0.03, 0.05), 0.006, M["frame"], hp)
    tube("HookArm", [(-0.01, hook_y, 0), (0.1, hook_y, 0), (0.115, hook_y + 0.025, 0)], 0.008, M["frame"], hp)
    build_headphones(hp, 0.065, hook_y, 0, M)

    # cup holder + drink can
    cx = -0.085
    cy = TOP_Y - t - 0.03
    rounded_box("CupClamp", (0.02, TOP_Y - t - 0.015, 0), (0.05, 0.03, 0.05), 0.006, M["frame"], cup)
    tube("CupArm", [(0.01, cy, 0), (cx + 0.04, cy, 0)], 0.008, M["frame"], cup)
    ring("CupRing", (cx, cy, 0), 0.042, 0.007, M["frame"], cup)
    tube("CupStrut", [(cx + 0.04, cy, 0), (cx + 0.035, TOP_Y - 0.13, 0), (cx, TOP_Y - 0.135, 0)],
         0.006, M["frame"], cup)
    disc("CupBase", (cx, TOP_Y - 0.137, 0), 0.04, 0.008, M["frame"], cup)
    disc("Can", (cx, TOP_Y - 0.07, 0), 0.033, 0.125, M["can"], cup)
    disc("CanTop", (cx, TOP_Y - 0.005, 0), 0.029, 0.006, M["can_top"], cup)

    return root


def _mount(name, pos, yaw, parent):
    e = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(e)
    e.location = P(*pos)
    e.rotation_euler = (0, 0, yaw)
    e.parent = parent
    return e
