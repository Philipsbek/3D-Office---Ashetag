'use client'

// Capture mode, used to render the high-quality phone hero images (components/PhoneHero.tsx):
//   /?capture=1&time=night   the office at full desktop quality, UI hidden;
//   window.__captureGlow = true switches the extra spots' hover glass on (for the glow overlays)
// window.__capture then holds where every hotspot lands on screen, and
// window.__captureShot() returns the frame as a PNG data URL. Render at 430 x 932 (x3 = 1290 x 2796);
// the 2026-11-24 images were saved through a temporary dev-only API route, then processed into
// public/phone-hero/ and components/phoneHeroData.ts (glow overlays = glow frame minus plain frame).

export const CAPTURE: string | null =
  typeof window === 'undefined' ? null : new URLSearchParams(window.location.search).get('capture')
