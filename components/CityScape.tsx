'use client'

// The city outside. The loft is the top floor of a mid-height condo standing in
// one connected street grid (see "city grid" below): approved smooth neon-night
// buildings (C4-C7) fill the blocks, a glowing canal runs south from the tower
// under bridging cross streets, supercars (C3) drive every street and stop at the
// traffic lights (C11) near the office, and the skyline stands in purple haze
// beyond. Models come from public/models/city.glb (blender/build_city.py).
//
// Office floor is y = 0; the street is GROUND metres below it.

import { useGLTF } from '@react-three/drei'
import { useFrame, useThree } from '@react-three/fiber'
import { Suspense, useEffect, useMemo, useRef } from 'react'
import * as THREE from 'three'
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js'

const GROUND = 36
/** The night haze: distant things fade into it and it is the sky's glowing horizon. */
export const CITY_HAZE = '#3a1a4c'
const ORIGIN = new THREE.Vector2(0.8, -1.0) // centre of the condo tower (x, z)
// horizontal direction the lobby camera looks in (camera -> target)
const VIEW = new THREE.Vector2(-0.623, -0.782).normalize()

function rng(seed: number) {
  let s = seed >>> 0
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0
    return s / 4294967296
  }
}

/* ------------------------------------------------------------------ city grid */

// One connected street grid, square to the office (and to the condo tower under
// it). Every street runs the full width of the city and meets every cross street
// at a crossroads tile, so there are no dead ends. The tower sits in its own
// block in the middle; the canal runs straight south from it between the two
// north-south streets either side of the tower, with the cross streets passing
// over it as bridges. Every other block holds one building sized to fill it.
// Past the edge of the grid the skyline towers stand in the haze.

const CITY_URL = '/models/city.glb?v=18'
const DRACO_URL = '/draco/'
const XR_HALF = 8.75 // half a street incl. sidewalks (= half the crossroads tile)
const LANE_OFF = 2.2
const STOP_BACK = 8.05 // car centre stops this far before a crossroads centre
const CAR_GAP = 7 // centre-to-centre gap kept to the car in front
// a car's centre is in a crossroads' conflict box between these distances past its stop line
const CLAIM_MARGIN = 8 // claim a crossroads this far beyond braking distance
const BOX_OUT = STOP_BACK + 6.9
const SPACING = 45 // street centre to street centre
const RINGS = 5 // streets on each side of the tower ring
const EDGE = 30 // how far streets run past the outermost cross street
// the tower ring, then every 45 m outward
const GRID_X = [
  ...Array.from({ length: RINGS + 1 }, (_, k) => -16.5 - SPACING * k).reverse(),
  ...Array.from({ length: RINGS + 1 }, (_, k) => 18.1 + SPACING * k),
] // streets running along Z, at these x
const GRID_Z = [
  ...Array.from({ length: RINGS + 1 }, (_, k) => -15.55 - SPACING * k).reverse(),
  ...Array.from({ length: RINGS + 1 }, (_, k) => 13.55 + SPACING * k),
] // streets running along X, at these z
const X0 = GRID_X[0] - EDGE, X1 = GRID_X[GRID_X.length - 1] + EDGE
const Z0 = GRID_Z[0] - EDGE, Z1 = GRID_Z[GRID_Z.length - 1] + EDGE
const CANAL_X = 0.8, CANAL_HALF = 7 // canal centre / half width, between the two ring streets
const CANAL_TOP = GRID_Z[RINGS] // the ring street south of the tower: the canal starts below it
const SIGNAL_R = 70 // crossroads closer than this to the office get traffic lights

type GridLine = { axis: 'x' | 'z'; c: number; from: number; to: number; cross: number[] }
// axis 'x' = the street runs along X at z = c
const GRID_LINES: GridLine[] = [
  ...GRID_Z.map((c) => ({ axis: 'x' as const, c, from: X0, to: X1, cross: GRID_X })),
  ...GRID_X.map((c) => ({ axis: 'z' as const, c, from: Z0, to: Z1, cross: GRID_Z })),
]
const lineWorld = (l: GridLine, along: number, across: number) =>
  l.axis === 'x' ? new THREE.Vector3(along, 0, l.c + across) : new THREE.Vector3(l.c + across, 0, along)
const crossId = (x: number, z: number) => GRID_X.indexOf(x) * GRID_Z.length + GRID_Z.indexOf(z)
const signalled = (x: number, z: number) => Math.abs(x - ORIGIN.x) < SIGNAL_R && Math.abs(z - ORIGIN.y) < SIGNAL_R

/** One building copy: which model (index into BUILDINGS), ground position, facing angle (front = +Z), uniform scale. */
type Placement = { m: number; x: number; z: number; rot: number; s: number }
// approved smooth neon-night buildings (C4-C7), origin at the centre of the plan,
// and their footprints at scale 1 (width along X, depth along Z, facing +Z)
const SHOW_BUILDINGS = true
// approved city buildings: the dark-glass block with the advert (G2) and the two
// street-level neon dioramas (G3 ramen corner, G4 neon courtyard), with footprints at
// scale 1 (w along X, d along Z, facing +Z). The tall glass tower (G1) is not used.
const BUILDINGS = ['GlassBlock', 'RamenCorner', 'NeonAlley']
const FOOTPRINT: [number, number][] = [[27.6, 18.8], [16.0, 17.0], [16.0, 16.0]]
const MAX_SCALE = 1.5
// Blocks whose advert stays in frame AND unblocked from the lobby camera on desktop and
// on phones (checked by projecting/ray-casting the banner against the office from the
// lobby shot at 4:3 and 375x812). Only these get the advert block, banner turned to the camera.
const AD_SPOTS: [number, number][] = [[-84, -38.05], [-129, -83.05], [-39, -173.05]]
const LOBBY_CAM = new THREE.Vector2(9.2, 9.6)

function useLayout() {
  return useMemo(() => {
    const r = rng(2024)
    const out: Placement[] = []
    // one building per block, front facing the street on the office side
    for (let i = 0; i < GRID_X.length - 1; i++)
      for (let j = 0; j < GRID_Z.length - 1; j++) {
        const xa = GRID_X[i] + XR_HALF, xb = GRID_X[i + 1] - XR_HALF
        const za = GRID_Z[j] + XR_HALF, zb = GRID_Z[j + 1] - XR_HALF
        if (GRID_X[i] === -16.5 && GRID_X[i + 1] === 18.1) continue // the tower block and the canal
        const cx = (xa + xb) / 2, cz = (za + zb) / 2
        const bw = xb - xa, bd = zb - za
        const dx = ORIGIN.x - cx, dz = ORIGIN.y - cz
        const alongZ = Math.abs(dz) >= Math.abs(dx) // face north/south, else east/west
        const rot = alongZ ? (dz > 0 ? 0 : Math.PI) : dx > 0 ? Math.PI / 2 : -Math.PI / 2
        if (AD_SPOTS.some(([ax, az]) => Math.abs(ax - cx) < 1 && Math.abs(az - cz) < 1)) {
          // advert block: banner (its local +X side) turned to the lobby camera, snapped to the grid
          const ux = LOBBY_CAM.x - cx, uz = LOBBY_CAM.y - cz
          const faceX = Math.abs(ux) >= Math.abs(uz)
          const adRot = faceX ? (ux > 0 ? 0 : Math.PI) : uz > 0 ? -Math.PI / 2 : Math.PI / 2
          const [fw, fd] = faceX ? FOOTPRINT[0] : [FOOTPRINT[0][1], FOOTPRINT[0][0]]
          out.push({ m: 0, x: cx, z: cz, rot: adRot, s: Math.min(1.3, (0.94 * bw) / fw, (0.94 * bd) / fd) })
          continue
        }
        // every other block: one of the two street-level dioramas, filling the block,
        // never the same as the block next door
        const prev = out[out.length - 1]
        const m = prev && prev.m === 1 ? 2 : prev && prev.m === 2 ? 1 : r() < 0.5 ? 1 : 2
        const [fw, fd] = alongZ ? FOOTPRINT[m] : [FOOTPRINT[m][1], FOOTPRINT[m][0]]
        out.push({ m, x: cx, z: cz, rot, s: Math.min(MAX_SCALE, (0.94 * bw) / fw, (0.94 * bd) / fd) })
      }
    return out
  }, [])
}

/* ------------------------------------------------------------------ models */

type ModelPart = { geometry: THREE.BufferGeometry; material: THREE.Material; paint: boolean }

// key light from over the viewer's shoulder so the walls we look at read, roofs a bit less
const MOON_DIR = new THREE.Vector3(-VIEW.x, 1.1, -VIEW.y).normalize()
const SHADOW_FILL = new THREE.Color(0.2, 0.15, 0.3)
/** Bakes a soft moonlight + violet haze fill into a geometry's vertex colours (for unlit city buildings). */
function shadeMoonlit(g: THREE.BufferGeometry) {
  const n = g.getAttribute('normal')
  const col = new Float32Array(n.count * 3)
  const v = new THREE.Vector3()
  for (let i = 0; i < n.count; i++) {
    v.fromBufferAttribute(n, i)
    const k = 0.55 * Math.max(0, v.dot(MOON_DIR)) + 0.12 * Math.max(0, v.y)
    col[i * 3] = SHADOW_FILL.r + k
    col[i * 3 + 1] = SHADOW_FILL.g + k * 0.95
    col[i * 3 + 2] = SHADOW_FILL.b + k * 1.05
  }
  g.setAttribute('color', new THREE.BufferAttribute(col, 3))
}

/** The approved models as instancing-ready parts (one per material). Cars are turned to face +Z. */
function useCityModels() {
  const { scene } = useGLTF(CITY_URL, DRACO_URL)
  return useMemo(() => {
    const get = (name: string, turn: boolean) => {
      const parts: ModelPart[] = []
      const node = scene.getObjectByName(name)
      node?.updateMatrixWorld(true)
      node?.traverse((o) => {
        const m = o as THREE.Mesh
        if (!m.isMesh) return
        const geometry = m.geometry.clone().applyMatrix4(m.matrixWorld)
        if (turn) geometry.rotateY(-Math.PI / 2) // model drives toward +X, lookAt wants +Z
        const src = m.material as THREE.MeshStandardMaterial
        let material: THREE.Material = src.clone()
        const emissive = src.emissive && src.emissive.getHex() !== 0
        if (BUILDINGS.includes(name) && !emissive && !src.transparent && !src.name.includes('DarkGlass')) {
          // The city has no real lights on these models (their neon is emissive only), so lit
          // by the faint sky alone they read as flat grey blocks. Render them unlit in their own
          // colours with a fixed moonlight baked into vertex colours: roofs catch the moon, walls
          // facing away fall dark, and a little haze-violet fills the shadows.
          shadeMoonlit(geometry)
          const color = src.color.clone()
          const hsl = { h: 0, s: 0, l: 0 }
          color.getHSL(hsl)
          // daylight concrete/tile greys become night slate with a hint of violet
          if (hsl.s < 0.2 && !src.map) color.setHSL(0.74, 0.22, hsl.l * 0.55)
          material = new THREE.MeshBasicMaterial({ name: src.name, color, map: src.map ?? null, vertexColors: true, side: src.side })
        }
        parts.push({ geometry, material, paint: src.name.includes('CarPaint') })
      })
      return parts
    }
    return {
      buildings: BUILDINGS.map((n) => get(n, false)),
      car: get('Car', true),
      lamps: [get('LampCyan', false), get('LampPink', false)],
      street: get('Street20', false),
      crossroads: get('Crossroads', false),
      signal: get('TrafficLight', false),
      tower: get('MinimalTowerBase', false),
    }
  }, [scene])
}

/** Every part of a model as one InstancedMesh; matrices come from a shared array (copied each frame when live). */
function ModelInstances({ parts, matrices, count, colors, live }: { parts: ModelPart[]; matrices: Float32Array; count: number; colors?: THREE.Color[]; live?: boolean }) {
  const refs = useRef<(THREE.InstancedMesh | null)[]>([])
  const setRef = (i: number) => (m: THREE.InstancedMesh | null) => {
    refs.current[i] = m
    if (!m || m.userData.filled) return
    m.instanceMatrix.array.set(matrices)
    m.instanceMatrix.needsUpdate = true
    if (colors && parts[i].paint) {
      colors.forEach((c, k) => m.setColorAt(k, c))
      if (m.instanceColor) m.instanceColor.needsUpdate = true
    }
    m.userData.filled = true
  }
  useFrame(() => {
    if (!live) return
    refs.current.forEach((m) => {
      if (!m) return
      m.instanceMatrix.array.set(matrices)
      m.instanceMatrix.needsUpdate = true
    })
  })
  return (
    <>
      {parts.map((p, i) => (
        <instancedMesh key={i} ref={setRef(i)} args={[p.geometry, p.material, count]} frustumCulled={false} />
      ))}
    </>
  )
}

function StreetBuildings({ list }: { list: Placement[] }) {
  const { buildings } = useCityModels()
  const groups = useMemo(
    () =>
      buildings.map((_, m) => {
        const mine = list.filter((p) => p.m === m)
        const arr = new Float32Array(mine.length * 16)
        const o = new THREE.Object3D()
        mine.forEach((p, i) => {
          o.position.set(p.x, -GROUND, p.z)
          o.rotation.set(0, p.rot, 0)
          o.scale.setScalar(p.s)
          o.updateMatrix()
          o.matrix.toArray(arr, i * 16)
        })
        return { count: mine.length, matrices: arr }
      }),
    [buildings, list],
  )
  return (
    <>
      {buildings.map((parts, m) =>
        groups[m].count ? <ModelInstances key={m} parts={parts} matrices={groups[m].matrices} count={groups[m].count} /> : null,
      )}
    </>
  )
}

/** The approved minimalist tower (B1) under the office: nine floors of near-black
 * glass in the office's two-pane glazing. Once the city has loaded, one snapshot
 * of it is taken from inside the tower so the glass reflects the real neon streets. */
function TowerBase() {
  const { tower, buildings } = useCityModels()
  const { gl, scene } = useThree()
  const group = useRef<THREE.Group>(null)
  const matrices = useMemo(() => {
    const o = new THREE.Object3D()
    o.position.set(0, -GROUND, 0) // the model's ground is y = 0; the office floor sits at its y = 36
    o.updateMatrix()
    return new Float32Array(o.matrix.toArray())
  }, [])
  useEffect(() => {
    const rt = new THREE.WebGLCubeRenderTarget(256, { type: THREE.HalfFloatType })
    const cam = new THREE.CubeCamera(1, 1500, rt)
    cam.position.set(ORIGIN.x, -GROUND + 18, ORIGIN.y)
    const id = setTimeout(() => {
      const g = group.current
      if (!g) return
      g.visible = false // don't reflect the tower in itself
      cam.update(gl, scene)
      g.visible = true
      ;[...tower, ...buildings.flat()].forEach((p) => {
        if (p.material.name !== 'Loft_MinDarkGlass') return
        const m = p.material as THREE.MeshStandardMaterial
        m.envMap = rt.texture
        m.envMapIntensity = 1.4
        m.needsUpdate = true
      })
    }, 1500)
    return () => {
      clearTimeout(id)
      rt.dispose()
    }
  }, [gl, scene, tower, buildings])
  return (
    <group ref={group}>
      <ModelInstances parts={tower} matrices={matrices} count={1} />
    </group>
  )
}

/** Ground: dark city floor, and the canal in stretches between the cross streets
 * (the streets pass over it as bridges), each with a stone ledge (no neon edge). */
function Ground() {
  const canalTex = useMemo(() => {
    const c = document.createElement('canvas')
    c.width = 64
    c.height = 256
    const g = c.getContext('2d')!
    const grd = g.createLinearGradient(0, 0, 0, 256)
    // dark night water (it used to glow neon violet)
    grd.addColorStop(0, '#120e22')
    grd.addColorStop(0.5, '#0c0a18')
    grd.addColorStop(1, '#120e22')
    g.fillStyle = grd
    g.fillRect(0, 0, 64, 256)
    const r = rng(12)
    for (let k = 0; k < 70; k++) {
      g.fillStyle = `rgba(200,210,255,${0.03 + r() * 0.08})`
      g.fillRect(r() * 64, r() * 256, 6 + r() * 20, 1)
    }
    const t = new THREE.CanvasTexture(c)
    t.colorSpace = THREE.SRGBColorSpace
    return t
  }, [])
  const ledge = useMemo(() => new THREE.MeshStandardMaterial({ color: '#1e2028', roughness: 0.55 }), [])
  // stretches of water between the cross streets south of the tower
  const stretches = useMemo(() => {
    const south = GRID_Z.filter((z) => z <= CANAL_TOP).sort((a, b) => b - a) // north to south
    const out: { z0: number; z1: number }[] = []
    for (let k = 0; k < south.length; k++) {
      const top = south[k] - XR_HALF
      const bottom = k + 1 < south.length ? south[k + 1] + XR_HALF : Z0
      out.push({ z0: bottom, z1: top })
    }
    return out
  }, [])
  const gapL = CANAL_X - CANAL_HALF - (GRID_X[RINGS] + XR_HALF) // ledge between canal and sidewalk
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[ORIGIN.x, -GROUND - 0.05, ORIGIN.y]}>
        <planeGeometry args={[1600, 1600]} />
        <meshBasicMaterial color="#07050c" />
      </mesh>
      {stretches.map(({ z0, z1 }, k) => {
        const len = z1 - z0
        const zc = (z0 + z1) / 2
        return (
          <group key={k}>
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[CANAL_X, -GROUND + 0.02, zc]}>
              <planeGeometry args={[CANAL_HALF * 2, len]} />
              <meshBasicMaterial map={canalTex} />
            </mesh>
            {[-1, 1].map((s) => {
              const edge = CANAL_X + s * CANAL_HALF
              return (
                <group key={s}>
                  <mesh material={ledge} position={[edge + (s * gapL) / 2, -GROUND + 0.1, zc]}>
                    <boxGeometry args={[gapL, 0.2, len]} />
                  </mesh>
                </group>
              )
            })}
          </group>
        )
      })}
    </group>
  )
}

/** Signal phase for crossroads k at time t: X-running and Z-running traffic. */
function signalPhase(k: number, t: number) {
  const p = (t + k * 3.7) % 16
  const x = p < 6 ? 'g' : p < 7.5 ? 'a' : 'r'
  const z = p >= 8 && p < 14 ? 'g' : p >= 14 && p < 15.5 ? 'a' : 'r'
  return { x, z } as const
}

const LENSES: Record<string, { color: string; on: (axisState: string) => boolean }> = {
  Loft_SignalRed: { color: '#ff2a2a', on: (s) => s === 'r' },
  Loft_SignalAmber: { color: '#ffb020', on: (s) => s === 'a' },
  Loft_SignalGreen: { color: '#2bff7a', on: (s) => s === 'g' },
  Loft_SignalWalk: { color: '#e8f6ff', on: (s) => s === 'r' }, // people cross while these cars wait
  Loft_SignalStop: { color: '#ff3a3a', on: (s) => s !== 'r' },
}

const PAINTS = ['#c23a1c', '#1d1f27', '#c9ccd4', '#d8961a', '#23408f', '#6a1a5e', '#0f6b6b']

/** Fake headlights for the instanced cars (no real lights: hundreds would be far too slow):
 * a warm pool of light on the road ahead and a faint beam above it, both additive,
 * built in the car's own space (it faces +Z) so they ride on the car's instance matrices. */
function useHeadlightParts(car: ModelPart[]): ModelPart[] {
  return useMemo(() => {
    const box = new THREE.Box3()
    car.forEach((p) => {
      p.geometry.computeBoundingBox()
      box.union(p.geometry.boundingBox!)
    })
    const front = box.max.z
    const halfW = (box.max.x - box.min.x) / 2
    const lampY = box.min.y + (box.max.y - box.min.y) * 0.32
    const LEN = 9

    // pool on the road: a trapezoid widening ahead, bright near the car and fading out
    const c = document.createElement('canvas')
    c.width = 64
    c.height = 128
    const g = c.getContext('2d')!
    const img = g.createImageData(64, 128)
    for (let y = 0; y < 128; y++)
      for (let x = 0; x < 64; x++) {
        const t = y / 127 // 0 at the car, 1 at the far end
        const u = Math.abs(x / 63 - 0.5) * 2
        const a = Math.pow(1 - t, 1.6) * Math.pow(Math.max(0, 1 - u * u), 1.5) * Math.min(1, t * 6 + 0.25)
        const i = (y * 64 + x) * 4
        img.data[i] = 255
        img.data[i + 1] = 236
        img.data[i + 2] = 200
        img.data[i + 3] = Math.round(255 * a)
      }
    g.putImageData(img, 0, 0)
    const tex = new THREE.CanvasTexture(c)
    tex.colorSpace = THREE.SRGBColorSpace
    const pool = new THREE.BufferGeometry()
    const w0 = halfW * 0.9, w1 = halfW * 2.0, y = box.min.y + 0.04
    pool.setAttribute('position', new THREE.Float32BufferAttribute([-w0, y, front, w0, y, front, w1, y, front + LEN, -w1, y, front + LEN], 3))
    pool.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, 1, 0, 1, 1, 0, 1], 2))
    pool.setIndex([0, 2, 1, 0, 3, 2])
    const poolMat = new THREE.MeshBasicMaterial({ map: tex, color: new THREE.Color(0.45, 0.42, 0.36), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false })

    // faint beam: a flattened cone from each lamp, tipped slightly down onto the road
    const beams: THREE.BufferGeometry[] = []
    for (const s of [-1, 1]) {
      const cone = new THREE.ConeGeometry(1.1, LEN * 0.75, 16, 1, true)
      cone.translate(0, -(LEN * 0.75) / 2, 0) // apex at the lamp
      cone.rotateX(-Math.PI / 2 + 0.06) // point it forward (+Z), dipping a little
      cone.scale(1, 0.45, 1)
      cone.translate(s * halfW * 0.62, lampY, front - 0.1)
      beams.push(cone)
    }
    const beamGeo = mergeGeometries(beams)
    const beamMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.0, 0.92, 0.75).multiplyScalar(0.025), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, toneMapped: false })
    return [
      { geometry: pool, material: poolMat, paint: false },
      { geometry: beamGeo, material: beamMat, paint: false },
    ]
  }, [car])
}

/** Streets, crossroads, lamps, traffic lights and traffic for the whole grid. */
function StreetGrid() {
  const { street, crossroads, signal, lamps, car } = useCityModels()
  const headlights = useHeadlightParts(car)
  const Y = -GROUND + 0.03

  const layout = useMemo(() => {
    const o = new THREE.Object3D()
    const mats = { street: [] as number[], cross: [] as number[], lamp0: [] as number[], lamp1: [] as number[], signal: [] as number[] }
    const signals: { cross: number; axis: 'x' | 'z' }[] = []
    const put = (key: keyof typeof mats, p: THREE.Vector3, rotY: number, sx = 1) => {
      o.position.set(p.x, Y, p.z)
      o.rotation.set(0, rotY, 0)
      o.scale.set(sx, 1, 1)
      o.updateMatrix()
      mats[key].push(...o.matrix.toArray())
    }
    // crossroads at every meeting point; four signals each near the office
    for (const x of GRID_X)
      for (const z of GRID_Z) {
        put('cross', new THREE.Vector3(x, 0, z), 0)
        if (!signalled(x, z)) continue
        const c = 4.4 + 0.35 + 0.55
        for (const [sx, sz, rot, axis] of [[1, 1, 0, 'x'], [-1, -1, 180, 'x'], [-1, 1, -90, 'z'], [1, -1, 90, 'z']] as const) {
          put('signal', new THREE.Vector3(x + sx * c, 0, z + sz * c), THREE.MathUtils.degToRad(rot))
          signals.push({ cross: crossId(x, z), axis })
        }
      }
    // street pieces between crossroads (20 m model, stretched to fit the gap) + lamps
    for (const l of GRID_LINES) {
      const stops = [l.from, ...l.cross.flatMap((p) => [p - XR_HALF, p + XR_HALF]), l.to]
      for (let i = 0; i < stops.length; i += 2) {
        const a0 = stops[i], a1 = stops[i + 1]
        if (a1 - a0 < 1) continue
        const n = Math.max(1, Math.round((a1 - a0) / 20))
        const len = (a1 - a0) / n
        for (let k = 0; k < n; k++) put('street', lineWorld(l, a0 + len * (k + 0.5), 0), l.axis === 'x' ? 0 : Math.PI / 2, len / 20)
        // one lamp each side per stretch, staggered; only within sight of the office
        const mid = lineWorld(l, (a0 + a1) / 2, 0)
        if (Math.hypot(mid.x - ORIGIN.x, mid.z - ORIGIN.y) > 170 || a1 - a0 < 12) continue
        for (const [a, side] of [[a0 + 6, 1], [a1 - 6, -1]] as const) {
          const rot = l.axis === 'x' ? (side > 0 ? 0 : Math.PI) : side > 0 ? Math.PI / 2 : -Math.PI / 2
          put((Math.round(a) + (side > 0 ? 1 : 0)) % 2 ? 'lamp0' : 'lamp1', lineWorld(l, a, side * 5.55), rot)
        }
      }
    }
    const pack = (a: number[]) => ({ count: a.length / 16, matrices: new Float32Array(a) })
    return {
      street: pack(mats.street), cross: pack(mats.cross), lamp0: pack(mats.lamp0), lamp1: pack(mats.lamp1),
      signal: pack(mats.signal), signals,
    }
  }, [Y])

  // signal lenses: unlit-looking instanced parts whose colour is driven per crossroads
  const lensParts = useMemo(
    () =>
      signal
        .filter((p) => LENSES[p.material.name])
        .map((p) => ({ ...p, lens: LENSES[p.material.name], material: new THREE.MeshBasicMaterial({ color: '#ffffff', toneMapped: false }) })),
    [signal],
  )
  const bodyParts = useMemo(() => signal.filter((p) => !LENSES[p.material.name]), [signal])
  const lensRefs = useRef<(THREE.InstancedMesh | null)[]>([])
  const phases = useRef<string>('')

  // traffic: two lanes on every street, the full width of the city; cars stop on
  // red at signalled crossroads and drive straight through the quiet ones
  const sim = useMemo(() => {
    const r = rng(41)
    const lanes = GRID_LINES.flatMap((l) =>
      ([1, -1] as const).map((dir) => {
        const len = l.to - l.from
        const stopsAt = l.cross.map((p) => ({
          d: (dir > 0 ? p - l.from : l.to - p) - STOP_BACK,
          cross: l.axis === 'x' ? crossId(p, l.c) : crossId(l.c, p),
          lit: l.axis === 'x' ? signalled(p, l.c) : signalled(l.c, p),
        }))
        return { l, dir, len, stopsAt }
      }),
    )
    const cars: { lane: number; d: number; v: number; vmax: number; commit: number; commitD: number }[] = []
    lanes.forEach((ln, i) => {
      const near = Math.abs(ln.l.c - (ln.l.axis === 'x' ? ORIGIN.y : ORIGIN.x)) < 110
      const n = near ? 2 : 1 // light traffic: a few cars near the office, one per lane further out
      for (let k = 0; k < n; k++) {
        let d = ((k + r() * 0.5) / n) * ln.len
        // never start inside a crossroads (or right at its line): move back to clear road
        for (const s of ln.stopsAt) if (d > s.d - CLAIM_MARGIN - 4 && d < s.d + BOX_OUT) d = s.d + BOX_OUT + 1
        cars.push({ lane: i, d: Math.min(d, ln.len - 1), v: 6, vmax: 8 + r() * 4, commit: -1, commitD: 0 })
      }
    })
    const colors = cars.map(() => new THREE.Color(PAINTS[Math.floor(r() * PAINTS.length)]))
    return { lanes, cars, colors, matrices: new Float32Array(cars.length * 16) }
  }, [])
  const o = useMemo(() => new THREE.Object3D(), [])
  const ahead = useMemo(() => new THREE.Vector3(), [])

  useFrame(({ clock }, dt) => {
    const t = clock.elapsedTime
    const step = Math.min(dt, 0.05)
    const phase = (k: number) => signalPhase(k, t)

    // lens colours, only when some phase changed
    const key = layout.signals.map((s) => phase(s.cross)[s.axis]).join('')
    if (key !== phases.current) {
      phases.current = key
      const c = new THREE.Color()
      lensParts.forEach((part, i) => {
        const m = lensRefs.current[i]
        if (!m) return
        layout.signals.forEach((sg, k) => {
          c.set(part.lens.color).multiplyScalar(part.lens.on(phase(sg.cross)[sg.axis]) ? 2.6 : 0.015)
          m.setColorAt(k, c)
        })
        if (m.instanceColor) m.instanceColor.needsUpdate = true
      })
    }

    // Right of way at every crossroads: a car claims it once it is within braking distance
    // (plus a margin) and holds the claim until it has driven out the far side. Cars on the
    // crossing street see the claim early enough to stop at their line, so they never meet.
    const busy = new Map<number, 'x' | 'z'>()
    sim.cars.forEach((c) => {
      const ln = sim.lanes[c.lane]
      if (c.commit >= 0 && c.d > c.commitD + BOX_OUT) c.commit = -1 // cleared it
      if (c.commit >= 0) busy.set(c.commit, ln.l.axis)
      for (const s of ln.stopsAt) if (c.d > s.d - 0.2 && c.d < s.d + BOX_OUT) busy.set(s.cross, ln.l.axis)
    })

    // cars: 1-D per lane, front to back
    sim.lanes.forEach((ln, li) => {
      const mine = sim.cars.filter((c) => c.lane === li).sort((a, b) => b.d - a.d)
      mine.forEach((c, i) => {
        // keep a gap to the car in front (the lane loops, so the leader follows the last car)
        const front = i > 0 ? mine[i - 1].d : mine.length > 1 ? mine[mine.length - 1].d + ln.len : Infinity
        let limit = front - c.d - CAR_GAP
        for (const s of ln.stopsAt) {
          const dist = s.d - c.d
          if (dist < -0.2 || dist > 40) continue
          if (c.commit === s.cross) continue // already claimed: drive through (it can't stop in time anyway)
          let stop = false
          if (s.lit) {
            const st = phase(s.cross)[ln.l.axis]
            stop = st === 'r' || (st === 'a' && dist > 6)
          }
          const owner = busy.get(s.cross)
          if (owner && owner !== ln.l.axis) stop = true // crossing traffic has it: wait
          if (front - (s.d + BOX_OUT) < CAR_GAP) stop = true // no room to clear it: don't block it
          if (stop) limit = Math.min(limit, dist)
          else if (dist < (c.v * c.v) / 14 + CLAIM_MARGIN) {
            c.commit = s.cross // within braking distance and free: take it
            c.commitD = s.d
            busy.set(s.cross, ln.l.axis)
          }
        }
        const target = Math.max(0, Math.min(c.vmax, Math.sqrt(Math.max(0, 2 * 7 * (limit - 0.5)))))
        c.v += THREE.MathUtils.clamp(target - c.v, -14 * step, 4 * step)
        c.d += c.v * step
        if (c.d > ln.len) {
          c.d -= ln.len // off the far edge of the city, back in at the other
          c.commit = -1
        }
      })
    })
    sim.cars.forEach((c, i) => {
      const ln = sim.lanes[c.lane]
      const along = ln.dir > 0 ? ln.l.from + c.d : ln.l.to - c.d
      const across = (ln.l.axis === 'x' ? 1 : -1) * ln.dir * LANE_OFF
      const p = lineWorld(ln.l, along, across)
      o.position.set(p.x, Y + 0.01, p.z)
      ahead.copy(lineWorld(ln.l, along + ln.dir, across)).setY(Y + 0.01)
      o.lookAt(ahead)
      // only at the city's outer edge (deep in the haze) do cars shrink away and come back
      o.scale.setScalar(Math.max(0.001, Math.min(1, c.d / 8, (ln.len - c.d) / 8)))
      o.updateMatrix()
      o.matrix.toArray(sim.matrices, i * 16)
    })
  })

  return (
    <>
      <ModelInstances parts={street} matrices={layout.street.matrices} count={layout.street.count} />
      <ModelInstances parts={crossroads} matrices={layout.cross.matrices} count={layout.cross.count} />
      <ModelInstances parts={lamps[0]} matrices={layout.lamp0.matrices} count={layout.lamp0.count} />
      <ModelInstances parts={lamps[1]} matrices={layout.lamp1.matrices} count={layout.lamp1.count} />
      <ModelInstances parts={bodyParts} matrices={layout.signal.matrices} count={layout.signal.count} />
      {lensParts.map((p, i) => (
        <instancedMesh
          key={i}
          ref={(m) => {
            lensRefs.current[i] = m
            if (m && !m.userData.filled) {
              m.instanceMatrix.array.set(layout.signal.matrices)
              m.instanceMatrix.needsUpdate = true
              m.userData.filled = true
              phases.current = '' // force a colour pass
            }
          }}
          args={[p.geometry, p.material, layout.signal.count]}
          frustumCulled={false}
        />
      ))}
      <ModelInstances parts={car} matrices={sim.matrices} count={sim.cars.length} colors={sim.colors} live />
      <ModelInstances parts={headlights} matrices={sim.matrices} count={sim.cars.length} live />
    </>
  )
}

/** Orange embers drifting up past the office. */
function Weather() {
  const embers = useMemo(() => {
    const r = rng(8)
    const n = 90
    const pos = new Float32Array(n * 3)
    const seeds = Array.from({ length: n }, () => ({ x: ORIGIN.x + (r() - 0.5) * 40, z: ORIGIN.y + (r() - 0.5) * 30, y: -10 + r() * 25, v: 0.4 + r() * 0.8, ph: r() * 6 }))
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3))
    return { g, seeds, pos }
  }, [])
  const emberMat = useMemo(() => new THREE.PointsMaterial({ color: new THREE.Color('#ff8a3a').multiplyScalar(2.5), size: 0.12, transparent: true, opacity: 0.9, depthWrite: false, toneMapped: false }), [])
  useFrame(({ clock }, dt) => {
    const step = Math.min(dt, 0.05)
    const t = clock.elapsedTime
    embers.seeds.forEach((s, i) => {
      s.y += s.v * step
      if (s.y > 18) s.y = -12
      embers.pos[i * 3] = s.x + Math.sin(t * 0.5 + s.ph) * 1.5
      embers.pos[i * 3 + 1] = s.y
      embers.pos[i * 3 + 2] = s.z + Math.cos(t * 0.4 + s.ph) * 1.5
    })
    ;(embers.g.attributes.position as THREE.BufferAttribute).needsUpdate = true
  })
  return (
    <>
      <points geometry={embers.g} material={emberMat} frustumCulled={false} />
    </>
  )
}

/** A few small drones drifting around the tower at about office height. */
function Drones() {
  const drones = useMemo(
    () => [
      { r: 22, h: 6, speed: 0.12, phase: 0, color: '#22e4ff' },
      { r: 30, h: 12, speed: -0.08, phase: 2.1, color: '#ff2bd6' },
      { r: 26, h: -4, speed: 0.1, phase: 4.0, color: '#2bff9a' },
    ],
    [],
  )
  const refs = useRef<(THREE.Group | null)[]>([])
  const body = useMemo(() => new THREE.MeshStandardMaterial({ color: '#15161b', roughness: 0.4, metalness: 0.6 }), [])
  const lights = useMemo(() => drones.map((d) => new THREE.MeshBasicMaterial({ color: new THREE.Color(d.color).multiplyScalar(3), toneMapped: false })), [drones])
  const base = useMemo(() => drones.map((d) => new THREE.Color(d.color)), [drones])
  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    drones.forEach((d, i) => {
      const g = refs.current[i]
      if (!g) return
      const a = d.phase + t * d.speed
      g.position.set(ORIGIN.x + Math.cos(a) * d.r, d.h + Math.sin(t * 0.7 + i) * 0.8, ORIGIN.y + Math.sin(a) * d.r * 0.8)
      g.rotation.y = -a + (d.speed > 0 ? 0 : Math.PI)
      g.rotation.z = 0.08 * Math.sin(t * 1.3 + i)
      lights[i].color.copy(base[i]).multiplyScalar(Math.sin(t * 6 + i) > 0 ? 3 : 0.4)
    })
  })
  return (
    <>
      {drones.map((d, i) => (
        <group key={i} ref={(g) => void (refs.current[i] = g)}>
          <mesh material={body}>
            <boxGeometry args={[0.7, 0.16, 0.7]} />
          </mesh>
          {[[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([sx, sz], k) => (
            <mesh key={k} material={body} position={[sx * 0.45, 0.08, sz * 0.45]}>
              <cylinderGeometry args={[0.2, 0.2, 0.02, 16]} />
            </mesh>
          ))}
          <mesh material={lights[i]} position={[0, -0.12, 0]}>
            <sphereGeometry args={[0.08, 10, 8]} />
          </mesh>
        </group>
      ))}
    </>
  )
}

/** Night sky, lit from below like a real city at night: brightest right at the horizon
 * where the neon lights up the haze, darkening toward the top, with a few stars.
 * The horizon colour IS the scene haze (CITY_HAZE, also used for the fog in Scene.tsx),
 * so distant streets fade straight into the glow with no seam. */
function Sky() {
  const mat = useMemo(
    () =>
      new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        fog: false,
        // THREE.Color keeps linear values, the same space the fog is applied in
        uniforms: { horizon: { value: new THREE.Color(CITY_HAZE) } },
        vertexShader: 'varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
        fragmentShader: `uniform vec3 horizon;
          varying vec3 vDir;
          void main(){
            float y = vDir.y;
            vec3 mid = horizon * 0.22;
            vec3 top = vec3(0.002, 0.002, 0.007);
            vec3 c = mix(horizon, mid, smoothstep(0.0, 0.22, y));
            c = mix(c, top, smoothstep(0.22, 0.7, y));
            gl_FragColor = vec4(y < 0.0 ? horizon : c, 1.0); // below the horizon: pure haze
          }`,
      }),
    [],
  )
  const stars = useMemo(() => {
    const r = rng(5)
    const pts: number[] = []
    for (let i = 0; i < 260; i++) {
      const a = r() * Math.PI * 2
      const y = 0.35 + r() * 0.65
      const s = Math.sqrt(1 - y * y)
      pts.push(Math.cos(a) * s * 900, y * 900, Math.sin(a) * s * 900)
    }
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3))
    return g
  }, [])
  // moon: pale disc with soft maria, and a wide faint halo, up ahead of the lobby view
  const moon = useMemo(() => {
    const c = document.createElement('canvas')
    c.width = c.height = 256
    const g = c.getContext('2d')!
    const halo = g.createRadialGradient(128, 128, 30, 128, 128, 128)
    halo.addColorStop(0, 'rgba(220,210,255,0.55)')
    halo.addColorStop(0.35, 'rgba(170,140,230,0.18)')
    halo.addColorStop(1, 'rgba(120,80,200,0)')
    g.fillStyle = halo
    g.fillRect(0, 0, 256, 256)
    const disc = g.createRadialGradient(118, 118, 4, 128, 128, 34)
    disc.addColorStop(0, '#fffaf0')
    disc.addColorStop(1, '#e8e0f5')
    g.fillStyle = disc
    g.beginPath()
    g.arc(128, 128, 32, 0, Math.PI * 2)
    g.fill()
    const r = rng(31)
    for (let k = 0; k < 9; k++) {
      // soft grey maria inside the disc
      const a = r() * Math.PI * 2, d = r() * 20
      g.fillStyle = `rgba(150,145,170,${0.18 + r() * 0.2})`
      g.beginPath()
      g.arc(128 + Math.cos(a) * d, 128 + Math.sin(a) * d, 3 + r() * 8, 0, Math.PI * 2)
      g.fill()
    }
    const t = new THREE.CanvasTexture(c)
    t.colorSpace = THREE.SRGBColorSpace
    const m = new THREE.SpriteMaterial({ map: t, fog: false, depthWrite: false, transparent: true, toneMapped: false })
    const dir = new THREE.Vector3(VIEW.x, 0.42, VIEW.y).normalize().multiplyScalar(900)
    return { m, pos: dir }
  }, [])
  return (
    <group>
      <mesh material={mat} renderOrder={-3}>
        <sphereGeometry args={[950, 32, 16]} />
      </mesh>
      <points geometry={stars} renderOrder={-2}>
        <pointsMaterial color="#e6dcff" size={1.4} sizeAttenuation={false} fog={false} transparent opacity={0.6} />
      </points>
      <sprite material={moon.m} position={moon.pos} scale={[170, 170, 1]} renderOrder={-2} />
    </group>
  )
}

export default function CityScape() {
  const buildings = useLayout()
  return (
    <group>
      <Sky />
      <Ground />
      <Suspense fallback={null}>
        <TowerBase />
        {SHOW_BUILDINGS && <StreetBuildings list={buildings} />}
        <StreetGrid />
      </Suspense>
      <Weather />
      <Drones />
    </group>
  )
}
