"""
Render the built office (blender/office.blend) with the loft's zone lighting,
to check the layout before it goes to the website.

  blender -b blender/office.blend --python blender/render_loft.py -- <out.png> [lobby|people|lab|services|lower]
"""

import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from character import P, _hex  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
out = os.path.abspath(args[0])
view = args[1] if len(args) > 1 else "lobby"
scene = bpy.context.scene
UP = 3.3


def point(name, pos, color, watts, radius=0.15):
    d = bpy.data.lights.new(name, "POINT")
    d.color = _hex(color)
    d.energy = watts
    d.shadow_soft_size = radius
    o = bpy.data.objects.new(name, d)
    o.location = P(*pos)
    scene.collection.objects.link(o)


def area(name, pos, rot_deg, color, watts, size):
    d = bpy.data.lights.new(name, "AREA")
    d.color = _hex(color)
    d.energy = watts
    d.size = size
    o = bpy.data.objects.new(name, d)
    o.location = P(*pos)
    o.rotation_euler = [math.radians(a) for a in rot_deg]
    scene.collection.objects.link(o)


area("L_Window", (4.1, 5.0, -5.6), (-90, 0, 0), "#ffcf20", 900, 4.0)
point("L_WindowBounce", (4.0, UP + 1.2, -3.6), "#ffb020", 250)
point("L_Workstation", (-4.6, UP + 2.0, -4.2), "#38e0c8", 420)
point("L_Arcades", (-1.1, UP + 1.8, -4.4), "#3a6bff", 260)
point("L_ArcadesRed", (-0.5, UP + 1.6, -4.3), "#ff2a3a", 160)
point("L_KitchenRed", (-4.2, 2.2, -4.4), "#ff2438", 520)
point("L_KitchenPink", (-6.3, 1.7, -3.8), "#ff5fb0", 160)
point("L_Alcove", (0.9, 2.2, -4.6), "#2aa8ff", 380)
area("L_Doorway", (5.3, 1.3, -6.1), (-90, 0, 0), "#ff7a14", 500, 1.4)
point("L_DoorBounce", (5.3, 1.4, -4.4), "#ff8a2a", 220)
point("L_Front", (0.6, 2.6, 1.6), "#9fb6d8", 200, 1.0)
point("L_Table", (-2.2, 2.0, -0.6), "#9fdcff", 90, 0.6)

world = bpy.data.worlds.new("World")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0

VIEWS = {
    "lobby": ((11.5, 8.0, 12.5), (-0.2, 2.4, -2.2), 27),
    "people": ((-1.6, 5.3, 1.2), (-4.6, 3.9, -5.0), 26),
    "lab": ((-0.6, 4.9, -1.4), (-1.15, 4.4, -5.6), 30),
    "services": ((3.2, 5.0, 0.2), (4.1, 4.6, -5.6), 28),
    "lower": ((2.5, 2.4, 7.0), (-1.0, 1.0, -3.0), 24),
}
cpos, tgt, lens = VIEWS[view]
cd = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cd)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = P(*cpos)
cam.rotation_euler = (Vector(P(*tgt)) - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
cd.lens = lens

for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = 0.3
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("RENDERED", out)
