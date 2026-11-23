'use client'

// Phones (touch, portrait, small screen) see a high-quality pre-rendered picture of the office on the
// homepage instead of the live 3D (components/PhoneHero.tsx). The 3D still loads for People / Lab /
// Services, or when the visitor taps "Explore in 3D".
// Override for testing: ?hero=image or ?hero=3d

import { CAPTURE } from './capture'

function detect(): boolean {
  if (typeof window === 'undefined' || CAPTURE) return false
  const h = new URLSearchParams(window.location.search).get('hero')
  if (h === 'image') return true
  if (h === '3d') return false
  const coarse = window.matchMedia?.('(pointer: coarse)').matches ?? false
  const portrait = window.innerHeight > window.innerWidth
  const small = Math.min(window.screen?.width ?? 9999, window.screen?.height ?? 9999) < 820
  return coarse && portrait && small
}

/** decided once, when the page loads */
export const PHONE_IMAGE_HERO = detect()

// While the picture covers the screen, the live 3D (if it was loaded for another page) pauses.
type Listener = (covered: boolean) => void
const listeners = new Set<Listener>()
let covered = false
export const heroCover = {
  get covered() {
    return covered
  },
  set(v: boolean) {
    if (v === covered) return
    covered = v
    listeners.forEach((l) => l(v))
  },
  on(l: Listener) {
    listeners.add(l)
    return () => void listeners.delete(l)
  },
}
