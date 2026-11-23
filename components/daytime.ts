'use client'

// Real time of day: the city follows the visitor's own clock.
//   night 19:30–05:00 · dawn 05:00–07:00 · day 07:00–17:30 · dusk 17:30–19:30
// Each phase has its own sky (horizon + zenith), haze/fog colour, ambient light and how bright the
// unlit city buildings read. Night is the original neon look.
// Override for testing: ?time=night | dawn | day | dusk

import { useEffect, useState } from 'react'

export type Phase = 'night' | 'dawn' | 'day' | 'dusk'

export type Palette = {
  phase: Phase
  horizon: string // sky at the horizon = scene haze / fog / background
  top: string // sky overhead
  stars: number // star opacity
  moon: boolean
  ambient: number // hemisphere light multiplier
  city: number // brightness multiplier for the unlit city buildings
  fogFar: number // how far you can see into the haze
  sun: { color: string; intensity: number; elevation: number } // 0 = no sun (night)
}

export const PALETTES: Record<Phase, Palette> = {
  night: { phase: 'night', horizon: '#3a1a4c', top: '#020208', stars: 0.6, moon: true, ambient: 1, city: 1, fogFar: 470, sun: { color: '#000000', intensity: 0, elevation: 0 } },
  dawn: { phase: 'dawn', horizon: '#d98aa0', top: '#2a3c74', stars: 0.12, moon: true, ambient: 2.2, city: 2.1, fogFar: 540, sun: { color: '#ffb3c4', intensity: 1.4, elevation: 0.25 } },
  day: { phase: 'day', horizon: '#a9c6ec', top: '#3c74c4', stars: 0, moon: false, ambient: 3.6, city: 3.2, fogFar: 700, sun: { color: '#fff4e0', intensity: 2.6, elevation: 0.9 } },
  dusk: { phase: 'dusk', horizon: '#e07848', top: '#33296e', stars: 0.15, moon: false, ambient: 2, city: 2, fogFar: 540, sun: { color: '#ff9a52', intensity: 1.8, elevation: 0.2 } },
}

function override(): Phase | null {
  if (typeof window === 'undefined') return null
  const t = new URLSearchParams(window.location.search).get('time')
  return t === 'night' || t === 'dawn' || t === 'day' || t === 'dusk' ? t : null
}

export function phaseAt(d: Date): Phase {
  const h = d.getHours() + d.getMinutes() / 60
  if (h >= 5 && h < 7) return 'dawn'
  if (h >= 7 && h < 17.5) return 'day'
  if (h >= 17.5 && h < 19.5) return 'dusk'
  return 'night'
}

/** The visitor's current phase, re-checked every minute. */
export function useDayPhase(): Palette {
  const [phase, setPhase] = useState<Phase>(() => override() ?? (typeof window === 'undefined' ? 'night' : phaseAt(new Date())))
  useEffect(() => {
    if (override()) return
    const id = setInterval(() => setPhase(phaseAt(new Date())), 60_000)
    return () => clearInterval(id)
  }, [])
  return PALETTES[phase]
}

