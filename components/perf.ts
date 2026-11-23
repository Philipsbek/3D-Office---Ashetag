'use client'

// Phone mode: phones and low-power devices get a lighter version of the 3D office
// (normal-resolution rendering, no shadows, fewer lights, a lighter glow, less traffic).
// Desktop keeps the full look.
//
// Override for testing: add ?quality=low or ?quality=high to the address.

function detectLowPower(): boolean {
  if (typeof window === 'undefined') return false
  const q = new URLSearchParams(window.location.search).get('quality')
  if (q === 'low') return true
  if (q === 'high') return false
  const coarse = window.matchMedia?.('(pointer: coarse)').matches ?? false
  const small = Math.min(window.screen?.width ?? 9999, window.screen?.height ?? 9999) < 820
  const nav = navigator as Navigator & { deviceMemory?: number }
  const weak = (nav.deviceMemory !== undefined && nav.deviceMemory <= 4) || (navigator.hardwareConcurrency ?? 8) <= 4
  return (coarse && small) || (coarse && weak)
}

/** true on phones / low-power devices (decided once, when the page loads) */
export const LOW_POWER = detectLowPower()
