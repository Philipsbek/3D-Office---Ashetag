'use client'

// On-screen navigation between the office's 3D sections:
// - a "Lobby" back button (also Esc) whenever you're zoomed into a section
// - a bottom-centre pill: ‹ LOBBY SERVICES PEOPLE LAB ›, the current one in orange
// - ← / → keys step between sections (not in the Lab, where they play the game)
// On the homepage the pill only shows while the 3D hero is on screen.

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

export const SECTIONS = [
  { href: '/', label: 'Lobby' },
  { href: '/services', label: 'Services' },
  { href: '/people', label: 'People' },
  { href: '/lab', label: 'Lab' },
]

export default function SectionNav() {
  const pathname = usePathname()
  const router = useRouter()
  const idx = Math.max(0, SECTIONS.findIndex((s) => s.href === pathname))
  const prev = SECTIONS[(idx - 1 + SECTIONS.length) % SECTIONS.length]
  const next = SECTIONS[(idx + 1) % SECTIONS.length]
  const inSection = pathname !== '/'

  // hide the pill once the homepage content has scrolled over the hero
  const [heroVisible, setHeroVisible] = useState(true)
  useEffect(() => {
    if (inSection) {
      setHeroVisible(true)
      return
    }
    const check = () => setHeroVisible(window.scrollY < window.innerHeight * 0.35)
    check()
    window.addEventListener('scroll', check, { passive: true })
    return () => window.removeEventListener('scroll', check)
  }, [inSection])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (pathname === '/lab') return // arrows belong to the arcade game there
      if (!heroVisible) return // reading the homepage content: leave the keys alone
      if (e.target instanceof HTMLElement && e.target.closest('input, textarea')) return
      if (e.key === 'ArrowLeft') router.push(prev.href)
      if (e.key === 'ArrowRight') router.push(next.href)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [pathname, prev.href, next.href, router, heroVisible])

  return (
    <>
      {inSection && (
        <Link href="/" className="back-btn" aria-label="Back to the lobby">
          <span aria-hidden>←</span> Lobby <kbd>Esc</kbd>
        </Link>
      )}

      <nav className={`switcher ${heroVisible ? '' : 'is-hidden'}`} aria-label="3D sections" aria-hidden={!heroVisible}>
        <Link href={prev.href} className="switcher-arrow" aria-label={`Previous: ${prev.label}`} tabIndex={heroVisible ? 0 : -1}>
          ‹
        </Link>
        {SECTIONS.map((s, i) => (
          <Link
            key={s.href}
            href={s.href}
            className={`switcher-item ${i === idx ? 'on' : ''}`}
            aria-current={i === idx ? 'page' : undefined}
            tabIndex={heroVisible ? 0 : -1}
          >
            {s.label}
          </Link>
        ))}
        <Link href={next.href} className="switcher-arrow" aria-label={`Next: ${next.label}`} tabIndex={heroVisible ? 0 : -1}>
          ›
        </Link>
      </nav>
    </>
  )
}
