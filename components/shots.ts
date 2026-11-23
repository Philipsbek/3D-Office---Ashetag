// One camera "shot" per page. Changing the URL flies the camera to that shot.
// To add a new room: add a route in /app and an entry here.

export type Vec3 = [number, number, number]

export type Shot = {
  pos: Vec3 // where the camera sits
  target: Vec3 // what it looks at
  parallax: number // how much the mouse nudges the camera
}

export const SHOTS: Record<string, Shot> = {
  // the whole two-level loft, three-quarter view from the front right
  // aimed a little higher than the room so the city view opens up above it
  '/': { pos: [9.2, 9.5, 9.6], target: [-0.2, 0.0, -2.2], parallax: 0.8 },
  // upper floor, left: the two Razer desks, hero + typer, fan, bookshelf
  '/people': { pos: [-1.6, 5.3, 1.2], target: [-4.6, 3.9, -5.0], parallax: 0.2 },
  // upper floor, middle: straight onto the playable arcade screen (What We Build select)
  '/lab': { pos: [-1.57, 4.72, -3.9], target: [-1.57, 4.55, -5.31], parallax: 0.04 },
  // upper floor, right: the holographic Services board in the yellow window
  '/services': { pos: [4.1, 4.85, -2.45], target: [4.1, 4.9, -5.75], parallax: 0.2 },
}

export const shotFor = (pathname: string): Shot => SHOTS[pathname] ?? SHOTS['/']

/** The phone hero render (components/PhoneHero.tsx, made with ?capture=): the lobby view, shifted so the
 * whole office is centred in a portrait frame. Capture-only; the live 3D keeps SHOTS['/']. */
export const PHONE_HERO_SHOT: Shot = { pos: [10.99, 6.06, 10.72], target: [0.01, -3.4, -2.23], parallax: 0 }
