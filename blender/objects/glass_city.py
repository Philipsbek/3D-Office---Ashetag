"""
City buildings in the office tower's design language (B1): every floor is
floor-to-ceiling glass with ONE slim black mullion per wall, a thin black sill
and head, glass meeting glass at the corners, and a slim dark slab with a light
edge line between floors. Ordinary floors are near-black glossy glass (only the
city reflects in them); some floors are clear glass with a lit interior. Neon is
sparing: a crown line, a corner line, a lobby canopy line.

    glass_building(parent, name, tiers, fh=4.0, accent=..., lit_floors=(), ...)
        tiers: list of (w, d, floors, (cx, cz)) stacked bottom to top; each tier
        is a box of glass floors, set back as you like.
    build_g1_setback(parent, name)   new building 1: two-tier setback tower
    build_glass_preview(module_fn)   preview helper (adds a stand-in city to reflect)

Origin on the ground at the centre of the footprint; fronts face +Z.
Coordinates are three.js style (Y up).
"""

import math
import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P  # noqa: E402
from glass_room import glass_mat  # noqa: E402
from loft_room import mat, slab  # noqa: E402
from minimal_tower import _dark_glass  # noqa: E402


def _mats(accent):
    return {
        "slab": mat("MinSlab", "#1a1b21", 0.5),
        "edge": mat("MinSlabEdge", "#d9dbe2", 0.35),
        "frame": mat("MinFrame", "#2c2e36", 0.35, metal=0.6),
        "darkGlass": _dark_glass(),
        "clearGlass": glass_mat("MinGlass", "#8fa6c8", 0.18),
        "ceiling": mat("MinCeiling", "#eceef2", 0.6),
        "downlight": mat("MinDownlight", "#ffffff", emit="#fff4e0", strength=10.0),
        "litFloor": mat("GlassLitFloor", "#3a2c3c", 0.6, emit="#6a3a5a", strength=1.2),
        "warm": mat("GlassInteriorWarm", "#ffd9a8", emit="#ffc48a", strength=1.6),
        "furn": mat("GlassFurniture", "#121217", 0.6),
        "accent": mat(f"GlassNeon{accent[1:]}", accent, emit=accent, strength=9.0),
        "beacon": mat("MinBeacon", "#ff2020", emit="#ff2020", strength=14.0),
    }


def _box_floor(name, M, root, x0, x1, z0, z1, y0, fh, lit, rng):
    """One storey: four glass walls (dark or clear), frames, one mullion per wall."""
    g0, g1 = y0 + 0.15, y0 + fh - 0.15
    glass = M["clearGlass"] if lit else M["darkGlass"]
    for k, (a0, a1, b0, b1) in enumerate(((x0, x1, z0 - 0.01, z0 + 0.01), (x0, x1, z1 - 0.01, z1 + 0.01),
                                           (x0 - 0.01, x0 + 0.01, z0, z1), (x1 - 0.01, x1 + 0.01, z0, z1))):
        slab(f"{name}Glass{k}", a0, a1, g0, g1, b0, b1, glass, root)
    for k, (a0, a1, b0, b1) in enumerate(((x0, x1, z0 - 0.04, z0 + 0.04), (x0, x1, z1 - 0.04, z1 + 0.04),
                                           (x0 - 0.04, x0 + 0.04, z0, z1), (x1 - 0.04, x1 + 0.04, z0, z1))):
        slab(f"{name}Sill{k}", a0, a1, g0, g0 + 0.06, b0, b1, M["frame"], root)
        slab(f"{name}Head{k}", a0, a1, g1 - 0.06, g1, b0, b1, M["frame"], root)
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    for k, z in enumerate((z0, z1)):
        slab(f"{name}MullX{k}", xm - 0.03, xm + 0.03, g0, g1, z - 0.04, z + 0.04, M["frame"], root)
    for k, x in enumerate((x0, x1)):
        slab(f"{name}MullZ{k}", x - 0.04, x + 0.04, g0, g1, zm - 0.03, zm + 0.03, M["frame"], root)
    if lit:
        # a lived-in lit floor behind clear glass: warm floor, ceiling downlights, dark furniture
        slab(f"{name}LitFloor", x0 + 0.1, x1 - 0.1, y0 + 0.15, y0 + 0.17, z0 + 0.1, z1 - 0.1, M["litFloor"], root)
        slab(f"{name}Ceil", x0 + 0.05, x1 - 0.05, g1 - 0.08, g1, z0 + 0.05, z1 - 0.05, M["ceiling"], root)
        nx, nz = max(2, int((x1 - x0) / 4)), max(2, int((z1 - z0) / 4))
        for i in range(nx):
            for j in range(nz):
                x = x0 + (i + 0.5) * (x1 - x0) / nx
                z = z0 + (j + 0.5) * (z1 - z0) / nz
                slab(f"{name}Down{i}{j}", x - 0.18, x + 0.18, g1 - 0.09, g1 - 0.08, z - 0.05, z + 0.05, M["downlight"], root)
        for k in range(rng.randint(3, 5)):
            w, d, h = rng.uniform(1.2, 3.0), rng.uniform(0.6, 1.6), rng.uniform(0.7, 1.9)
            x = rng.uniform(x0 + 1.5, x1 - 1.5)
            z = rng.uniform(z0 + 1.5, z1 - 1.5)
            slab(f"{name}Furn{k}", x - w / 2, x + w / 2, y0 + 0.17, y0 + 0.17 + h, z - d / 2, z + d / 2, M["furn"], root)
        # warm back wall behind the furniture so the floor reads as lit from outside
        slab(f"{name}Glow", x0 + 1.0, x1 - 1.0, y0 + 0.17, g1 - 0.3, z0 + 0.5, z0 + 0.6, M["warm"], root)


def _slab_with_edge(name, M, root, x0, x1, z0, z1, y, over=0.12):
    slab(f"{name}", x0 - over, x1 + over, y - 0.15, y + 0.15, z0 - over, z1 + over, M["slab"], root)
    e = over + 0.01
    for k, (a0, a1, b0, b1) in enumerate(((x0 - e, x1 + e, z0 - e, z0 - e + 0.02), (x0 - e, x1 + e, z1 + e - 0.02, z1 + e),
                                           (x0 - e, x0 - e + 0.02, z0 - e, z1 + e), (x1 + e - 0.02, x1 + e, z0 - e, z1 + e))):
        slab(f"{name}Edge{k}", a0, a1, y - 0.05, y + 0.05, b0, b1, M["edge"], root)


def glass_building(parent, name, tiers, fh=4.0, accent="#ffb82e", lit_floors=(), seed=1,
                   corner_neon=True, canopy=True, crown=True, mast=True):
    M = _mats(accent)
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    y = 0.0
    f_index = 0
    for t, (w, d, floors, (cx, cz)) in enumerate(tiers):
        x0, x1, z0, z1 = cx - w / 2, cx + w / 2, cz - d / 2, cz + d / 2
        for f in range(floors):
            _box_floor(f"{name}T{t}F{f}", M, root, x0, x1, z0, z1, y, fh, f_index in lit_floors, rng)
            y += fh
            _slab_with_edge(f"{name}T{t}Slab{f}", M, root, x0, x1, z0, z1, y)
            f_index += 1
        if t < len(tiers) - 1 and crown:
            # a thin neon line along the setback's terrace edge
            e = 0.14
            for k, (a0, a1, b0, b1) in enumerate(((x0 - e, x1 + e, z1 + e - 0.03, z1 + e), (x0 - e, x0 - e + 0.03, z0 - e, z1 + e),
                                                   (x1 + e - 0.03, x1 + e, z0 - e, z1 + e))):
                slab(f"{name}TerraceNeon{t}_{k}", a0, a1, y + 0.16, y + 0.22, b0, b1, M["accent"], root)
    top_w, top_d, _, (tcx, tcz) = tiers[-1]
    tx0, tx1, tz0, tz1 = tcx - top_w / 2, tcx + top_w / 2, tcz - top_d / 2, tcz + top_d / 2
    if crown:
        # roof: dark cap and the neon crown line all round
        slab(f"{name}Roof", tx0 - 0.3, tx1 + 0.3, y + 0.15, y + 0.5, tz0 - 0.3, tz1 + 0.3, M["slab"], root)
        e = 0.32
        for k, (a0, a1, b0, b1) in enumerate(((tx0 - e, tx1 + e, tz0 - e, tz0 - e + 0.03), (tx0 - e, tx1 + e, tz1 + e - 0.03, tz1 + e),
                                               (tx0 - e, tx0 - e + 0.03, tz0 - e, tz1 + e), (tx1 + e - 0.03, tx1 + e, tz0 - e, tz1 + e))):
            slab(f"{name}Crown{k}", a0, a1, y + 0.25, y + 0.32, b0, b1, M["accent"], root)
    if mast:
        mx, mz = tx0 + 1.4, tz0 + 1.4
        slab(f"{name}Mast", mx - 0.05, mx + 0.05, y + 0.5, y + 5.5, mz - 0.05, mz + 0.05, M["frame"], root)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, segments=12, ring_count=8, location=P(mx, y + 5.65, mz))
        b = bpy.context.active_object
        b.name = f"{name}Beacon"
        b.data.materials.append(M["beacon"])
        b.parent = root
    base_w, base_d, _, (bcx, bcz) = tiers[0]
    bx0, bx1, bz0, bz1 = bcx - base_w / 2, bcx + base_w / 2, bcz - base_d / 2, bcz + base_d / 2
    if corner_neon:
        # one vertical neon line up the front-left corner of the base tier
        h = fh * tiers[0][2]
        slab(f"{name}CornerNeon", bx0 - 0.16, bx0 - 0.1, 0.4, h - 0.2, bz1 + 0.1, bz1 + 0.16, M["accent"], root)
    if canopy:
        slab(f"{name}Canopy", bx0 + 2.0, bx1 - 2.0, fh - 0.2, fh + 0.05, bz1, bz1 + 2.4, M["slab"], root)
        slab(f"{name}CanopyNeon", bx0 + 2.0, bx1 - 2.0, fh - 0.24, fh - 0.2, bz1 + 2.34, bz1 + 2.4, M["accent"], root)
    slab(f"{name}Plinth", bx0 - 0.4, bx1 + 0.4, -0.05, 0.15, bz0 - 0.4, bz1 + 0.4, M["slab"], root)
    return root


# ---------------------------------------------------------------- advert banner
TEX_DIR = os.path.join(HERE, "textures")


def _ad_material(file="anime_ad.png", strength=2.4):
    key = "Glass_Ad_" + os.path.splitext(file)[0]
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(TEX_DIR, file), check_existing=True)
    tex.image.pack()
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Roughness"].default_value = 0.35
    m.use_backface_culling = False  # exported double-sided: the screen shows whichever way its face points
    return m


def ad_banner(root, name, x, y0, h, w, accent="#22e4ff", file="anime_ad.png", zc=0.0):
    """Tall LED screen fixed to an east (+X) wall at x, bottom at y0: dark backing box,
    the image screen, a neon frame and small brackets back to the glass."""
    import bmesh

    M = _mats(accent)
    off = 0.55  # held off the glass
    sx = x + off
    slab(f"{name}Back", sx - 0.3, sx, y0 - 0.3, y0 + h + 0.3, zc - w / 2 - 0.3, zc + w / 2 + 0.3, M["slab"], root)
    # the screen quad, facing +X; u runs from +Z to -Z so the picture reads correctly from outside
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")  # same name as the other parts, so it survives the join
    vs = [bm.verts.new(P(sx + 0.01, y, z)) for y, z in ((y0, zc + w / 2), (y0, zc - w / 2), (y0 + h, zc - w / 2), (y0 + h, zc + w / 2))]
    f = bm.faces.new(vs)
    for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = (u, v)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(f"{name}Screen")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(f"{name}Screen", me)
    bpy.context.collection.objects.link(o)
    me.materials.append(_ad_material(file))
    o.parent = root
    # neon frame
    e = 0.12
    for k, (a0, a1, b0, b1, c0, c1) in enumerate(((sx, sx + 0.08, y0 - e, y0, zc - w / 2 - e, zc + w / 2 + e),
                                                   (sx, sx + 0.08, y0 + h, y0 + h + e, zc - w / 2 - e, zc + w / 2 + e),
                                                   (sx, sx + 0.08, y0, y0 + h, zc - w / 2 - e, zc - w / 2),
                                                   (sx, sx + 0.08, y0, y0 + h, zc + w / 2, zc + w / 2 + e))):
        slab(f"{name}Frame{k}", a0, a1, b0, b1, c0, c1, M["accent"], root)
    # brackets back to the facade
    for k, yy in enumerate((y0 + 1.0, y0 + h / 2, y0 + h - 1.0)):
        for j, zz in enumerate((zc - w / 3, zc + w / 3)):
            slab(f"{name}Bracket{k}{j}", x, sx - 0.3, yy - 0.12, yy + 0.12, zz - 0.12, zz + 0.12, M["frame"], root)


# ---------------------------------------------------------------- the new buildings
def build_g1_setback(parent=None, name="G1Tower"):
    """New building 1: one straight tower, the same footprint from bottom to top
    (no setback), 15 floors of dark glass, one lit floor near the top; amber accent.
    (The first version stepped in halfway up; the user found the wide base odd.)"""
    return glass_building(parent, name, tiers=[(17.0, 13.0, 15, (0.0, 0.0))],
                          accent="#ffb82e", seed=11)


def build_g2_block(parent=None, name="G2Block"):
    """New building 2: a wide, low straight block, 8 floors of dark glass over a
    26 x 18 m footprint, with a tall LED advert on its east side showing the
    image the user supplied (textures/banner_g2.png); cyan accent, no mast."""
    root = glass_building(parent, name, tiers=[(26.0, 18.0, 8, (0.0, 0.0))],
                          accent="#22e4ff", seed=22, mast=False)
    # the user's own banner image (textures/banner_g2.png, 736 x 1308): screen sized to its aspect
    ad_banner(root, f"{name}Ad", x=13.0, y0=5.5, h=23.0, w=23.0 * 736 / 1308, accent="#22e4ff", file="banner_g2.png")
    return root


def build_g2_preview(parent=None, name="G2Preview"):
    root = build_g2_block(parent, name)
    _preview_city(root)
    return root


def build_g3_slim(parent=None, name="G3Slim"):
    """New building 3: a tall, slim square tower, 13 x 13 m and 20 floors (~80 m) of
    dark glass, the same footprint top to bottom; pink accent, beacon mast."""
    return glass_building(parent, name, tiers=[(13.0, 13.0, 20, (0.0, 0.0))], accent="#ff4fd8", seed=33)


def build_g3_preview(parent=None, name="G3Preview"):
    root = build_g3_slim(parent, name)
    _preview_city(root)
    return root


def build_g4_slim_ad(parent=None, name="G4SlimAd"):
    """New building 4: a tall, slim square glass tower (13 x 13 m, 18 floors, ~75 m),
    straight top to bottom, all dark glass, with a tall narrow LED advert on its east
    side showing the original anime-style character (textures/anime_ad.png);
    pink accent, beacon mast."""
    root = glass_building(parent, name, tiers=[(13.0, 13.0, 18, (0.0, 0.0))], accent="#ff4fd8", seed=44)
    ad_banner(root, f"{name}Ad", x=6.5, y0=30.0, h=26.0, w=10.0, accent="#ff4fd8", file="anime_ad.png")
    return root


def build_g4_preview(parent=None, name="G4Preview"):
    root = build_g4_slim_ad(parent, name)
    _preview_city(root)
    return root


# ---------------------------------------------------------------- preview
def _preview_city(root):
    """Preview only: lit blocks round the building so the dark glass has city to reflect."""
    rng = random.Random(3)
    for k in range(36):
        ang = k / 36 * 2 * math.pi + rng.uniform(-0.05, 0.05)
        rad = rng.uniform(110, 150)
        w, h = rng.uniform(8, 16), rng.uniform(20, 70)
        x, z = math.cos(ang) * rad, math.sin(ang) * rad
        slab(f"PrevCityBlock{k}", x - w / 2, x + w / 2, 0, h, z - w / 2, z + w / 2, mat("PreviewCityBlock", "#0c0b14", 0.8), root)
        col = rng.choice(("#22e4ff", "#ff4fd8", "#ffb82e", "#ffd9a8"))
        for j in range(rng.randint(3, 7)):
            yy = rng.uniform(4, h - 2)
            slab(f"PrevCityLit{k}_{j}", x - w / 2 - 0.05, x + w / 2 + 0.05, yy, yy + rng.uniform(0.4, 2.0), z - w / 2 - 0.05, z + w / 2 + 0.05,
                 mat(f"PreviewCityLit{col[1:]}", col, emit=col, strength=3.0), root)
    for n, pos, col, e, sz in (("Fill", (-40, 40, 40), (0.55, 0.5, 1.0), 25000, 12), ("Street", (-20, 6, 25), (0.9, 0.5, 1.0), 20000, 6)):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = col
        ld.energy = e
        ld.shadow_soft_size = sz
        ld.specular_factor = 0.0  # no lamp discs mirrored in the glass
        lo = bpy.data.objects.new(n, ld)
        lo.visible_glossy = False  # Cycles: never mirror the lamp itself in the glass
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)


def build_g1_preview(parent=None, name="G1Preview"):
    root = build_g1_setback(parent, name)
    _preview_city(root)
    return root
