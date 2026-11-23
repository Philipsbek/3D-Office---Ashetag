"""
Renders a character turnaround (front / side / back / seated) and a face
close-up, to compare against the reference sheet.

  blender -b --python blender/preview_character.py -- <output_dir>
"""

import bpy
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character  # noqa: E402

out_dir = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.path.dirname(__file__)
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# turnaround: front, side (facing right), back, + seated 3/4
for i, (pose, yaw) in enumerate([("stand", 0), ("stand", 90), ("stand", 180), ("sit", 35)]):
    e = bpy.data.objects.new(f"Slot{i}", None)
    bpy.context.collection.objects.link(e)
    e.location = (-1.5 + i * 1.0, 0, 0)
    e.rotation_euler = (0, 0, math.radians(yaw))
    character.build_character(e, pose=pose, name=f"Char{i}")

# light grey backdrop
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
floor = bpy.context.active_object
bm = bpy.data.materials.new("Backdrop")
bm.diffuse_color = (0.8, 0.8, 0.8, 1)
floor.data.materials.append(bm)

scene.render.engine = "BLENDER_WORKBENCH"
shading = scene.display.shading
shading.light = "STUDIO"
shading.color_type = "MATERIAL"
shading.show_shadows = True
shading.show_cavity = True
shading.cavity_type = "BOTH"
scene.display.shadow_focus = 0.6
scene.world = bpy.data.worlds.new("W") if not scene.world else scene.world
scene.render.film_transparent = False

cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam


def shot(path, loc, rot_deg, lens, w, h):
    cam.location = loc
    cam.rotation_euler = [math.radians(a) for a in rot_deg]
    cam_data.lens = lens
    scene.render.resolution_x = w
    scene.render.resolution_y = h
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


# full turnaround (camera looks along +Y toward the characters, which face -Y)
shot(os.path.join(out_dir, "turnaround.png"), (0, -7.5, 0.95), (90, 0, 0), 50, 1400, 700)
# face close-up of the front-facing character
shot(os.path.join(out_dir, "face.png"), (-1.5, -0.75, 1.63), (90, 0, 0), 50, 700, 700)

# ---- desk poses: typing + sleeping, each with a desk in front
for o in list(bpy.data.objects):
    if o.name not in ("Cam",) and o != floor:
        bpy.data.objects.remove(o, do_unlink=True)
for i, pose in enumerate(["type", "sleep"]):
    x = -0.7 + i * 1.4
    e = bpy.data.objects.new(f"PoseSlot{i}", None)
    bpy.context.collection.objects.link(e)
    e.location = (x, 0, 0)
    character.build_character(e, pose=pose, name=f"Pose{i}")
    # desk (three.js z +0.25..+1.05 in front of the pelvis = blender -y)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.65, 0.76))
    d = bpy.context.active_object
    d.scale = (1.4, 0.8, 0.03)
    d.data.materials.append(bm)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.55, 0.785))
    k = bpy.context.active_object
    k.scale = (0.42, 0.14, 0.02)
    # chair seat
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.0, 0.48))
    c = bpy.context.active_object
    c.scale = (0.5, 0.48, 0.07)

shot(os.path.join(out_dir, "poses.png"), (2.3, -2.3, 1.9), (62, 0, 45), 40, 1200, 700)
