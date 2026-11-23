# Approved 3D assets

Assets are generated one at a time, reviewed from a preview render, and only
placed in the office (`build_office.py` → `office.glb`) once every asset is approved.

Preview any asset:

```
blender -b --python blender/objects/preview_object.py -- <module> <function> <out.png>
```

| # | Asset | Builder | Preview | Status |
|---|-------|---------|---------|--------|
| 1 | Gaming chair (black leather racing style, red piping) | `gaming_chair.py` → `build_gaming_chair(parent, name)` | `../previews/gaming_chair.png` | Approved 2026-11-21 — applied 2026-11-21 |
| 2 | Gaming desk (sit-stand frame, desk mat, headphone hook + RGB headphones, cup holder + can) | `gaming_desk.py` → `build_gaming_desk(parent, name, width=1.6, depth=0.75)` | `../previews/gaming_desk.png` | Approved 2026-11-21 — applied 2026-11-21 |

| 3 | Razer-style 27" monitor (Raptor-inspired: L stand, green cables, underglow; screen mesh `MonitorScreen`) | `razer_monitor.py` → `build_razer_monitor(parent, name)` | `../previews/razer_monitor.png` | Approved 2026-11-21 — applied 2026-11-21 |

| 4 | Razer-style full-size RGB keyboard (BlackWidow-inspired, rainbow Chroma backplate + legends, side underglow, media roller, wrist rest w/ RGB strip) | `razer_keyboard.py` → `build_razer_keyboard(parent, name, wrist_rest=True)` | `../previews/razer_keyboard.png`, `razer_keyboard_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |

| 5 | Razer-style RGB mouse (ergonomic, RGB wheel, hexagon palm glow, Chroma underglow) | `razer_mouse.py` → `build_razer_mouse(parent, name)` | `../previews/razer_mouse.png`, `razer_mouse_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |

**Apply stage started 2026-11-21** — all five assets placed in the People cluster via `build_office.py`.

Chroma lighting uses one shared rainbow texture in material `Razer_ChromaRGB` (UV u = left→right), so the site can scroll it for a wave effect.

Open question for the apply stage: chair piping + headphone RGB are red, Razer accent is green — ask the user whether to unify.

Preview command used for the desk: `... -- gaming_desk build_gaming_desk blender/previews/gaming_desk.png 2.15 6.0 2.15 "35,-35" 75`
(args after the output path: spacing, camera distance, camera height, view yaws, camera pitch)

## Loft revamp (started 2026-11-21)

Revamp of the whole office into a two-level loft (layout + colour-zone lighting
inspired by a reference image; normal room, no cutaway shell). Same workflow:
one asset at a time, preview, approval, apply only when everything is approved.
Characters and assets 1–5 above are reused.

| # | Asset | Builder | Preview | Status |
|---|-------|---------|---------|--------|
| L1 | Loft room structure (mezzanine, open copper stairs + railing, ducts, vents, pipework, big yellow window, orange doorway, blue alcove, zone markers) | `loft_room.py` → `build_loft_room(parent, name)` | `../previews/loft_room.png` (with placeholders), `loft_room_empty.png` | Approved 2026-11-21 — applied 2026-11-21 |

Preview command: `blender -b --python blender/objects/preview_room.py -- blender/previews/loft_room.png [blockout|empty] [lobby|front]`

Defaults used (user did not pick): upper left workstation = People, upper middle arcades = Lab,
window/pinboard = Services, lower level = Lobby; neon sign reads ASHETAG; two desks upstairs
(hero + typer), sleeper at the lower bar table; stylised materials first, baked textures later.
| L2 | Industrial wall fan unit (steel cabinet, two 1 m exhaust fans with wire grilles, side louvres, conduit, red status LED; rotors `FanRotor0/1` can spin on the site) | `fan_unit.py` → `build_fan_unit(parent, name)` | `../previews/fan_unit.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L3 | Wall bookshelf (3 × 3.2 m dark-wood shelves, steel L brackets, ~200 books in rows/leaning/flat stacks, boxes, bookends, gold-foil spine bands, teal LED under each shelf; books merged into one mesh per shelf) | `bookshelf.py` → `build_bookshelf(parent, name, length=3.2, shelves=3)` | `../previews/bookshelf.png`, `bookshelf_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L4 | Arcade cabinet pair (upright cabinets, cabinet silhouette, neon edge trim, lit marquee with 3D text, slanted screen + glow frame, joystick + 6 lit buttons + 2 start, asymmetric coin door). Blue "WHAT WE BUILD" = playable What We Build select screen (`ArcadeScreen`; marquee renamed from BLOCK CATCHER 2026-11-23), red (striped marquee, no title) = decor (`ArcadeScreen2`) | `arcade_cabinet.py` → `build_arcade_cabinet(...)`, `build_arcade_pair(parent, name)` | `../previews/arcade_cabinets.png`, `arcade_cabinets_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L5 | Loft bed (removed from the loft 2026-11-21, builder kept), cyberpunk (black steel platform bed, magenta neon underglow, cyan headboard light line, dark charcoal mattress/sheet/pillows, rumpled black duvet, black steel bedside crate with cyan edge light, warm globe lamp + phone) | `loft_bed.py` → `build_loft_bed(parent, name)` | `../previews/loft_bed.png`, `loft_bed_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L6 | Cyberpunk telescope (matte-black refractor + dew shield, cyan light rings, finder scope, focuser + eyepiece, black steel tripod with tray + spare eyepieces, red LED; tube on `TelescopePivot`) | `telescope.py` → `build_telescope(parent, name, tilt_deg=32)` | `../previews/telescope.png`, `telescope_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L7 | Holo Services board (hanging 2.2 m 16:9 holographic display = `TVScreen` for the live Services list, black bezel, cyan neon corner brackets, magenta status bar, suspension cables, 6 glowing note cards on the window wired to it with magenta neon lines) | `holo_board.py` → `build_holo_board(parent, name)` (preview: `build_holo_board_preview`) | `../previews/holo_board_dark.png`, `holo_board_angle.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L8 | Cyberpunk kitchenette (2.6 m gloss-black base cabinets, recessed plinth + pink toe-kick glow, dark steel worktop, sink + chrome tap, induction hob with red rings, built-in black washing machine with cyan door ring + display, dark tiled splashback, floating shelf with plates/bowls/jars + pink under-strip, kettle with cyan base, two mugs) | `kitchenette.py` → `build_kitchenette(parent, name)` | `../previews/kitchenette.png`, `kitchenette_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L9 | Neon wall sign ("ASHETAG" outline-style red neon tube lettering, rounded neon border, satin black acrylic backplate on steel standoffs, tube clips, transformer box + cable; text/colours are parameters) | `neon_sign.py` → `build_neon_sign(parent, name, text, color, border)` (preview: `build_neon_sign_preview`) | `../previews/neon_sign_dark.png` | Awaiting review |
| L10 | Lounge table + 3 stools (2.4 m black slab table at desk height 0.76 m on waterfall legs, cyan under-edge + leg glow strips, steel footrest + cable tray, tablet, two cans, papers; round black leather stools at 0.51 m with cyan under-seat ring + chrome foot ring) — sized so the sleeping character fits | `lounge_table.py` → `build_lounge_table(parent, name, stools=3)`, `build_lounge_stool(...)` | `../previews/lounge_table.png`, `lounge_table_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L11 | Cyberpunk e-moped (matte-black step-through scooter, sleek tapered rear body, padded seat with orange piping, glowing orange wheel rims + underglow + leg-shield strip, round headlight with cyan ring, cyan dash, red tail light, chrome spokes/grab rail, centre stand) | `e_moped.py` → `build_e_moped(parent, name)` | `../previews/e_moped.png`, `e_moped_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L12 | Cargo crate set (black chamfered hard-shell crates, lid band, red light strips on the front corners, steel latches + side handles, red status panel + LED, rubber feet; 4 sizes, one stacked, one angled) | `cargo_crate.py` → `build_cargo_crate(parent, name, size)`, `build_crate_set(parent, name)` | `../previews/cargo_crates.png`, `cargo_crates_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L13 | Cyberpunk vending machine (black cabinet with a 0.3 m deep blue-backlit display recess, five shelves of glowing cans with sold-out gaps, lit "DRINKS" header, keypad column with cyan screen, 12 keys, coin slot, card reader + green LED, change cup, pickup flap, cyan neon edges) | `vending_machine.py` → `build_vending_machine(parent, name, header)` | `../previews/vending_machine.png`, `vending_machine_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L14 | Cyberpunk boombox (black body, two big speakers with chrome surrounds, magenta light rings + grille bars, tweeters, cyan EQ display (bars `BoomboxEQ0-7` can animate), tape deck with reels, piano-key buttons, cyan-ringed volume knob, chrome handle + antenna) | `boombox.py` → `build_boombox(parent, name)` | `../previews/boombox.png`, `boombox_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L15 | Cyberpunk potted plant (snake plant, 11 twisting sword leaves with a folded midrib, tapered black concrete planter with green neon ring + rim, soil and pebbles, magenta grow-light on a stake; leaves merged into one mesh) | `potted_plant.py` → `build_potted_plant(parent, name, leaves=11, seed=2)` | `../previews/potted_plant.png`, `potted_plant_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |
| L16 | Floor cables (removed from the loft 2026-11-21, builder kept) (black junction box with green/amber/cyan status LEDs, four thick rubber cables snaking across the floor, steel collars with cyan glow rings at both ends, cyan + amber light segments along each run, loose coil at the end of the long cable) | `floor_cables.py` → `build_floor_cables(parent, name, seed=5)` | `../previews/floor_cables.png`, `floor_cables_dark.png` | Approved 2026-11-21 — applied 2026-11-21 |

**Style direction (user, 2026-11-21):** objects and room should look and feel cyberpunk — dark/black materials, neon light accents (magenta, cyan, plus the zone colours), no light/beige surfaces.

**Loft apply stage done 2026-11-21:** `build_office.py` now builds the loft with every
approved piece (layout: People = upper-left workstation with both Razer desk setups,
hero + typer, fan unit, bookshelf; Lab = arcade pair; Services = holo board in the
yellow window; bed + telescope; lower floor: kitchenette, ASHETAG neon, vending
machine, e-moped, lounge table with the sleeper, crates, boombox, plant, cables).
Site: zone lights + bloom in `components/Scene.tsx`, camera shots in `components/shots.ts`.
Check render: `blender -b blender/office.blend --python blender/render_loft.py -- out.png lobby`

## Additions after the loft apply

| # | Asset | Builder | Preview | Status |
|---|-------|---------|---------|--------|
| L17 | Glass room (3.2 × 3.0 × 2.6 m: black steel frame, tinted see-through glass walls + glass roof, sliding glass door with long handle, frosted privacy band, cyan neon on the roof edge + raised floor edge, magenta line on the door track) | `glass_room.py` → `build_glass_room(parent, name, w, d, h)` | `../previews/glass_room.png`, `glass_room_dark.png` | Approved + applied 2026-11-21 |
| L18 | Bean bag set (three slouchy bean bags with a rounded raised back, deep seat dent, soft wrinkles, carry loop and a glowing neon seam: charcoal/cyan, plum/magenta, teal/green) | `bean_bag.py` → `build_bean_bag(parent, name, fabric, seam, size, seed)`, `build_bean_bag_set(parent, name)` | `../previews/bean_bags.png`, `bean_bags_dark.png` | Approved + applied 2026-11-21 (replaced the bed under the window) |
| L19 | "SHA AREA" neon sign (same design as the ASHETAG sign: red outline neon lettering, rounded neon border, satin black acrylic on standoffs, transformer + cable) | `neon_sign.py` → `build_neon_sign(parent, name, text="SHA AREA")` (preview: `build_sha_area_sign_preview`) | `../previews/neon_sign_sha_area.png` | Approved + applied 2026-11-21 (outside of the glass room's right wall) |

Applied 2026-11-21: glass room placed in the lower-left front corner (centre
x -5.35, z 1.5); the crate set that stood there was removed (user's call). The solo
crate by the stairs stays.

## Furnishing round (2026-11-21)

Agreed list: lounge set, hanging lights, server rack, pinball machine, left-wall LED
mural/posters, mini fridge (upstairs), one glass-room theme, small clutter + hanging plant.

| # | Asset | Builder | Preview | Status |
|---|-------|---------|---------|--------|
| F1 | Lounge set (3.4 × 2.6 m dark rug with cyan neon edge + faint stripes; black L-shaped sectional with seat/back cushions, magenta underglow, cyan + magenta throw pillows; low black coffee table with cyan edge, hologram projector (cone beam + spinning-ready wireframe shape `LoungeSetHoloShape`), can + remote) | `lounge_set.py` → `build_lounge_set(parent, name)` | `../previews/lounge_set.png`, `lounge_set_dark.png` | Approved + applied 2026-11-21 |
| F2 | Hanging lights, three kinds for under the mezzanine (cyan neon bar pendant in a black channel on two cables; cluster of five warm amber filament bulbs at staggered heights; magenta neon ring pendant on three cables; cable lengths adjustable) | `hanging_lights.py` → `build_neon_bar_pendant`, `build_bulb_cluster`, `build_ring_pendant` (preview: `build_hanging_lights_preview`) | `../previews/hanging_lights_dark.png` | Approved + applied 2026-11-21 |
| F3 | Server rack pair (two 2 m black 42U cabinets on castors, tinted glass doors in steel frames with handles, stacked 1-4U servers with green/cyan/amber status LEDs + drive bays, patch panel with blue/magenta/green/amber cables, top vents, cyan edge + top strips; LEDs merged per rack) | `server_rack.py` → `build_server_rack(parent, name, seed)`, `build_server_rack_pair(parent, name)` | `../previews/server_racks.png`, `server_racks_dark.png` | Approved + applied 2026-11-21 |
| F4 | Pinball machine (original design: black cabinet on chrome legs, sloped playfield under glass with magenta/cyan/yellow pop bumpers, flippers, cyan slingshots, chrome wire ramp, lane guides, lit arrow inserts, steel ball; backbox with synthwave backglass art (neon sun over grid, no text, plane `PinballBackglass`), magenta/cyan neon trim, coin door, start button, plunger) | `pinball.py` → `build_pinball(parent, name)` | `../previews/pinball.png`, `pinball_dark.png` | Approved + applied 2026-11-21 |
| F5 | Wall art (original, generated in code): 4 × 2.2 m LED mural showing a night city skyline with lit windows, neon rooftop strips and a magenta moon ring, in a black frame with brackets + cyan top light (screen plane `LEDMuralScreen`); three neon-framed posters (concentric circles / magenta, diagonal stripes + triangle / cyan, wave lines / yellow) | `wall_art.py` → `build_led_mural`, `build_poster(art=circles|stripes|wave)` (preview: `build_wall_art_preview`) | `../previews/wall_art_dark.png` | Approved + applied 2026-11-21 |
| F6 | Mini drinks fridge (compact black glass-door fridge, blue-lit interior, two wire shelves of glowing cans + two bottles, chrome bar handle, cyan badge + base glow, snack box and a can on top; drinks merged into one mesh) | `mini_fridge.py` → `build_mini_fridge(parent, name, seed)` | `../previews/mini_fridge.png`, `mini_fridge_dark.png` | Approved + applied 2026-11-21 |
| F7 | Glass-room meeting set (user's choice: round black pedestal table with cyan under-glow ring + four black swivel chairs with 5-star bases, chrome lifts and cyan accents; open black shelving rack for the solid wall with storage boxes, books, binders, a speaker with cyan ring, trophy, small plant and cyan shelf lights) | `meeting_set.py` → `build_meeting_table_set`, `build_wall_rack` (preview in the glass room: `build_meeting_room_preview`) | `../previews/meeting_room_dark.png`, `meeting_set.png`, `wall_rack.png` | Approved + applied 2026-11-21 |
| F8 | Small props + hanging plant (skateboard with kicktails, magenta grip stripe, glowing cyan wheels; black electric guitar with cyan edge line, chrome pickups/strings on an A-frame stand; three stacked pizza boxes; energy-drink can cluster with a crushed can; headphone stand with magenta-ringed headphones + cyan base glow; hanging plant on three cords with trailing vines + cyan pot ring) | `clutter.py` → `build_skateboard`, `build_guitar_on_stand`, `build_pizza_boxes`, `build_can_cluster`, `build_headphone_stand`, `build_hanging_plant` (preview: `build_clutter_preview`) | `../previews/clutter.png`, `clutter_dark.png` | Approved + applied 2026-11-21 |

**Furnishing round applied 2026-11-21** (`build_office.py`, section "FURNISHING ROUND"): lounge set on
the open front floor; bulb cluster over the kitchen, neon bar by the vending machine, ring pendant by
the ASHETAG sign; server racks in the back-right corner beside the riser pipes (moved 2026-11-21); pinball side-on at the front right; LED mural high
on the left wall; three posters on the lower back wall; mini fridge + guitar upstairs; headphone stand
on the hero's desk; cans by the bean bags; pizza boxes + skateboard near the sofa; two hanging plants
on arms off the mezzanine railing; meeting table + rack inside the glass room. Site: extra zone lights
and a spinning hologram (`LoungeSetHoloShape`) in `components/Scene.tsx`.

## City models (2026-11-22)

The outside city is code-generated on the site (`components/CityScape.tsx`, approved look:
open view, purple haze, spire + beam, rain). These models replace its plain boxes once approved.
Preview script for city-scale pieces: `blender/objects/preview_city.py`.

| # | Asset | Builder | Preview | Status |
|---|-------|---------|---------|--------|
| C1 | Building kit, 5 low-poly designs sharing one world-mapped window texture (stepped tower with corner fins + antenna, octagonal ring tower with cyan ring balconies + dish, billboard slab with giant lit billboard + ribs + AC units, twin towers with neon sky-bridge, low-rise block with water tank / AC / stair hut / rooftop sign) | `city_buildings.py` → `build_stepped_tower`, `build_ring_tower`, `build_billboard_tower`, `build_twin_towers`, `build_lowrise_block` | `../previews/city_buildings.png` | Rejected (user wants simple blocky street buildings instead) |
| C2 | Blocky neon street building (style ref: foggy cyberpunk street block). Three joined sections: 2-storey BAR (lantern sign, purple shopfront, rooftop AC + red-beacon antennas), 3-storey GARAGE (cyan-framed roller door, big sign, blue windows, balcony), 4-storey red block (stepped awning, red windows, pink tubes, vertical bulb sign, rooftop billboard). Pixel-stone texture, sidewalk + curb, pipes, wall lamps | `city_street.py` → `build_street_building` | `../previews/city_street.png` | Approved, placed |
| C3 | Cyberpunk supercar (style ref: low wedge supercar; original design). Lofted crease-sharp body, orange-red paint over dark lower body, twin vertical LED bars on the front corners, aero disc front wheels, dark five-spoke rear rims, red tail bar. Variants: any paint colour, `hover=True` swaps wheels for pink thruster pods | `city_cars.py` → `build_street_car` | `../previews/city_car_hero.png`, `../previews/city_cars.png` | Approved, placed |
| C4 | Smooth neon-night tower, variant 1 (style ref: soft rounded futuristic architecture, kept in the night palette). Rounded floor plates, wrap-around curved balconies with glass railings and cyan neon edges, lit window texture, warm glass lobby with a deep canopy, round glass stair tower, rooftop garden with trees and a glass pavilion. Accent colour and window pattern are parameters | `city_smooth.py` → `build_smooth_tower` | `../previews/city_smooth.png` | Approved, removed 2026-11-22 (replaced by new buildings in the office tower style) |
| C5 | Smooth neon-night tower, variant 2: slim stadium-plan shaft in three tiers stepping back with glass-railed terraces and pink neon lips, thin floor fins, mostly solid cladding with few lit windows, LED ad screens on the middle and top tiers, a red glyph banner blade, a wrap-around LED ticker on the podium, a rooftop letter sign, short glowing spine, two-storey rounded podium with warm glass shopfront and planted roof, crown with a neon halo ring, glass penthouse and beacon antenna (~66 m) | `city_smooth.py` → `build_smooth_slim` | `../previews/city_smooth_slim.png` | Approved, removed 2026-11-22 (replaced by new buildings in the office tower style) |
| C6 | Smooth neon-night block, variant 3: wide stepped building, four rounded two-storey levels stepping back so each has a planted terrace with glass rail and amber neon lip; mostly solid cladding with few lit windows, LED ticker round the warm glass base, two red glyph banner blades on the right, a wide drink-can product billboard on a rooftop scaffold, AC units, beacon (~37 m) | `city_smooth.py` → `build_smooth_terrace` | `../previews/city_smooth_terrace.png` | Approved, removed 2026-11-22 (replaced by new buildings in the office tower style) |
| C7 | Smooth neon-night tower, variant 4: soft-square tower (big corner radii) (corner LED screen removed at review), mint-green neon ring bands every three floors, mostly solid cladding, warm glass lobby under a deep canopy, red glyph banner on the left, rooftop helipad with lit ring and H marking, twin beacon masts (~44 m) | `city_smooth.py` → `build_smooth_corner` | `../previews/city_smooth_corner.png` | Approved, removed 2026-11-22 (replaced by new buildings in the office tower style) |
| C8 | Canal road segment (40 m, one side): canal ledge with glass railing and cyan neon base strip, two asphalt lanes with dashed yellow centre line and white edge lines, rounded curb with neon strip, drain grates, tiled running-bond sidewalk; crosswalk variant with zebra stripes, stop lines and tactile paving | `city_roads.py` → `build_road_segment` | `../previews/city_roads.png` | Approved, retired (canal now sits in the unified grid between two city streets) |
| C9 | Street lamp: 7.2 m slim tapered pole on a round base, glowing accent ring (cyan / pink / amber), curved arm over the road, flat head with a warm-white light panel and neon top line; twin-arm variant for medians | `city_roads.py` → `build_street_lamp` | `../previews/city_roads.png` | Approved, placed |
| C10 | City grid street (two lanes, sidewalks both sides, neon curb strips, drains; 17.5 m wide incl. sidewalks) and four-way crossroads tile (zebra crossings and stop lines on all arms, rounded corner sidewalks with neon edges, lamps on two corners) | `city_roads.py` → `build_street_segment`, `build_intersection` | `../previews/city_streets.png` | Approved, placed |
| C11 | Traffic light: tapered pole with neon ring, curved-brace mast arm (5 m) with neon line, two rounded signal heads (red / amber / green lenses with visors) on neon-edged backplates, pedestrian box (stop hand / walk). Lens materials keep fixed names (Loft_SignalRed/Amber/Green/Walk/Stop) so the site can cycle them per crossroads | `city_roads.py` → `build_traffic_light` | `../previews/city_traffic_lights.png` | Approved, placed |
| C12 | Plaza furniture kit: rounded planter with neon rim, tree and shrubs; curved-edge bench with neon underglow; noodle kiosk (rounded cabin, warm serving hatch and counter, red awning with neon edge, glowing NOODLES sign, two stools); bollard with glowing top ring; flush round floor light. Shown with the approved vending machine (L13) | `city_plaza.py` → `build_plaza_planter`, `build_plaza_bench`, `build_plaza_kiosk`, `build_plaza_bollard`, `build_plaza_floor_light` | `../previews/city_plaza.png` | Approved, removed (user: plazas made no sense in the layout) |

## Office building (2026-11-22)

| # | Asset | Builder | Preview | Status |
|---|-------|---------|---------|--------|
| B1 | Minimalist glass tower for the office: same footprint as the condo; nine 4 m floors glazed exactly like the office level (two floor-to-ceiling panes per wall, one slim mullion, thin black sill and head, glass-to-glass corners), thin dark slabs with a light edge line, near-black glossy glass on all lower floors (no interiors, only faint reflections of the city lights); office level on top with floor-to-ceiling glass on the back and left walls (one slim mullion each, frameless glass corner, thin black sill/head), white ceiling slab with downlights, cyan neon crown line, full-height pink neon corner line, lobby canopy with cyan line, rooftop box and beacon mast | `minimal_tower.py` → `build_minimal_tower` | `../previews/minimal_tower.png` | Approved, applied (loft left wall → glass; back wall kept solid at the user's request; tower under the office in the city) |

## New city buildings in the office tower's design (2026-11-22)

All use the B1 glazing: two floor-to-ceiling panes per wall (one slim mullion), thin black sill/head, glass-to-glass corners, slim dark slabs with a light edge line, near-black reflective glass, sparing neon. Builder: `glass_city.py` (`glass_building` generator).

| # | Asset | Builder | Preview | Status |
|---|-------|---------|---------|--------|
| G1 | Straight glass tower (reworked: the first version had a wider 6-floor base under a set-back tower, which looked odd): 15 floors, 17�13 m, same footprint top to bottom; all floors dark glass (its lit floor was removed: no clear glass on any G building, user 2026-11-22); amber crown line, amber corner line, lobby canopy, beacon mast (~60 m) | `build_g1_setback` | `../previews/glass_g1.png` | Approved, retired (user: no tall buildings round the office) |
| G2 | Wide low glass block: 8 floors, 26x18 m, straight, all dark glass (no clear/lit floors); tall LED advert on the east side (12.9x23 m, neon frame, brackets) showing the image the user supplied (`textures/banner_g2.png`; third-party fan art, user to confirm rights before publishing); cyan crown line, cyan corner line, lobby canopy, no mast (~33 m) | `build_g2_block` | `../previews/glass_g2.png` | Approved, placed |
| G3 | Ramen corner shop (replaces the slim glass tower; built from scratch following the user's reference): two-storey corner building on a broken tiled platform. Ground: open ramen stall (counter, bowls, stools, red awning, red neon ramen sign, tube lights), small shop with lit door, barred window and tiled canopy, corner pipe. Upper: rounded concrete box with a wide open window into a lit room (sofa, tiled floor, blue/yellow walls), taller block with a big round louvred vent, roof garden with two bonsai trees, AC units and cables. Tall glowing vertical kanji sign with a street lamp, utility pole with insulators, cables and a lit metro sign, metro stair entrance with railings and green glow, boxes, caution sign, barrier with beacon (~10 m tall, 14x14 m platform) | `ramen_corner.py` -> `build_ramen_corner` | `../previews/ramen_corner.png` | Approved, placed |
| G4 | Neon courtyard block (replaces the slim ad tower; built from scratch following the user's reference, with our own sign texts and car instead of real brands): two-storey garage/showroom with a big cyan NEON MOTORS sign and pink script line, lit blinds windows, open garage bay, pink neon arrow; taller three-storey HOTEL building with a vertical red sign, wide cyan-lit shutter band, warm top windows, Bar neon, red door, fire ladder, roof AC units, dish and vent stack; wet asphalt yard with the approved supercar (cyan underglow), utility pole with transformer and a tangle of cables, rusty barrels, crowd fence, puddles, trash; on a raised 16x16 m base (~11 m tall) | `neon_alley.py` -> `build_neon_alley` | `../previews/neon_alley.png` | Approved, placed |

## Office corner (2026-11-22)

| # | Asset | Builder | Preview | Status |
|---|-------|---------|---------|--------|
| F9 | Sim-racing rig (replaces the glass room + SHA AREA sign + meeting set, removed at the user's request): black aluminium-profile cockpit on a mat with cyan neon border, magenta underglow, bucket seat with neon piping, wheel with rev LEDs, pedals, shifter, three screens wrapping toward the seat showing an original night-race picture (make_race_screens.py) | `sim_racing.py` -> `build_sim_rig(parent, name)` | `../previews/sim_rig_dark.png`, `../previews/sim_rig_top.png` | Approved + applied 2026-11-22 (front-left corner, screens against the glass wall) |


## Chill area (2026-11-23)

| # | Asset | Module | Preview | Status |
|---|-------|--------|---------|--------|
| F10 | Big TV on slatted media console, violet backlight strip, original console home screen | `chill_area.py` -> `build_big_tv`, `make_console_home.py` | `../previews/chill_tv.png` | Approved 2026-11-23 - applied |
| F11 | Original next-gen console (white shells, black core, cyan seams) | `chill_area.py` -> `build_console` | `../previews/chill_console.png` | Approved 2026-11-23 - applied |
| F12 | Two original controllers (cyan + pink light bars, plain coloured buttons) | `chill_area.py` -> `build_controller` | `../previews/chill_controllers.png` | Approved 2026-11-23 - applied |
| F13 | Big synthwave floor rug (3.4 x 3.2 m in place) | `chill_area.py` -> `build_rug`, `make_chill_rug.py` | `../previews/chill_rug.png` | Approved 2026-11-23 - applied |
| F14 | Lounger bean bags x3 (cream, lilac, burnt orange) | `chill_area.py` -> `build_lounger` | `../previews/chill_loungers.png` | Approved 2026-11-23 - applied |

Placed together as `ChillSpot` (-5.25, 0, -0.375), yaw 90: TV against the left glass wall facing into the room.


## Bar (2026-11-23)

| # | Asset | Module | Preview | Status |
|---|-------|--------|---------|--------|
| F15 | Bar counter (ribbed, cyan edge glow, magenta under-glow, chrome foot rail) + back bar (glass shelves, amber under-shelf LEDs, neon BAR sign) | `bar.py` -> `build_bar_counter`, `build_back_bar` | `../previews/bar_counter.png` | Approved 2026-11-23 - applied |
| F16 | Drinks: ~45 unbranded bottles, upturned glasses, 3 cocktails, shaker, 3 cans | `bar.py` -> `build_back_bar_drinks`, `build_counter_drinks` | `../previews/bar_drinks.png` | Approved 2026-11-23 - applied |
| F17 | Snacks: crisps, nachos on slate, nuts, striped popcorn bucket | `bar.py` -> `build_bar_snacks` | `../previews/bar_snacks.png` | Approved 2026-11-23 - applied |

Placed as `BarSpot` (-1.85, 0, -4.44): back bar against the back wall (covers the three wall posters), counter facing the room, ring pendant above it. Bar + chill area are merged into one mesh each at build time (`merge_into` in build_office.py) to keep draw calls down.


## Workstation monitors (2026-11-23)

| # | Asset | Module | Preview | Status |
|---|-------|--------|---------|--------|
| F18 | 40"-class curved ultrawide on a short stand, cyan back/chin light bars; screens: code editor + repo page (original UI, git.ashetag.dev) | `dev_monitor.py` -> `build_dev_monitor`, `make_dev_screens.py` | `../previews/dev_monitors.png` | Approved 2026-11-23 - applied (replaces the Razer-style monitors on both desks) |
| F19 | Low vinyl-record cabinet for the boombox (record sleeves, amp, cyan lip strip, pink underglow); placed behind the lounge sofa, open front toward the camera, boombox on top | `boombox_stand.py` -> `build_boombox_stand` | `../previews/boombox_stand.png`, `../previews/boombox_stand_placed.png` | Approved 2026-11-24 - applied (BoomboxStandSpot; boombox moved onto it) |
| F20 | Cyberpunk street tree: forked dark trunk, faceted low-poly canopy (green / teal), warm + pink fairy lights, square concrete planter with grate and cyan neon lip (~1.8k tris) | `street_tree.py` -> `build_street_tree` | `../previews/street_tree.png` | Approved 2026-11-24 - applied (three variations StreetTree1-3 in city.glb; ~140 instanced along the sidewalks near the office, StreetTrees in CityScape.tsx) |
