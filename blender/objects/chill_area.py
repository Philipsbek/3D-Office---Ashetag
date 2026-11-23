"""
Chill (gaming) corner for the loft's lower floor, ORIGINAL designs only (no real brand):

  build_big_tv(parent, name)   75"-class TV on a low media console, violet bias light behind it,
                               showing an original console home screen (textures/console_home.png)
  build_console(parent, name)  next-gen games console standing upright: white side shells with a
                               slanted top, a gloss-black core down the middle, cyan light seams
  build_controller(parent, name, accent)  wireless pad lying flat: white two-tone body, black centre
                               plate, two sticks, d-pad, four plain coloured face buttons (no symbols),
                               touch panel with a light bar
  build_rug(parent, name, w, d) big woven floor rug for the whole area (textures/chill_rug.png)
  build_lounger(parent, name, fabric, trim, seed)  structured lounger bean bag: plump rounded-square
                               seat + tilted backrest with stitched channels, soft fabric, no neon
                               (a different style from the slouchy neon-seam bean_bag.py ones)
  build_chill_area(parent, name)  everything together on the rug: TV at the -Z end, console beside it,
                               two pads on the rug, three loungers in a curve facing the TV

Coordinates are three.js style (Y up). The TV faces +Z; origin at the centre of the
console's footprint on the floor.
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
from loft_room import block, mat, slab  # noqa: E402
from arcade_cabinet import prism  # noqa: E402
from gaming_desk import disc  # noqa: E402

TV_TEX = os.path.join(HERE, "textures", "console_home.png")
RUG_TEX = os.path.join(HERE, "textures", "chill_rug.png")


def _root(name, parent):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    return root


def _image_mat(name, path, strength=1.4):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path, check_existing=True)
    tex.image.pack()
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Roughness"].default_value = 0.25
    return m


def _image_quad(name, x0, x1, y0, y1, z, m, parent):
    """Flat quad facing +Z with 0..1 UVs (named UVMap so it survives joins)."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new(P(x, y, z)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    f = bm.faces.new(vs)
    for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = (u, v)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    o.parent = parent
    return o


def build_big_tv(parent=None, name="ChillTV"):
    WOOD = mat("ChillConsoleWood", "#1c1a20", 0.55)
    TOP = mat("ChillConsoleTop", "#2a2730", 0.35, metal=0.2)
    SLAT = mat("ChillConsoleSlat", "#121116", 0.6)
    LEG = mat("ChillConsoleLeg", "#0c0c0f", 0.3, metal=0.8)
    BODY = mat("ChillTVBody", "#0b0b0e", 0.3, metal=0.6)
    BEZEL = mat("ChillTVBezel", "#050506", 0.2)
    GLOW = mat("ChillTVBacklight", "#7a4dff", emit="#7a4dff", strength=5.0)
    STRIP = mat("ChillConsoleStrip", "#22e4ff", emit="#22e4ff", strength=5.0)
    SCREEN = _image_mat("Loft_ChillTVScreen", TV_TEX, 1.5)

    root = _root(name, parent)

    # ---------- low media console: slatted front, thin legs, cyan strip under the top lip
    cw, ch, cd = 2.0, 0.42, 0.42
    leg_h = 0.1
    for sx in (-1, 1):
        for sz in (-1, 1):
            block(f"{name}Leg{sx}{sz}", (sx * (cw / 2 - 0.08), leg_h / 2, sz * (cd / 2 - 0.06)), (0.035, leg_h, 0.035), LEG, root)
    block(f"{name}Console", (0, leg_h + ch / 2, 0), (cw, ch, cd), WOOD, root, r=0.012)
    block(f"{name}ConsoleTop", (0, leg_h + ch + 0.012, 0), (cw + 0.04, 0.024, cd + 0.02), TOP, root, r=0.006)
    for k in range(-9, 10):  # vertical slats across the doors
        block(f"{name}Slat{k}", (k * 0.1, leg_h + ch / 2, cd / 2 + 0.006), (0.04, ch - 0.06, 0.012), SLAT, root, r=0.003)
    slab(f"{name}Strip", -cw / 2 + 0.05, cw / 2 - 0.05, leg_h + ch - 0.012, leg_h + ch - 0.004, cd / 2 + 0.008, cd / 2 + 0.014, STRIP, root)

    # ---------- the TV on a centre pedestal
    top_y = leg_h + ch + 0.024
    tw, th = 1.66, 0.94  # 75"-class 16:9 panel
    ty = top_y + 0.09 + th / 2
    tz = -0.05
    block(f"{name}StandFoot", (0, top_y + 0.008, tz), (0.42, 0.016, 0.24), BODY, root, r=0.006)
    block(f"{name}StandNeck", (0, top_y + 0.06, tz - 0.04), (0.12, 0.1, 0.03), BODY, root, r=0.005)
    block(f"{name}Body", (0, ty, tz - 0.035), (tw - 0.2, th - 0.2, 0.05), BODY, root, r=0.01)  # electronics hump
    block(f"{name}Panel", (0, ty, tz), (tw, th, 0.02), BEZEL, root, r=0.004)
    _image_quad(f"{name}Screen", -tw / 2 + 0.012, tw / 2 - 0.012, ty - th / 2 + 0.012, ty + th / 2 - 0.012, tz + 0.0105, SCREEN, root)
    # violet bias light: an LED strip around the back of the panel, glowing onto the wall
    bw, bh, bz, t = tw - 0.26, th - 0.26, tz - 0.062, 0.018
    for k, (x0, x1, y0, y1) in enumerate((
        (-bw / 2, bw / 2, ty + bh / 2 - t, ty + bh / 2),
        (-bw / 2, bw / 2, ty - bh / 2, ty - bh / 2 + t),
        (-bw / 2, -bw / 2 + t, ty - bh / 2, ty + bh / 2),
        (bw / 2 - t, bw / 2, ty - bh / 2, ty + bh / 2),
    )):
        slab(f"{name}Backlight{k}", x0, x1, y0, y1, bz - 0.006, bz, GLOW, root)
    return root


def build_console(parent=None, name="ChillConsole"):
    SHELL = mat("ConsoleShell", "#eef0f3", 0.32)
    CORE = mat("ConsoleCore", "#08090c", 0.12, metal=0.3)
    VENT = mat("ConsoleVent", "#16181d", 0.6)
    LIGHT = mat("ConsoleLight", "#38d8ff", emit="#38d8ff", strength=7.0)
    PORT = mat("ConsolePort", "#2a2d33", 0.4, metal=0.6)

    root = _root(name, parent)
    lift = 0.02  # sits on a thin round stand

    # gloss-black core: a slim slab down the middle, a little taller than the shells
    core = [(-0.12, lift), (0.115, lift), (0.125, lift + 0.36), (0.02, lift + 0.41), (-0.12, lift + 0.41)]
    cr = prism(f"{name}Core", core, -0.028, 0.028, CORE, root)
    bev = cr.modifiers.new("Soft", "BEVEL")
    bev.width, bev.segments, bev.limit_method = 0.004, 2, "ANGLE"

    # white side shells: slanted top that drops toward the front, a scooped notch at the front foot
    shell = [
        (-0.13, lift + 0.005), (0.05, lift + 0.005), (0.075, lift + 0.035), (0.13, lift + 0.04),
        (0.135, lift + 0.33), (0.0, lift + 0.395), (-0.13, lift + 0.4),
    ]
    for s in (-1, 1):
        x0, x1 = (0.03, 0.058) if s > 0 else (-0.058, -0.03)
        sh = prism(f"{name}Shell{s}", shell, x0, x1, SHELL, root)
        bev = sh.modifiers.new("Soft", "BEVEL")  # moulded-plastic edges
        bev.width, bev.segments, bev.limit_method = 0.008, 3, "ANGLE"
        # cyan light seam between the shell and the core, running up the front edge
        slab(f"{name}Seam{s}", s * 0.0285 - 0.0015, s * 0.0285 + 0.0015, lift + 0.05, lift + 0.33, 0.118, 0.132, LIGHT, root)

    # vents along the top of the core, ports + power on the front of the core
    for k in range(6):
        block(f"{name}Vent{k}", (0, lift + 0.405, -0.1 + k * 0.022), (0.04, 0.006, 0.012), VENT, root)
    block(f"{name}PortA", (-0.01, lift + 0.08, 0.121), (0.012, 0.005, 0.004), PORT, root)
    block(f"{name}PortC", (0.01, lift + 0.08, 0.121), (0.009, 0.004, 0.004), PORT, root)
    block(f"{name}Power", (0, lift + 0.12, 0.123), (0.016, 0.004, 0.003), LIGHT, root)

    # round stand
    disc(f"{name}Stand", (0, lift / 2, 0), 0.085, lift, CORE, root, axis="y", verts=40)
    return root


def build_console_preview(parent=None, name="ChillConsolePreview"):
    """The console on its own, scaled up 3x so the details read in a preview render."""
    root = _root(name, parent)
    c = build_console(root, name=name + "C")
    c.scale = (3, 3, 3)
    return root


def _plate(name, outline, y0, y1, m, parent, bevel=0.0):
    """Extrude an (x, z) outline from y0 up to y1 (a flat part lying on the floor)."""
    n = len(outline)
    verts = [P(x, y, z) for y in (y0, y1) for (x, z) in outline]
    faces = [list(range(n)), list(range(n, 2 * n))[::-1]]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, n + i, n + j, j])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    me.materials.append(m)
    o.parent = parent
    if bevel:
        b = o.modifiers.new("Soft", "BEVEL")
        b.width, b.segments, b.limit_method = bevel, 3, "ANGLE"
    return o


def _mirror(half):
    """Right-half outline (x >= 0, front to back) -> full closed outline."""
    return half + [(-x, z) for (x, z) in reversed(half) if x > 0]


def build_controller(parent=None, name="ChillPad", accent="#22e4ff"):
    WHITE = mat("PadWhite", "#eceef2", 0.35)
    BLACK = mat("PadBlack", "#0d0e12", 0.3)
    STICK = mat("PadStick", "#1b1c21", 0.6)
    TOUCH = mat("PadTouch", "#e3e5ea", 0.25)
    LIGHT = mat(f"PadLight{accent[1:]}", accent, emit=accent, strength=6.0)
    BTN = [mat(f"PadBtn{c[1:]}", c, 0.3, emit=c, strength=1.2) for c in ("#22e4ff", "#ff4fd8", "#b6ff3b", "#ffb020")]

    root = _root(name, parent)
    t = 0.03  # body thickness (lies flat on the mat, front/triggers toward -Z)
    body = _mirror([
        (0.0, -0.046), (0.045, -0.05), (0.068, -0.043), (0.08, -0.02), (0.084, 0.015),
        (0.079, 0.048), (0.066, 0.064), (0.05, 0.06), (0.038, 0.035), (0.0, 0.028),
    ])
    _plate(f"{name}Body", body, 0.0, t, WHITE, root, bevel=0.007)
    plate = _mirror([(0.0, -0.03), (0.04, -0.03), (0.046, -0.005), (0.04, 0.026), (0.0, 0.022)])
    _plate(f"{name}Plate", plate, t - 0.002, t + 0.004, BLACK, root, bevel=0.002)

    # touch panel + light bar around it
    block(f"{name}Touch", (0, t + 0.006, -0.03), (0.06, 0.004, 0.028), TOUCH, root, r=0.003)
    for sx in (-1, 1):
        block(f"{name}Light{sx}", (sx * 0.032, t + 0.005, -0.03), (0.003, 0.004, 0.026), LIGHT, root)

    # thumbsticks
    for sx in (-1, 1):
        disc(f"{name}StickBase{sx}", (sx * 0.024, t + 0.006, 0.006), 0.012, 0.006, BLACK, root, axis="y", verts=20)
        disc(f"{name}Stick{sx}", (sx * 0.024, t + 0.013, 0.006), 0.009, 0.006, STICK, root, axis="y", verts=20)

    # d-pad (left) and four plain coloured face buttons (right)
    block(f"{name}DpadH", (-0.056, t + 0.003, -0.012), (0.026, 0.005, 0.008), BLACK, root, r=0.002)
    block(f"{name}DpadV", (-0.056, t + 0.003, -0.012), (0.008, 0.005, 0.026), BLACK, root, r=0.002)
    for k, (dx, dz) in enumerate(((0, -0.011), (0.011, 0), (0, 0.011), (-0.011, 0))):
        disc(f"{name}Btn{k}", (0.056 + dx, t + 0.003, -0.012 + dz), 0.0048, 0.005, BTN[k], root, axis="y", verts=16)

    # shoulder triggers at the front
    for sx in (-1, 1):
        block(f"{name}Trigger{sx}", (sx * 0.055, t * 0.6, -0.05), (0.03, 0.016, 0.012), BLACK, root, r=0.004)
    return root


def build_controllers_preview(parent=None, name="ChillPadsPreview"):
    """Two pads as they'll lie on the mat (cyan + pink light bars), scaled up 4x for the preview."""
    root = _root(name, parent)
    a = build_controller(root, name + "A", "#22e4ff")
    a.location = P(-0.13, 0, 0)
    a.rotation_euler = (0, 0, 0.25)
    b = build_controller(root, name + "B", "#ff4fd8")
    b.location = P(0.12, 0, 0.04)
    b.rotation_euler = (0, 0, -0.5)
    root.scale = (4, 4, 4)
    return root


def build_rug(parent=None, name="ChillRug", w=3.0, d=3.6):
    """Rug lying on the floor, centred on the origin; the pattern's top edge is at -Z (toward the TV)."""
    EDGE = mat("ChillRugEdge", "#15162a", 0.95)
    TOPM = bpy.data.materials.get("Loft_ChillRug")
    if TOPM is None:
        TOPM = _image_mat("Loft_ChillRug", RUG_TEX, strength=0.0)
        b = TOPM.node_tree.nodes["Principled BSDF"]
        b.inputs["Roughness"].default_value = 0.95
        b.inputs["Emission Strength"].default_value = 0.0

    root = _root(name, parent)
    th = 0.018
    block(f"{name}Base", (0, th / 2 - 0.001, 0), (w, th, d), EDGE, root, r=0.008)
    # textured top: a flat quad facing up with 0..1 UVs (v=1 at the -Z end)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    y = th + 0.0005
    vs = [bm.verts.new(P(x, y, z)) for x, z in ((-w / 2, d / 2), (w / 2, d / 2), (w / 2, -d / 2), (-w / 2, -d / 2))]
    f = bm.faces.new(vs)
    for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = (u, v)
    me = bpy.data.meshes.new(f"{name}Top")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(f"{name}Top", me)
    bpy.context.collection.objects.link(o)
    me.materials.append(TOPM)
    o.parent = root
    return root


def _soft_box(name, size, m, parent, boxy=0.32, channels=0, sag=0.0, seed=0, segs=40):
    """A plump cushion: a sphere pushed toward a rounded box (superellipsoid), with optional
    stitched channels running top-to-bottom on its front (+Z) face and a sat-in dip on top."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=segs, ring_count=segs // 2)
    o = bpy.context.active_object
    o.name = name
    o.data.name = name
    w, h, d = size
    for v in o.data.vertices:
        x, y, z = v.co.x, v.co.z, -v.co.y  # Blender -> three.js
        f = lambda c: math.copysign(abs(c) ** boxy, c)  # noqa: E731
        X, Y, Z = f(x) * w / 2, f(y) * h / 2, f(z) * d / 2
        if channels and z > 0:  # quilted channels on the front face
            Z -= 0.012 * (1 - math.cos(x * math.pi * channels)) * z
        if sag and y > 0:  # a soft dip where you sit
            Y -= sag * (1 - min(1, (x * x + z * z) * 1.6)) * y
        v.co = P(X, Y, Z)
    o.data.update()
    for poly in o.data.polygons:
        poly.use_smooth = True
    for c in list(o.users_collection):
        c.objects.unlink(o)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(m)
    o.parent = parent
    return o


def build_lounger(parent=None, name="ChillLounger", fabric="#d9cbb5", trim="#2b2238", seed=1):
    FAB = mat(f"LoungerFabric{fabric[1:]}", fabric, 0.97)
    TRIM = mat(f"LoungerTrim{trim[1:]}", trim, 0.8)
    root = _root(name, parent)
    # seat cushion
    seat = _soft_box(f"{name}Seat", (0.86, 0.3, 0.8), FAB, root, boxy=0.34, sag=0.05)
    seat.location = P(0, 0.15, 0.06)
    # backrest, leaning back ~16 degrees, quilted channels facing the seat
    back = _soft_box(f"{name}Back", (0.84, 0.62, 0.26), FAB, root, boxy=0.36, channels=5)
    back.location = P(0, 0.48, -0.3)
    back.rotation_euler = (math.radians(16), 0, 0)
    # a low contrasting base band (piping round the bottom) + a little carry tab on top of the back
    _soft_box(f"{name}Base", (0.9, 0.05, 0.86), TRIM, root, boxy=0.25).location = P(0, 0.025, -0.02)
    tab = block(f"{name}Tab", (0, 0.8, -0.4), (0.12, 0.03, 0.03), TRIM, root, r=0.012)
    tab.rotation_euler = (math.radians(16), 0, 0)
    return root


def build_lounger_set(parent=None, name="ChillLoungers"):
    """Three loungers in different soft colours (cream, dusty lilac, burnt orange), slightly turned."""
    root = _root(name, parent)
    for k, (fab, trim, x, z, yaw) in enumerate((
        ("#d9cbb5", "#2b2238", -1.0, 0.1, 18),
        ("#a58fc7", "#1c1a2e", 0.0, -0.1, 0),
        ("#d4733a", "#26191a", 1.0, 0.1, -18),
    )):
        b = build_lounger(root, f"{name}{k}", fab, trim, seed=k)
        b.location = P(x, 0, z)
        b.rotation_euler = (0, 0, math.radians(yaw))
    return root


def build_chill_area(parent=None, name="ChillArea", rug_w=3.4, rug_d=3.2):
    """The whole corner, centred on the rug. The TV sits at the -Z end facing +Z."""
    root = _root(name, parent)
    build_rug(root, f"{name}Rug", rug_w, rug_d)
    z_tv = -rug_d / 2 + 0.25
    tv = build_big_tv(root, f"{name}TV")
    tv.location = P(0, 0, z_tv)
    con = build_console(root, f"{name}Console")
    con.location = P(1.28, 0.018, z_tv)  # on the rug, just right of the TV stand
    con.rotation_euler = (0, 0, math.radians(-8))
    for k, (x, z, yaw, accent) in enumerate(((-0.3, 0.05, 22, "#22e4ff"), (0.35, 0.28, -38, "#ff4fd8"))):
        pad = build_controller(root, f"{name}Pad{k}", accent)
        pad.location = P(x, 0.018, z)
        pad.rotation_euler = (0, 0, math.radians(yaw + 180))  # grips toward the seats
    for k, (fab, trim, x, z, yaw) in enumerate((
        ("#d9cbb5", "#2b2238", -1.02, 0.78, 165),
        ("#a58fc7", "#1c1a2e", 0.0, 0.92, 180),
        ("#d4733a", "#26191a", 1.02, 0.78, 195),
    )):
        b = build_lounger(root, f"{name}Lounger{k}", fab, trim, seed=k)
        b.location = P(x, 0.018, z)
        b.rotation_euler = (0, 0, math.radians(yaw))  # seats face the TV (-Z)
    return root
