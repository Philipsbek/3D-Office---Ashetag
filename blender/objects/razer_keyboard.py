"""
Razer-style full-size RGB mechanical keyboard (BlackWidow-inspired):
matte black aluminium-look case, floating black keycaps with glowing
legends, a rainbow "Chroma" backlight plate visible between the keys,
side underglow, a media roller + media keys, and a plush wrist rest with an
RGB underglow strip. No logos.

    build_razer_keyboard(parent=None, name="RazerKeyboard") -> root empty

Coordinates are three.js style (Y up, the typist is on the +Z side, origin
on the desk under the keyboard's centre).

All glowing parts share one rainbow texture, mapped left -> right, in a
material named "Razer_ChromaRGB" so the website can animate it (e.g. scroll
the texture offset for a Chroma wave).
"""

import colorsys
import math
import os
import sys

import bpy
import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, rounded_box  # noqa: E402
from razer_monitor import mat  # noqa: E402  (shared "Razer_" material cache)

U = 0.019  # one key unit (19 mm)

# rows: list of (label, width_in_units) ; None label = gap
MAIN = [
    [("Esc", 1), (None, 1), ("F1", 1), ("F2", 1), ("F3", 1), ("F4", 1), (None, 0.5),
     ("F5", 1), ("F6", 1), ("F7", 1), ("F8", 1), (None, 0.5), ("F9", 1), ("F10", 1), ("F11", 1), ("F12", 1)],
    [("`", 1)] + [(c, 1) for c in "1234567890-="] + [("Bksp", 2)],
    [("Tab", 1.5)] + [(c, 1) for c in "QWERTYUIOP[]"] + [("\\", 1.5)],
    [("Caps", 1.75)] + [(c, 1) for c in "ASDFGHJKL;'"] + [("Enter", 2.25)],
    [("Shift", 2.25)] + [(c, 1) for c in "ZXCVBNM,./"] + [("Shift", 2.75)],
    [("Ctrl", 1.25), ("Win", 1.25), ("Alt", 1.25), ("Space", 6.25), ("Alt", 1.25), ("Fn", 1.25),
     ("Menu", 1.25), ("Ctrl", 1.25)],
]
# (label, col, row, w, h) in units, for the nav cluster + numpad (col from left edge)
EXTRA = [
    ("PrtSc", 15.25, 0, 1, 1), ("ScrLk", 16.25, 0, 1, 1), ("Pause", 17.25, 0, 1, 1),
    ("Ins", 15.25, 1, 1, 1), ("Home", 16.25, 1, 1, 1), ("PgUp", 17.25, 1, 1, 1),
    ("Del", 15.25, 2, 1, 1), ("End", 16.25, 2, 1, 1), ("PgDn", 17.25, 2, 1, 1),
    ("Up", 16.25, 4, 1, 1),
    ("Left", 15.25, 5, 1, 1), ("Down", 16.25, 5, 1, 1), ("Right", 17.25, 5, 1, 1),
    ("Num", 18.5, 1, 1, 1), ("/", 19.5, 1, 1, 1), ("*", 20.5, 1, 1, 1), ("-", 21.5, 1, 1, 1),
    ("7", 18.5, 2, 1, 1), ("8", 19.5, 2, 1, 1), ("9", 20.5, 2, 1, 1), ("+", 21.5, 2, 1, 2),
    ("4", 18.5, 3, 1, 1), ("5", 19.5, 3, 1, 1), ("6", 20.5, 3, 1, 1),
    ("1", 18.5, 4, 1, 1), ("2", 19.5, 4, 1, 1), ("3", 20.5, 4, 1, 1), ("NEnt", 21.5, 4, 1, 2),
    ("0", 18.5, 5, 2, 1), (".", 20.5, 5, 1, 1),
]
TOTAL_W = 22.5  # units


def row_z(r):
    """Row centre (units from the back). Gap of 0.5u after the function row."""
    return 0.5 + r + (0.5 if r > 0 else 0)


def rainbow_image(w=256, h=4):
    img = bpy.data.images.get("ChromaRainbow")
    if img:
        return img
    img = bpy.data.images.new("ChromaRainbow", w, h)
    px = []
    for _y in range(h):
        for x in range(w):
            r, g, b = colorsys.hsv_to_rgb(x / w, 0.9, 1.0)
            px += [r, g, b, 1.0]
    img.pixels = px
    img.pack()
    return img


def chroma_mat(strength=4.0):
    return mat("ChromaRGB", "#000000", 0.4, image=rainbow_image(), strength=strength)


def uv_by_x(ob, x0, x1):
    """Map every face's UV so u follows the world X position -> rainbow runs left to right."""
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    for poly in me.polygons:
        for li in poly.loop_indices:
            x = me.vertices[me.loops[li].vertex_index].co.x
            uv[li].uv = ((x - x0) / (x1 - x0), 0.5)


def box_mesh(name, boxes, bevel, segments, m, parent):
    """Many boxes (cx, cy, cz, sx, sy, sz in three.js space) as ONE mesh, edges bevelled."""
    bm = bmesh.new()
    for cx, cy, cz, sx, sy, sz in boxes:
        res = bmesh.ops.create_cube(bm, size=1.0)
        verts = res["verts"]
        c = P(cx, cy, cz)
        for v in verts:
            v.co.x = v.co.x * sx + c.x
            v.co.y = v.co.y * sz + c.y  # three z -> blender y
            v.co.z = v.co.z * sy + c.z  # three y -> blender z
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if bevel > 0:
        md = ob.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = segments
        md.limit_method = "ANGLE"
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.modifier_apply(modifier="Bevel")
    for p in ob.data.polygons:
        p.use_smooth = False
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


def build_razer_keyboard(parent=None, name="RazerKeyboard", wrist_rest=True):
    CASE = mat("KbCase", "#0d0d0e", 0.45, metal=0.5)
    CAP = mat("Keycap", "#0a0a0a", 0.6)
    RUBBER = mat("WristRest", "#101011", 0.75)
    DIAL = mat("Dial", "#2a2a2d", 0.3, metal=0.9)
    RGB = chroma_mat(4.0)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    # slight typing angle: back of the board a little higher
    body = bpy.data.objects.new(name + "Body", None)
    bpy.context.collection.objects.link(body)
    body.parent = root
    body.location = P(0, 0.006, 0)
    body.rotation_euler = (0.06, 0, 0)

    W = TOTAL_W * U
    D = 6.5 * U
    x0 = -W / 2
    z0 = -D / 2 - 0.006  # back edge of the key area

    # ---------- case + backlight plate
    case_w, case_d = W + 0.022, D + 0.04
    rounded_box("KbCase", (0, 0.011, z0 - 0.012 + case_d / 2), (case_w, 0.022, case_d), 0.004, CASE, body)
    plate = box_mesh("KbBacklight", [(0, 0.0225, z0 + D / 2, W + 0.004, 0.001, D + 0.004)], 0, 0, RGB, body)
    uv_by_x(plate, x0, -x0)

    # ---------- keycaps (one mesh) + glowing legends (one mesh)
    caps, legends = [], []
    cap_h = 0.009
    cy = 0.0235 + cap_h / 2 + 0.002  # floating above the plate

    def add_key(label, col, row, w, h=1):
        cx = x0 + (col + w / 2) * U
        cz = z0 + (row_z(row) + (h - 1) / 2) * U
        caps.append((cx, cy, cz, w * U - 0.0028, cap_h, h * U - 0.0028))
        if label != "Space":
            lw = 0.0042 if len(label) == 1 else 0.007
            lx = cx - w * U / 2 + 0.0045 + lw / 2
            lz = cz - h * U / 2 + 0.0055
            legends.append((lx, cy + cap_h / 2 + 0.0002, lz, lw, 0.0006, 0.0022))

    for r, row in enumerate(MAIN):
        col = 0.0
        for label, w in row:
            if label:
                add_key(label, col, r, w)
            col += w
    for label, col, r, w, h in EXTRA:
        add_key(label, col, r, w, h)

    box_mesh("Keycaps", caps, 0.0012, 2, CAP, body)
    leg = box_mesh("KeyLegends", legends, 0, 0, RGB, body)
    uv_by_x(leg, x0, -x0)

    # ---------- media roller + media keys (top right, above the numpad)
    mx = x0 + 20.0 * U
    mz = z0 + 0.15 * U
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.018, vertices=32)
    roller = bpy.context.active_object
    roller.name = "MediaRoller"
    roller.location = P(x0 + 21.6 * U, 0.026, mz)
    roller.rotation_euler = (0, math.pi / 2, 0)
    bpy.ops.object.shade_smooth()
    roller.data.materials.append(DIAL)
    roller.parent = body
    media = [(x0 + (18.6 + i * 0.75) * U, 0.0245, mz, 0.011, 0.004, 0.007) for i in range(3)]
    box_mesh("MediaKeys", media, 0.001, 1, CAP, body)

    # ---------- side underglow strips
    strips = box_mesh("KbUnderglow", [
        (x0 - 0.0115, 0.006, z0 + D / 2 + 0.008, 0.0012, 0.006, D + 0.02),
        (-x0 + 0.0115, 0.006, z0 + D / 2 + 0.008, 0.0012, 0.006, D + 0.02),
        (0, 0.002, z0 + D + 0.0285, W + 0.02, 0.003, 0.0012),
    ], 0, 0, RGB, body)
    uv_by_x(strips, x0 - 0.012, -x0 + 0.012)

    # ---------- wrist rest with RGB strip along its front edge
    if wrist_rest:
        wz = z0 + D + 0.028 + 0.045
        rounded_box("WristRest", (0, 0.012, wz), (W * 0.96, 0.02, 0.07), 0.009, RUBBER, root)
        ws = box_mesh("WristRestRGB", [(0, 0.004, wz + 0.0315, W * 0.92, 0.004, 0.002)], 0, 0, RGB, root)
        uv_by_x(ws, x0, -x0)

    return root
