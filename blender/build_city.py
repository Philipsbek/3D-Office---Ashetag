"""
Builds public/models/city.glb: the approved city models, each flattened into
one mesh (one primitive per material) so the site can instance them cheaply.

  Car            : C3 supercar with white paint (tinted per instance on the site)
  LampCyan / LampPink : C9 street lamps (city_roads.py)
  Street20 / Crossroads / TrafficLight : C10-C11 city grid kit (city_roads.py)
  MinimalTowerBase : B1 dark-glass floors under the office (minimal_tower.py)
  GlassBlock / RamenCorner / NeonAlley : G2-G4 city buildings (G1 tower retired)

    blender -b --factory-startup --python blender/build_city.py
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "objects"))

import bpy  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)

import city_cars  # noqa: E402
import minimal_tower  # noqa: E402
import glass_city  # noqa: E402
import ramen_corner  # noqa: E402
import neon_alley  # noqa: E402
import city_roads  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT_GLB = os.path.join(ROOT, "public", "models", "city.glb")
RAW_GLB = os.path.join(HERE, "out", "city.raw.glb")

assets = {
    "Car": city_cars.build_street_car(None, "CR", "#ffffff"),
    "LampCyan": city_roads.build_street_lamp(None, "LC", "#22e4ff"),
    "LampPink": city_roads.build_street_lamp(None, "LP", "#ff4fd8"),
    "Street20": city_roads.build_street_segment(None, "ST", 20.0),
    "Crossroads": city_roads.build_intersection(None, "XR"),
    "TrafficLight": city_roads.build_traffic_light(None, "TL", state="all"),
    "MinimalTowerBase": minimal_tower.build_minimal_tower(None, "MT", include_office=False),
    "GlassBlock": glass_city.build_g2_block(None, "G2"),
    "RamenCorner": ramen_corner.build_ramen_corner(None, "RC"),
    "NeonAlley": neon_alley.build_neon_alley(None, "NA"),
}

for ob in [o for o in bpy.data.objects if o.type == "LIGHT"]:
    bpy.data.objects.remove(ob, do_unlink=True)

for name, root in assets.items():
    parts = [o for o in root.children_recursive if o.type in ("MESH", "CURVE", "FONT")]
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.convert(target="MESH")  # applies bevels etc.
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    joined = bpy.context.active_object
    joined.name = name
    joined.data.name = name
    if name == "Car":
        # hundreds of these drive the grid, seen from 40+ m up: a lighter mesh is plenty
        dec = joined.modifiers.new("Lighter", "DECIMATE")
        dec.ratio = 0.35
        bpy.ops.object.modifier_apply(modifier="Lighter")
    tris = sum(len(p.vertices) - 2 for p in joined.data.polygons)
    print("ASSET", name, "tris", tris, "materials", len(joined.data.materials))

for ob in [o for o in bpy.data.objects if o.type == "EMPTY"]:
    bpy.data.objects.remove(ob, do_unlink=True)

os.makedirs(os.path.dirname(RAW_GLB), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=RAW_GLB,
    export_format="GLB",
    export_apply=True,
    export_draco_mesh_compression_enable=False,
    export_lights=False,
    export_cameras=False,
)
TMP = os.path.join(HERE, "out", "city.dedup.glb")
for cmd in (
    f'npx gltf-transform dedup "{RAW_GLB}" "{TMP}"',
    f'npx gltf-transform draco "{TMP}" "{OUT_GLB}"',
):
    subprocess.run(cmd, shell=True, check=True, cwd=ROOT)
os.remove(TMP)
print("OPTIMIZED", OUT_GLB, os.path.getsize(OUT_GLB), "bytes")
