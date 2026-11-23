'use client'

// The whole 3D office. It lives in the root layout, so it stays mounted while
// you move between pages — only the camera moves.
//
// The office itself comes from Blender: public/models/office.glb
// (built by blender/build_office.py, editable in blender/office.blend).
//
// Conventions shared with Blender:
// - An object with custom property "link" (e.g. "/lab") is a hotspot: clicking
//   any mesh under it goes to that URL; "label" is the hover text.
// - Meshes named "ArcadeScreen" and "TVScreen" get live canvas textures here.

import { Canvas, useFrame, useThree, type ThreeEvent } from '@react-three/fiber'
import { useCursor, useGLTF } from '@react-three/drei'
import { Bloom, EffectComposer } from '@react-three/postprocessing'
import { usePathname, useRouter } from 'next/navigation'
import { Suspense, useEffect, useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import { shotFor, type Shot, type Vec3 } from './shots'
import { ArcadeGame, type ArcadeTile } from './arcadeGame'
import { arcadeBus } from './arcadeBus'
import { memoBus, useOpenMemo } from './memoBus'
import { site } from '@/content/site'
import { markReady, setExpectedBytes, trackProgress } from './loadProgress'
import Loader from './Loader'
import CityScape, { CITY_HAZE } from './CityScape'

// The city outside the windows (components/CityScape.tsx). Set to false to go back to a black void.
const SHOW_CITY = true

const MODEL_URL = '/models/office.glb?v=31' // bump after re-exporting so browsers fetch the new file
// office.glb size in bytes: lets the loading screen show a % when the server omits it.
// Update together with MODEL_URL after re-exporting.
const MODEL_BYTES = 3_890_500
setExpectedBytes(MODEL_BYTES)
const DRACO_URL = '/draco/' // decoder copied from three/examples/jsm/libs/draco/gltf

export default function Scene() {
  return (
    <div className="scene">
      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{ fov: 50, position: [1, 3.2, 10], near: 0.05, far: 1200 }}
      >
        <color attach="background" args={[SHOW_CITY ? CITY_HAZE : '#000000']} />
        {/* purple-magenta city haze; it only starts past the office so the room stays crisp */}
        <fog attach="fog" args={SHOW_CITY ? [CITY_HAZE, 40, 470] : ['#000000', 24, 48]} />
        {SHOW_CITY && <CityScape />}
        <Lights />
        <Suspense fallback={null}>
          <Office />
          <MarkReadyAfterFirstFrames />
        </Suspense>
        <CameraRig />
        <PauseWhenScrolledAway />
        <Effects />
      </Canvas>
      <Loader />
    </div>
  )
}

/** Mounts once the model has loaded; tells the loading screen after a couple of
 *  rendered frames (so shaders are compiled and the office is really visible). */
function MarkReadyAfterFirstFrames() {
  const frames = useRef(0)
  useFrame(() => {
    if (++frames.current === 3) markReady()
  })
  return null
}

/* ---------------- the Blender model ---------------- */

type Hotspot = { link: string; label: string; root: THREE.Object3D }

/**
 * memo id (content/site.ts → memos) → the object in office.glb you click to open it.
 * `view` (optional) is a fixed camera in that object's own coordinates (so it follows the
 * object if it's moved in Blender); without it the camera frames the object from the front right.
 */
const MEMO_SPOTS: Record<string, { object: string; view?: { eye: Vec3; look: Vec3 } }> = {
  nap: { object: 'LoungeSpot' }, // the lounge table + Philips napping at it
  // sim rig: sitting in the bucket seat, looking at the three screens over the wheel
  simrig: { object: 'SimRigSpot', view: { eye: [0, 1.05, 0.5], look: [0, 0.9, -1.2] } },
  // pinball: standing at the front like you're playing, looking down the glass at the backbox
  pinball: { object: 'PinballSpot', view: { eye: [0, 1.55, 1.1], look: [0, 0.98, -0.45] } },
  // chill area: sunk into the middle lounger, looking up at the big TV
  chill: { object: 'ChillSpot', view: { eye: [0, 1.05, 1.05], look: [0, 0.82, -1.4] } },
}

/** Walk up from the clicked mesh to the nearest parent that has a "link". */
function findHotspot(obj: THREE.Object3D | null): Hotspot | null {
  while (obj) {
    if (typeof obj.userData.link === 'string') {
      return { link: obj.userData.link, label: obj.userData.label ?? obj.name, root: obj }
    }
    obj = obj.parent
  }
  return null
}

function Office() {
  const { scene } = useGLTF(MODEL_URL, DRACO_URL, undefined, trackProgress)
  const router = useRouter()
  const pathname = usePathname()
  const [hovered, setHovered] = useState<Hotspot | null>(null)
  // while a memo is open, its spot counts as "where you are" (no bubble / glass on it)
  const memoOpen = useOpenMemo()
  const here = memoOpen ? `#${memoOpen}` : pathname
  const isHere = hovered?.link === here
  // opening a memo (or changing page) drops any hover, so nothing stays lit while zoomed in
  useEffect(() => setHovered(null), [here])

  const arcade = useArcade(pathname === '/lab')
  const cast = useCharacterIdle(scene)
  // People floor: click a person for a small note next to them (all of them are Philips)
  const [person, setPerson] = useState<PersonId | null>(null)
  const [overPerson, setOverPerson] = useState(false)
  useEffect(() => setPerson(null), [pathname])
  useCursor((!!hovered && !isHere) || overPerson)
  // extra clickable spots that open a memo instead of flying to a page ("#id" links)
  useMemo(() => {
    for (const [id, { object }] of Object.entries(MEMO_SPOTS)) {
      const spot = scene.getObjectByName(object)
      if (!spot) continue
      spot.userData.link = `#${id}`
      spot.userData.label = site.memos[id]?.name ?? id
    }
  }, [scene])
  const hotspots = useHotspots(scene)
  // "/lab" flies the camera there; "#nap" opens that memo
  const go = (link: string) => (link.startsWith('#') ? memoBus.open(link.slice(1)) : router.push(link))
  useHoverGlow(hotspots, hovered && !isHere ? hovered.root : null)
  useChromaWave(scene)
  useFanSpin(scene)

  // floating "z z Z" above the sleeping coworker
  const [zzzPos, setZzzPos] = useState<[number, number, number] | null>(null)
  useEffect(() => {
    const head = cast.sleeper?.head
    if (!head) return
    scene.updateMatrixWorld(true)
    const p = head.getWorldPosition(new THREE.Vector3())
    setZzzPos([p.x, p.y + 0.4, p.z])
  }, [cast, scene])
  const tvTexture = useMemo(() => servicesTexture(), [])

  // one-time setup: shadows + live screen textures
  useEffect(() => {
    scene.traverse((o) => {
      const mesh = o as THREE.Mesh
      if (!mesh.isMesh) return
      const glowing = (mesh.material as THREE.MeshStandardMaterial).emissiveIntensity > 0 &&
        !(mesh.material as THREE.MeshStandardMaterial).emissive.equals(new THREE.Color(0, 0, 0))
      mesh.castShadow = !glowing
      mesh.receiveShadow = true
      // the big window glows less on the site than in Blender, so the bloom
      // doesn't wash out the Services board and its note cards
      const std = mesh.material as THREE.MeshStandardMaterial
      if (std.name === 'Loft_WindowGlow' && !std.userData.dimmed) {
        std.emissiveIntensity *= 0.3
        std.userData.dimmed = true
      }
    })
    const screens: [string, THREE.Texture][] = [
      ['ArcadeScreen', arcade.texture],
      ['TVScreen', tvTexture],
    ]
    for (const [name, map] of screens) {
      const mesh = scene.getObjectByName(name) as THREE.Mesh | undefined
      if (mesh) mesh.material = new THREE.MeshBasicMaterial({ map, toneMapped: false })
      else console.warn(`office.glb has no object named "${name}"`)
    }
  }, [scene, arcade.texture, tvTexture])

  const onClick = (e: ThreeEvent<MouseEvent>) => {
    // clicking the arcade screen while zoomed in picks a tile. The screen sits just
    // behind the cabinet's front shell, so look for it among all the hits.
    const screenHit = pathname === '/lab' ? e.intersections.find((i) => i.object.name === 'ArcadeScreen') : undefined
    if (screenHit) {
      e.stopPropagation()
      // glTF UVs with flipY = false: u = canvas x, v = canvas y (top = 0)
      if (screenHit.uv) arcade.game.click(screenHit.uv.x * ARCADE_W, screenHit.uv.y * ARCADE_H)
      return
    }
    if (pathname === '/people') {
      const who = findPerson(e.object)
      e.stopPropagation()
      setPerson(who && who !== person ? who : null) // click again (or elsewhere) to close
      if (who) return
    }
    const hit = findHotspot(e.object)
    if (!hit) return
    e.stopPropagation()
    if (hit.link !== pathname) go(hit.link)
  }

  return (
    <>
      <primitive
        object={scene}
        onClick={onClick}
        onPointerMove={(e: ThreeEvent<PointerEvent>) => {
          e.stopPropagation()
          const hit = findHotspot(e.object)
          if (hit?.root !== hovered?.root) setHovered(hit)
          const p = pathname === '/people' && !!findPerson(e.object)
          if (p !== overPerson) setOverPerson(p)
        }}
        onPointerOut={() => setHovered(null)}
      />
      {zzzPos && <Zzz position={zzzPos} />}
      <PersonNote
        person={person}
        head={person === 'hero' ? cast.hero?.head : person === 'typer' ? cast.typer?.head : undefined}
        onClose={() => setPerson(null)}
      />
      <SectionGlass
        hotspots={hotspots}
        current={here}
        hovered={hovered && !isHere ? hovered.link : null}
        onHover={(h) => setHovered(h)}
        onSelect={go}
      />
      <SectionBubbles
        hotspots={hotspots}
        current={here}
        hovered={hovered?.link ?? null}
        onHover={(h) => setHovered(h)}
        onSelect={go}
      />
    </>
  )
}

useGLTF.preload(MODEL_URL, DRACO_URL, undefined, trackProgress)

/* ---------------- clickable sections: hover glow + floating markers ---------------- */

type HotspotInfo = {
  link: string
  label: string
  root: THREE.Object3D
  top: THREE.Vector3 // a point just above the section, for its marker
  box: THREE.Box3 // the section's bounds: its glass hover box and click area
  mats: { m: THREE.MeshStandardMaterial; base: THREE.Color }[]
  glow: number // 0..1, eased toward 1 while hovered
}

const GLOW = new THREE.Color('#ffffff').multiplyScalar(0.02) // soft, see-through white sheen

/**
 * Every object with a "link" (set in Blender) is a section. Each section gets
 * its own copies of its materials so it can glow without lighting up the rest
 * of the office (materials are shared between objects in the glb).
 */
function useHotspots(scene: THREE.Object3D) {
  return useMemo(() => {
    scene.updateMatrixWorld(true)
    const list: HotspotInfo[] = []
    scene.traverse((o) => {
      if (typeof o.userData.link !== 'string') return
      const mats: HotspotInfo['mats'] = []
      const cloned = new Map<THREE.Material, THREE.Material>()
      const seen = new Set<THREE.Material>()
      o.traverse((c) => {
        const mesh = c as THREE.Mesh
        if (!mesh.isMesh || mesh.userData.glassShell) return // skip the hover-glass shells
        const swap = (m: THREE.Material) => {
          // Idempotent: React may run this twice (dev Strict Mode, hot reload); a material
          // that is already this section's copy is reused, so glow always hits what's drawn.
          let copy = m.userData.sectionCopy ? m : cloned.get(m)
          if (!copy) {
            copy = m.clone()
            const std = m as THREE.MeshStandardMaterial
            copy.userData.sectionCopy = true
            // only tint ordinary surfaces, not things that already glow (screens, RGB)
            copy.userData.glowable = !!std.isMeshStandardMaterial && !std.emissiveMap && std.emissive.getHex() === 0
            cloned.set(m, copy)
          }
          if (!seen.has(copy)) {
            seen.add(copy)
            if (copy.userData.glowable) {
              mats.push({ m: copy as THREE.MeshStandardMaterial, base: new THREE.Color(0, 0, 0) })
            }
          }
          return copy
        }
        mesh.material = Array.isArray(mesh.material) ? mesh.material.map(swap) : swap(mesh.material)
      })
      const box = new THREE.Box3().setFromObject(o)
      const top = box.getCenter(new THREE.Vector3())
      top.y = box.max.y + 0.35
      list.push({ link: o.userData.link, label: o.userData.label ?? o.name, root: o, top, box, mats, glow: 0 })
    })
    return list
  }, [scene])
}

function useHoverGlow(hotspots: HotspotInfo[], hoveredRoot: THREE.Object3D | null) {
  const tmp = useMemo(() => new THREE.Color(), [])
  useFrame((_, dt) => {
    const k = 1 - Math.exp(-dt * 10)
    for (const h of hotspots) {
      const target = h.root === hoveredRoot ? 1 : 0
      if (Math.abs(h.glow - target) < 0.001 && target === 0 && h.glow === 0) continue
      h.glow += (target - h.glow) * k
      if (h.glow < 0.002 && target === 0) h.glow = 0
      tmp.copy(GLOW).multiplyScalar(h.glow)
      for (const { m, base } of h.mats) m.emissive.copy(base).add(tmp)
    }
  })
}

/** Scroll the shared rainbow texture of the Razer-style gear: a Chroma "wave". */
function useChromaWave(scene: THREE.Object3D) {
  const textures = useMemo(() => {
    const set = new Set<THREE.Texture>()
    scene.traverse((o) => {
      const mesh = o as THREE.Mesh
      if (!mesh.isMesh) return
      const list = Array.isArray(mesh.material) ? mesh.material : [mesh.material]
      for (const m of list) {
        if (!m.name.startsWith('Razer_ChromaRGB')) continue
        const std = m as THREE.MeshStandardMaterial
        for (const t of [std.map, std.emissiveMap]) {
          if (!t) continue
          t.wrapS = THREE.RepeatWrapping
          t.needsUpdate = true
          set.add(t)
        }
      }
    })
    return [...set]
  }, [scene])
  useFrame((_, dt) => {
    for (const t of textures) t.offset.x = (t.offset.x - dt * 0.18) % 1
  })
}

type PersonId = 'hero' | 'typer'

/** Which person (on the People floor) a clicked mesh belongs to, if any. */
function findPerson(obj: THREE.Object3D | null): PersonId | null {
  while (obj) {
    if (obj.name === 'Character') return 'hero'
    if (obj.name === 'Typer') return 'typer'
    obj = obj.parent
  }
  return null
}

/**
 * A small sticky note pinned beside a person's head (plain DOM, positioned every frame by
 * projecting the head, like the section bubbles). Text comes from site.people. Esc, the x,
 * or clicking anywhere else closes it.
 */
function PersonNote({ person, head, onClose }: { person: PersonId | null; head?: THREE.Object3D; onClose: () => void }) {
  const { gl, camera, size } = useThree()
  const close = useRef(onClose)
  close.current = onClose
  const el = useMemo(() => {
    const d = document.createElement('aside')
    d.className = 'person-note'
    d.setAttribute('role', 'dialog')
    return d
  }, [])
  useEffect(() => {
    const host = gl.domElement.parentElement
    host?.appendChild(el)
    return () => el.remove()
  }, [gl, el])

  useEffect(() => {
    const info = person ? site.people[person] : null
    el.classList.toggle('is-open', !!info)
    if (!info) return
    el.innerHTML = `<span class="person-note-tape" aria-hidden="true"></span>
      <button type="button" class="person-note-close" aria-label="Close note">×</button>
      <b class="person-note-name"></b><span class="person-note-role"></span>
      <span class="person-note-status"><i></i><em></em></span><p class="person-note-text"></p>`
    el.querySelector('.person-note-name')!.textContent = info.name
    el.querySelector('.person-note-role')!.textContent = info.role
    el.querySelector('.person-note-status em')!.textContent = info.status
    el.querySelector('.person-note-text')!.textContent = info.note
    el.querySelector('button')!.addEventListener('click', () => close.current())
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return
      e.preventDefault()
      e.stopImmediatePropagation() // close the note, don't fly back to the lobby
      close.current()
    }
    window.addEventListener('keydown', onKey, true)
    return () => window.removeEventListener('keydown', onKey, true)
  }, [person, el])

  const v = useMemo(() => new THREE.Vector3(), [])
  useFrame(() => {
    if (!person || !head) return
    head.getWorldPosition(v)
    v.y += 0.12
    v.project(camera)
    // to the right of the head, kept on screen
    const x = Math.min(((v.x + 1) / 2) * size.width + 36, size.width - 280)
    const y = Math.min(Math.max(((1 - v.y) / 2) * size.height - 40, 60), size.height - 220)
    el.style.transform = `translate(${x}px, ${y}px)`
  })
  return null
}

/**
 * Hover glass that hugs the real objects: every mesh in a section gets a see-through
 * "shell" copy of itself (same geometry, pushed out a hair along its normals) with a
 * frosted fresnel rim and a light sheen that sweeps across when the hover starts. The
 * shells are children of the meshes, so they follow anything that moves (the people).
 *
 * Clicks and hover use a separate invisible box around each section, so the whole
 * section area (gaps included) is clickable. The section you're in has no box, so its
 * own objects (e.g. the arcade screen) get the clicks there.
 */
const glassVert = /* glsl */ `
  uniform float uInflate;
  varying vec3 vNormal;
  varying vec3 vView;
  varying vec3 vWorld;
  void main() {
    vec4 world = modelMatrix * vec4(position + normal * uInflate, 1.0);
    vWorld = world.xyz;
    vNormal = normalize(mat3(modelMatrix) * normal);
    vView = normalize(cameraPosition - world.xyz);
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`
const glassFrag = /* glsl */ `
  uniform float uGlow;
  uniform float uTime;
  uniform float uSweepStart;
  varying vec3 vNormal;
  varying vec3 vView;
  varying vec3 vWorld;
  void main() {
    float fres = pow(1.0 - abs(dot(normalize(vNormal), normalize(vView))), 2.0);
    // one diagonal band of light that sweeps across each time the hover starts
    float d = (vWorld.x + vWorld.y * 0.8) * 0.45 - (uTime - uSweepStart) * 2.2 + 2.0;
    float sheen = smoothstep(0.35, 0.0, abs(d)) * 0.55;
    vec3 tint = vec3(0.82, 0.92, 1.0);
    float a = uGlow * (0.012 + 0.2 * fres + sheen * 0.35);
    gl_FragColor = vec4(tint * (0.55 + 0.45 * fres + sheen), a);
  }
`
const noRaycast = () => {}

function SectionGlass({
  hotspots,
  current,
  hovered,
  onHover,
  onSelect,
}: {
  hotspots: HotspotInfo[]
  current: string
  hovered: string | null
  onHover: (h: Hotspot | null) => void
  onSelect: (link: string) => void
}) {
  const sections = useMemo(
    () =>
      hotspots.map((h) => {
        const material = new THREE.ShaderMaterial({
          vertexShader: glassVert,
          fragmentShader: glassFrag,
          uniforms: {
            uGlow: { value: 0 },
            uTime: { value: 0 },
            uSweepStart: { value: -10 },
            uInflate: { value: 0 },
          },
          transparent: true,
          depthWrite: false,
          blending: THREE.AdditiveBlending,
        })
        // one shell per mesh in the section, parented to that mesh
        const shells: THREE.Mesh[] = []
        const meshes: THREE.Mesh[] = []
        h.root.traverse((o) => {
          const m = o as THREE.Mesh
          if (m.isMesh && m.userData.glassShell !== true && m.geometry.attributes.normal) meshes.push(m)
        })
        for (const m of meshes) {
          const shell = new THREE.Mesh(m.geometry, material)
          shell.userData.glassShell = true
          shell.raycast = noRaycast // never steals clicks (e.g. from the arcade screen)
          shell.renderOrder = 10
          shell.visible = false
          shell.frustumCulled = m.frustumCulled
          m.add(shell)
          shells.push(shell)
        }
        // the click / hover area: an invisible box around the whole section
        const hit = new THREE.BoxGeometry(...h.box.getSize(new THREE.Vector3()).addScalar(0.16).toArray())
        const center = h.box.getCenter(new THREE.Vector3())
        return { h, material, shells, hit, center, glow: 0, wasOn: false, shown: false }
      }),
    [hotspots],
  )
  useEffect(
    () => () =>
      sections.forEach((s) => {
        s.shells.forEach((sh) => sh.removeFromParent())
        s.material.dispose()
        s.hit.dispose()
      }),
    [sections],
  )

  useFrame(({ clock }, dt) => {
    const t = clock.elapsedTime
    const k = 1 - Math.exp(-dt * 9)
    for (const s of sections) {
      const on = s.h.link === hovered
      if (on && !s.wasOn) s.material.uniforms.uSweepStart.value = t // replay the sheen
      s.wasOn = on
      s.glow += ((on ? 1 : 0) - s.glow) * k
      if (!on && s.glow < 0.003) s.glow = 0
      const u = s.material.uniforms
      u.uGlow.value = s.glow
      u.uTime.value = t
      u.uInflate.value = 0.004 + 0.008 * s.glow // swells out slightly as it fades in
      const show = s.glow > 0
      if (show !== s.shown) {
        s.shown = show
        for (const sh of s.shells) sh.visible = show // idle sections cost nothing to draw
      }
    }
  })

  return (
    <>
      {sections.map((s) =>
        s.h.link === current ? null : (
          <mesh
            key={s.h.link}
            geometry={s.hit}
            position={s.center}
            visible={false} // never drawn; raycasts ignore visibility
            onPointerMove={(e) => {
              e.stopPropagation()
              if (hovered !== s.h.link) onHover({ link: s.h.link, label: s.h.label, root: s.h.root })
            }}
            onPointerOut={() => onHover(null)}
            onClick={(e) => {
              e.stopPropagation()
              onSelect(s.h.link)
            }}
          />
        ),
      )}
    </>
  )
}

/**
 * A floating speech bubble with the section's name above every section you can go to
 * (not the one you're in). Plain DOM elements next to the canvas, positioned every frame
 * by projecting a 3D point (drei's <Html> makes a React root per label, which crashes in
 * React 19 dev mode). Hovering the section in 3D (or the bubble) highlights it.
 */
function SectionBubbles({
  hotspots,
  current,
  hovered,
  onHover,
  onSelect,
}: {
  hotspots: HotspotInfo[]
  current: string
  hovered: string | null
  onHover: (h: Hotspot | null) => void
  onSelect: (link: string) => void
}) {
  const { gl, camera, size } = useThree()
  const select = useRef(onSelect)
  select.current = onSelect
  const hover = useRef(onHover)
  hover.current = onHover

  const bubbles = useMemo(
    () =>
      hotspots.map((h, i) => {
        const a = document.createElement('a')
        a.className = 'section-bubble'
        a.href = h.link
        a.style.setProperty('--i', String(i)) // staggers the pop-in and the bob
        if (h.link.startsWith('#')) {
          // extra bits (memos etc.): just a small round "!" sign, no name
          a.classList.add('is-extra')
          a.setAttribute('aria-label', `More about ${h.label}`)
          a.innerHTML = '<span class="section-bubble-inner"><i class="section-bubble-info">!</i></span>'
        } else {
          a.innerHTML = '<span class="section-bubble-inner"><i class="section-bubble-dot"></i><b></b><em>→</em></span>'
          a.querySelector('b')!.textContent = h.label
        }
        a.addEventListener('click', (e) => {
          e.preventDefault()
          select.current(h.link)
        })
        // hovering the bubble lights up its section too
        a.addEventListener('pointerenter', () => hover.current({ link: h.link, label: h.label, root: h.root }))
        a.addEventListener('pointerleave', () => hover.current(null))
        return a
      }),
    [hotspots],
  )

  useEffect(() => {
    const host = gl.domElement.parentElement
    bubbles.forEach((b) => host?.appendChild(b))
    return () => bubbles.forEach((b) => b.remove())
  }, [gl, bubbles])

  // show / highlight: the section you're in has no bubble
  useEffect(() => {
    hotspots.forEach((h, i) => {
      const b = bubbles[i]
      b.classList.toggle('is-hidden', h.link === current)
      b.classList.toggle('is-active', h.link === hovered)
      b.tabIndex = h.link === current ? -1 : 0
    })
  }, [hotspots, bubbles, current, hovered])

  const v = useMemo(() => new THREE.Vector3(), [])
  useFrame(() => {
    hotspots.forEach((h, i) => {
      v.copy(h.top).project(camera)
      const b = bubbles[i]
      const x = ((v.x + 1) / 2) * size.width
      const sy = ((1 - v.y) / 2) * size.height
      // hide it when its section is off screen (e.g. zoomed into another section)
      const off = v.z > 1 || x < 30 || x > size.width - 30 || sy < -60 || sy > size.height - 40
      // keep the bubble (about 40px tall above its point) clear of the 36px top bar
      b.style.transform = `translate(${x}px, ${Math.max(sy, 90)}px)`
      b.classList.toggle('is-behind', off)
    })
  })

  return null
}

/* ---------------- character idle animation ---------------- */
// No skeleton needed: the character is made of separate parts grouped under
// pivots in Blender (UpperBody at the pelvis, HeadPivot at the neck), so we
// just rotate / scale those every frame.

type Rig = {
  upper?: THREE.Object3D
  head?: THREE.Object3D
  upperX: number
  headRot: THREE.Euler
  lids: { o: THREE.Object3D; y: number; sy: number }[]
  hands: { o: THREE.Object3D; y: number }[]
}

/** Find a character's animatable parts by name prefix (Blender adds .001 suffixes to copies). */
function findRig(root: THREE.Object3D | undefined): Rig | null {
  if (!root) return null
  let upper: THREE.Object3D | undefined
  let head: THREE.Object3D | undefined
  const lids: Rig['lids'] = []
  const hands: Rig['hands'] = []
  root.traverse((o) => {
    if (!upper && o.name.startsWith('UpperBody')) upper = o
    if (!head && o.name.startsWith('HeadPivot')) head = o
    if (o.name.startsWith('Eyelid')) lids.push({ o, y: o.position.y, sy: o.scale.y })
    if (o.name.startsWith('Hand')) hands.push({ o, y: o.position.y })
  })
  return {
    upper,
    head,
    upperX: upper?.rotation.x ?? 0,
    headRot: head?.rotation.clone() ?? new THREE.Euler(),
    lids,
    hands,
  }
}

function breathe(rig: Rig, t: number, period: number, depth: number) {
  const b = (Math.sin((t * Math.PI * 2) / period) + 1) / 2
  if (!rig.upper) return b
  rig.upper.scale.set(1 + 0.6 * depth * b, 1 + depth * b, 1 + 0.6 * depth * b)
  return b
}

function blink(rig: Rig, t: number, every: number) {
  const phase = t % every
  const k = phase < 0.18 ? Math.sin((phase / 0.18) * Math.PI) : 0
  for (const l of rig.lids) {
    l.o.position.y = l.y - 0.009 * k
    l.o.scale.y = l.sy * (1 + 0.35 * k)
  }
}

function useCharacterIdle(scene: THREE.Object3D) {
  const cast = useMemo(() => {
    const seat = scene.getObjectByName('HeroSeat')
    return {
      seat,
      seatYaw: seat?.rotation.y ?? 0,
      hero: findRig(scene.getObjectByName('Character')),
      typer: findRig(scene.getObjectByName('Typer')),
      sleeper: findRig(scene.getObjectByName('Sleeper')),
    }
  }, [scene])

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    const { seat, seatYaw, hero, typer, sleeper } = cast

    // HERO: sleepy, swivelling on his chair, now and then dozing off
    if (hero) {
      const b = breathe(hero, t, 4, 0.015)
      if (hero.upper) hero.upper.rotation.x = hero.upperX + 0.02 - 0.02 * b
      if (hero.head) {
        const doze = Math.pow(Math.max(0, Math.sin(t * 0.55)), 12)
        hero.head.rotation.x = hero.headRot.x + 0.05 + 0.03 * Math.sin(t * 0.4) + 0.22 * doze
        hero.head.rotation.z = hero.headRot.z + 0.06 * Math.sin(t * 0.45)
        hero.head.rotation.y = hero.headRot.y + 0.08 * Math.sin(t * 0.23)
      }
      blink(hero, t, 3.7)
      if (seat) seat.rotation.y = seatYaw + 0.1 * Math.sin(t * 0.25)
    }

    // TYPER: fingers tapping, head bobbing slightly while reading the screen
    if (typer) {
      breathe(typer, t + 1.3, 3.5, 0.012)
      typer.hands.forEach((h, i) => {
        // bursts of typing with short pauses
        const burst = Math.sin(t * 0.9 + i) > -0.3 ? 1 : 0
        h.o.position.y = h.y + 0.006 * burst * Math.abs(Math.sin(t * 17 + i * 1.7))
      })
      if (typer.head) {
        typer.head.rotation.x = typer.headRot.x + 0.02 * Math.sin(t * 1.3)
        typer.head.rotation.y = typer.headRot.y + 0.05 * Math.sin(t * 0.35)
      }
      blink(typer, t + 0.8, 4.3)
    }

    // SLEEPER: slow, deep breaths, head rising and settling on his arms
    if (sleeper) {
      const b = breathe(sleeper, t, 5.5, 0.025)
      if (sleeper.upper) sleeper.upper.rotation.x = sleeper.upperX - 0.02 * b
      if (sleeper.head) sleeper.head.rotation.x = sleeper.headRot.x + 0.015 * b
    }
  })

  return cast
}

/** Three "z" sprites drifting up and fading out, on a loop. */
function Zzz({ position }: { position: [number, number, number] }) {
  const texture = useMemo(() => {
    const c = document.createElement('canvas')
    c.width = c.height = 64
    const ctx = c.getContext('2d')!
    ctx.font = 'bold 52px ui-monospace, Consolas, monospace'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillStyle = '#ffffff'
    ctx.fillText('z', 32, 34)
    const tex = new THREE.CanvasTexture(c)
    tex.colorSpace = THREE.SRGBColorSpace
    return tex
  }, [])
  const sprites = useRef<(THREE.Sprite | null)[]>([])

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    sprites.current.forEach((s, i) => {
      if (!s) return
      const p = (t / 3 + i / 3) % 1 // 0 → 1 over 3 s, staggered
      s.position.set(p * 0.3, p * 0.55, 0)
      const size = 0.1 + 0.14 * p
      s.scale.set(size, size, size)
      ;(s.material as THREE.SpriteMaterial).opacity = Math.sin(p * Math.PI) * 0.9
    })
  })

  return (
    <group position={position}>
      {[0, 1, 2].map((i) => (
        <sprite key={i} ref={(el) => void (sprites.current[i] = el)}>
          <spriteMaterial map={texture} color="#cfd8ff" transparent depthWrite={false} toneMapped={false} />
        </sprite>
      ))}
    </group>
  )
}

/* ---------------- arcade game ---------------- */

const ARCADE_W = 512
const ARCADE_H = 400
const ARCADE_TILES: ArcadeTile[] = site.work.map((w) => ({
  title: w.title,
  color: w.arcade.color,
  icon: w.arcade.icon as ArcadeTile['icon'],
}))

function useArcade(active: boolean) {
  const { texture, game } = useMemo(() => {
    const canvas = document.createElement('canvas')
    canvas.width = ARCADE_W
    canvas.height = ARCADE_H
    const texture = new THREE.CanvasTexture(canvas)
    texture.colorSpace = THREE.SRGBColorSpace
    texture.flipY = false // glTF UVs are flipped compared to three.js defaults
    const game = new ArcadeGame(canvas, ARCADE_TILES)
    game.onSelect = (index) => arcadeBus.emit({ type: 'select', index })
    return { texture, game }
  }, [])

  // only send keys to the cabinet while the camera is zoomed in on it
  useEffect(() => {
    game.setActive(active)
    if (!active) return
    // capture phase, so a used Esc can stop the "Esc = back to lobby" handler
    const down = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLElement && e.target.closest('input, textarea, select')) return
      if (game.key(e.code, true)) {
        e.preventDefault()
        if (e.code === 'Escape') e.stopImmediatePropagation()
      }
    }
    const up = (e: KeyboardEvent) => game.key(e.code, false)
    window.addEventListener('keydown', down, true)
    window.addEventListener('keyup', up, true)
    const off = arcadeBus.on((ev) => {
      if (ev.type === 'key') game.key(ev.code, ev.down)
      if (ev.type === 'close') game.backToSelect()
    })
    return () => {
      window.removeEventListener('keydown', down, true)
      window.removeEventListener('keyup', up, true)
      off()
    }
  }, [active, game])

  useFrame((_, dt) => {
    game.update(dt)
    game.draw()
    texture.needsUpdate = true
  })

  return { texture, game }
}

/* ---------------- camera ---------------- */

/**
 * On the homepage the office is the hero and the content scrolls up over it.
 * Once the hero is fully covered there's nothing to see, so stop rendering.
 */
function PauseWhenScrolledAway() {
  const setFrameloop = useThree((s) => s.setFrameloop)
  useEffect(() => {
    let paused = false
    const check = () => {
      const covered = window.scrollY >= window.innerHeight
      if (covered !== paused) {
        paused = covered
        setFrameloop(covered ? 'never' : 'always')
      }
    }
    check()
    window.addEventListener('scroll', check, { passive: true })
    window.addEventListener('resize', check)
    return () => {
      window.removeEventListener('scroll', check)
      window.removeEventListener('resize', check)
      setFrameloop('always')
    }
  }, [setFrameloop])
  return null
}

function CameraRig() {
  const pathname = usePathname()
  const memo = useOpenMemo()
  const scene = useThree((st) => st.scene)
  const size = useThree((st) => st.size)
  // A memo open? Fly in on its spot, framed on the left (the memo card sits on the right);
  // in portrait the spot sits in the top half and the card slides up from the bottom.
  const memoShot = useMemo((): Shot | null => {
    const cfg = memo ? MEMO_SPOTS[memo] : undefined
    const spot = cfg ? scene.getObjectByName(cfg.object) : null
    if (!spot || !cfg) return null
    if (cfg.view) {
      // a fixed point of view (e.g. sitting in the sim rig's seat)
      spot.updateWorldMatrix(true, false)
      const eye = spot.localToWorld(new THREE.Vector3(...cfg.view.eye))
      const look = spot.localToWorld(new THREE.Vector3(...cfg.view.look))
      return { pos: eye.toArray() as Vec3, target: look.toArray() as Vec3, parallax: 0.04 }
    }
    const c = new THREE.Box3().setFromObject(spot).getCenter(new THREE.Vector3())
    const back = new THREE.Vector3(0.62, 0.5, 0.6).normalize() // from the front right, a bit above
    const forward = back.clone().negate()
    const right = new THREE.Vector3().crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize()
    const portrait = size.width < size.height
    const target = portrait ? c.clone().add(new THREE.Vector3(0, -1.9, 0)) : c.clone().addScaledVector(right, 0.95)
    const pos = target.clone().addScaledVector(back, portrait ? 4.6 : 3.4)
    return { pos: pos.toArray() as Vec3, target: target.toArray() as Vec3, parallax: 0.12 }
  }, [memo, scene, size.width, size.height])
  const shot = memoShot ?? shotFor(pathname)
  const lookAt = useRef(new THREE.Vector3(0, 1.4, -2))
  const shift = useRef(0) // horizontal view offset in px (see the end of useFrame)
  const goalPos = useMemo(() => new THREE.Vector3(), [])
  const goalTarget = useMemo(() => new THREE.Vector3(), [])

  // Keep the same horizontal view on any screen shape, so phones in portrait
  // see the whole shot instead of a cropped middle strip.
  const camera = useThree((st) => st.camera)
  useEffect(() => {
    const cam = camera as THREE.PerspectiveCamera
    const aspect = size.width / size.height
    const baseH = 2 * Math.atan(Math.tan(THREE.MathUtils.degToRad(25)) * 1.5) // 50° vfov at 3:2
    const vfov = 2 * Math.atan(Math.tan(baseH / 2) / aspect)
    cam.fov = Math.min(100, Math.max(50, THREE.MathUtils.radToDeg(vfov)))
    cam.updateProjectionMatrix()
  }, [camera, size])

  useFrame((state, dt) => {
    // smooth, frame-rate independent easing toward the current page's shot
    const k = 1 - Math.exp(-dt * 3)
    const p = shot.parallax
    goalPos.set(
      shot.pos[0] + state.pointer.x * p,
      shot.pos[1] + state.pointer.y * p * 0.5,
      shot.pos[2],
    )
    goalTarget.set(...shot.target)
    state.camera.position.lerp(goalPos, k)
    lookAt.current.lerp(goalTarget, k)
    state.camera.lookAt(lookAt.current)

    // first-person memo views (sim rig seat, pinball): slide the picture left so the
    // machine stays clear of the memo card on the right, without turning your head
    const { width, height } = state.size
    const wantShift = memo && MEMO_SPOTS[memo]?.view && width > height ? width * 0.2 : 0
    shift.current += (wantShift - shift.current) * k
    const cam = state.camera as THREE.PerspectiveCamera
    if (Math.abs(shift.current) > 0.5) cam.setViewOffset(width, height, shift.current, 0, width, height)
    else if (cam.view?.enabled) cam.clearViewOffset()
  })
  return null
}

/* ---------------- lighting ---------------- */
// Lights stay in code so they're easy to tweak. The next step for a
// Basement-style look is baking lighting into textures in Blender.

function Lights() {
  // Cyberpunk loft: near-black ambient, one colour per zone (like the reference).
  // Only the window light casts shadows, to keep it fast.
  return (
    <>
      <hemisphereLight args={['#4a5a78', '#120a0e', 0.35]} />
      {/* upper floor */}
      <WindowLight />
      <pointLight position={[4.0, 4.5, -3.6]} intensity={14} color="#ffb020" />
      <pointLight position={[-4.6, 5.6, -4.6]} intensity={14} color="#38e0c8" />
      <pointLight position={[-4.4, 4.5, -3.2]} intensity={2} color="#ffe2cc" />
      <pointLight position={[-1.1, 5.1, -4.4]} intensity={16} color="#3a6bff" />
      <pointLight position={[-0.5, 4.9, -4.3]} intensity={9} color="#ff2a3a" />
      {/* lower floor */}
      <pointLight position={[-4.2, 2.2, -4.4]} intensity={30} color="#ff2438" />
      <pointLight position={[-6.3, 1.7, -3.8]} intensity={8} color="#ff5fb0" />
      <pointLight position={[0.9, 2.2, -4.6]} intensity={22} color="#2aa8ff" />
      <pointLight position={[5.3, 1.3, -5.6]} intensity={28} color="#ff7a14" />
      <pointLight position={[5.3, 1.4, -4.2]} intensity={12} color="#ff8a2a" />
      <pointLight position={[-2.2, 2.0, -0.6]} intensity={6} color="#9fdcff" />
      <pointLight position={[0.6, 2.6, 1.6]} intensity={12} color="#9fb6d8" />
      {/* furnishing round: warm bulbs, neon pendants, lounge, servers, pinball */}
      <pointLight position={[-5.7, 2.2, -4.0]} intensity={7} color="#ffa040" />
      <pointLight position={[0.9, 2.1, -4.25]} intensity={5} color="#22e4ff" />
      <pointLight position={[-2.35, 1.9, -4.1]} intensity={5} color="#ff2bd6" />
      <pointLight position={[0.6, 0.6, 1.2]} intensity={5} color="#ff2bd6" />
      <pointLight position={[0.25, 1.0, 2.3]} intensity={3} color="#22e4ff" />
      <pointLight position={[7.55, 1.2, -4.4]} intensity={6} color="#22e4ff" />
      <pointLight position={[5.6, 1.4, 2.3]} intensity={4} color="#ff2bd6" />
    </>
  )
}

/** Cool city light falling in through the big clear window, aimed down into the corner. */
function WindowLight() {
  const light = useRef<THREE.SpotLight>(null)
  const scene = useThree((st) => st.scene)
  useEffect(() => {
    const l = light.current
    if (!l) return
    l.target.position.set(4.1, 3.3, -2.5)
    scene.add(l.target) // the target must be in the scene for its position to count
    return () => void scene.remove(l.target)
  }, [scene])
  return (
    <spotLight
      ref={light}
      position={[4.1, 5.3, -5.2]}
      angle={1.0}
      penumbra={0.9}
      intensity={45}
      color="#8fb4ff"
      castShadow
      shadow-mapSize={[1024, 1024]}
      shadow-bias={-0.0005}
      shadow-normalBias={0.03}
    />
  )
}

/** Soft glow around neon tubes, screens and LEDs (anything brighter than ~1). */
function Effects() {
  return (
    <EffectComposer multisampling={4}>
      <Bloom mipmapBlur luminanceThreshold={0.85} luminanceSmoothing={0.2} intensity={0.7} radius={0.7} />
    </EffectComposer>
  )
}

/** The two big fans in the workstation corner turn slowly. */
function useFanSpin(scene: THREE.Object3D) {
  const rotors = useMemo(
    () => ['FanRotor0', 'FanRotor1'].map((n) => scene.getObjectByName(n)).filter(Boolean) as THREE.Object3D[],
    [scene],
  )
  const holo = useMemo(() => scene.getObjectByName('LoungeSetHoloShape') ?? null, [scene])
  useFrame((_, dt) => {
    rotors.forEach((r, i) => r.rotateZ(dt * (2.2 + i * 0.4)))
    if (holo) holo.rotation.y += dt * 0.8 // hologram on the lounge coffee table
  })
}

/* ---------------- textures ---------------- */

function servicesTexture() {
  const canvas = document.createElement('canvas')
  canvas.width = 1024
  canvas.height = 576
  const ctx = canvas.getContext('2d')!
  ctx.fillStyle = '#07090c'
  ctx.fillRect(0, 0, 1024, 576)
  ctx.fillStyle = '#fff'
  ctx.font = 'bold 84px ui-sans-serif, system-ui, sans-serif'
  ctx.fillText('What I Build', 64, 140)
  // the same four entries as the homepage's What We Build section (content/site.ts),
  // each in its arcade colour, with its typical timeline on the right
  site.work.forEach((w, i) => {
    const y = 250 + i * 76
    ctx.font = '40px ui-monospace, Consolas, monospace'
    ctx.fillStyle = w.arcade.color
    ctx.fillText(String(i + 1).padStart(2, '0'), 64, y)
    ctx.fillStyle = i === 0 ? '#ffffff' : '#c9ced4'
    ctx.fillText(w.title, 150, y)
    ctx.font = '26px ui-monospace, Consolas, monospace'
    ctx.fillStyle = '#6f7a84'
    ctx.textAlign = 'right'
    ctx.fillText(w.timeline, 960, y)
    ctx.textAlign = 'left'
  })
  ctx.fillStyle = 'rgba(0,0,0,0.25)'
  for (let y = 0; y < 576; y += 4) ctx.fillRect(0, y, 1024, 2)
  const tex = new THREE.CanvasTexture(canvas)
  tex.colorSpace = THREE.SRGBColorSpace
  tex.flipY = false
  return tex
}
