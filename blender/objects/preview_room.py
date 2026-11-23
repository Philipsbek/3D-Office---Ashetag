"""
Preview render of the loft room structure with its colour-zone lighting.
Grey blocks are placeholders that only show where each zone's furniture goes;
they are not part of the room.

  blender -b --python blender/objects/preview_room.py -- <out.png> [blockout|empty] [cam]

cam: "lobby" (default, 3/4 from the front right) or "front".
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import bpy  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
out_path = os.path.abspath(args[0])
blockout = (args[1] if len(args) > 1 else "blockout") == "blockout"
cam_name = args[2] if len(args) > 2 else "lobby"

bpy.ops.wm.read_factory_settings(use_empty=True)
from character import P, _hex  # noqa: E402
import loft_room  # noqa: E402

loft_room.build_loft_room()
scene = bpy.context.scene

# ---------------------------------------------------------------- placeholders
if blockout:
    G = loft_room.mat("Placeholder", "#55585c", 0.8)
    Y = loft_room.MEZ_Y
    blocks = [
        # upper level
        ("PH_DeskA", (-5.4, Y + 0.375, -5.2), (1.6, 0.75, 0.75)),
        ("PH_DeskB", (-3.7, Y + 0.375, -5.2), (1.6, 0.75, 0.75)),
        ("PH_Chair", (-5.2, Y + 0.6, -4.2), (0.6, 1.2, 0.6)),
        ("PH_FanUnit", (-6.6, Y + 1.0, -3.6), (0.7, 2.0, 1.4)),
        ("PH_Bookshelf", (-4.6, Y + 2.0, -5.85), (3.4, 0.9, 0.3)),
        ("PH_ArcadeA", (-1.6, Y + 0.95, -5.5), (0.8, 1.9, 0.8)),
        ("PH_ArcadeB", (-0.5, Y + 0.95, -5.5), (0.8, 1.9, 0.8)),
        ("PH_Bed", (3.6, Y + 0.25, -4.4), (2.2, 0.5, 2.6)),
        ("PH_Telescope", (6.0, Y + 0.8, -3.4), (0.4, 1.6, 0.4)),
        # lower level
        ("PH_Kitchen", (-6.4, 0.45, -4.4), (1.2, 0.9, 2.8)),
        ("PH_Washer", (-6.4, 0.45, -2.6), (0.8, 0.9, 0.8)),
        ("PH_BarTable", (-1.6, 0.5, -1.3), (2.8, 1.0, 0.7)),
        ("PH_StoolA", (-2.4, 0.4, -0.5), (0.4, 0.8, 0.4)),
        ("PH_StoolB", (-1.4, 0.4, -0.5), (0.4, 0.8, 0.4)),
        ("PH_NeonSign", (-3.6, 1.8, -5.9), (1.3, 1.3, 0.08)),
        ("PH_Scooter", (5.9, 0.55, -2.8), (0.6, 1.1, 1.6)),
        ("PH_CrateA", (-3.8, 0.35, 1.4), (1.3, 0.7, 0.8)),
        ("PH_CrateB", (-1.4, 0.35, 2.4), (1.3, 0.7, 0.8)),
        ("PH_CrateC", (2.4, 0.35, 1.6), (1.1, 0.7, 0.8)),
        ("PH_CrateD", (6.0, 0.35, 0.2), (1.1, 0.7, 0.8)),
    ]
    for n, c, s in blocks:
        loft_room.block(n, c, s, G, None, r=0.02)

# ---------------------------------------------------------------- zone lights
def point(name, pos, color, watts, radius=0.15):
    d = bpy.data.lights.new(name, "POINT")
    d.color = _hex(color)
    d.energy = watts
    d.shadow_soft_size = radius
    o = bpy.data.objects.new(name, d)
    o.location = P(*pos)
    bpy.context.collection.objects.link(o)


def area(name, pos, rot_deg, color, watts, size):
    d = bpy.data.lights.new(name, "AREA")
    d.color = _hex(color)
    d.energy = watts
    d.size = size
    o = bpy.data.objects.new(name, d)
    o.location = P(*pos)
    o.rotation_euler = [math.radians(a) for a in rot_deg]
    bpy.context.collection.objects.link(o)


Y = loft_room.MEZ_Y
# upper floor
area("L_Window", (4.1, 5.0, -5.6), (-90, 0, 0), "#ffcf20", 900, 4.0)       # yellow window wash
point("L_WindowBounce", (4.0, Y + 1.2, -3.6), "#ffb020", 250)
point("L_Workstation", (-4.8, Y + 2.0, -4.6), "#38e0c8", 420)                # teal desk zone
point("L_Arcades", (-1.0, Y + 1.8, -4.6), "#3a6bff", 260)                   # blue arcade glow
point("L_ArcadesRed", (-0.3, Y + 1.6, -4.4), "#ff2a3a", 160)
# lower floor
point("L_KitchenRed", (-4.2, 2.2, -4.6), "#ff2438", 520)                    # red neon zone
point("L_KitchenPink", (-6.3, 1.7, -3.8), "#ff5fb0", 160)
point("L_Alcove", (0.9, 2.2, -5.0), "#2aa8ff", 380)                         # blue alcove
area("L_Doorway", (5.3, 1.3, -6.1), (-90, 0, 0), "#ff7a14", 500, 1.4)      # orange doorway
point("L_DoorBounce", (5.3, 1.4, -4.6), "#ff8a2a", 220)
point("L_Front", (0.6, 2.4, 1.6), "#9fb6d8", 140, 1.0)                      # dim cool fill on the open front

# ---------------------------------------------------------------- world, camera, render
world = bpy.data.worlds.new("World")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0

cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam
if cam_name == "front":
    cam.location = P(0.2, 4.2, 14.5)
    target = P(0.2, 3.0, -2.0)
    cam_data.lens = 26
else:
    cam.location = P(11.5, 8.0, 12.5)
    target = P(-0.2, 2.6, -2.4)
    cam_data.lens = 27
from mathutils import Vector  # noqa: E402

d = Vector(target) - Vector(cam.location)
cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
scene.view_settings.exposure = 0.3
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("RENDERED", out_path, scene.render.engine)
