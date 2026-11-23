'use client'

// Small round speaker button (bottom right, above WhatsApp) for the office music.
// - music starts on the visitor's first click / tap / key press (browsers require one),
//   unless they muted it on an earlier visit
// - it fades out while the tab is hidden or the 3D office is scrolled away, and back in after

import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import { music } from './music'

export default function MusicToggle() {
  const [playing, setPlaying] = useState(false)
  const pathname = usePathname()

  useEffect(() => music.on((e) => setPlaying(e.playing)), [])

  // first interaction anywhere starts it
  useEffect(() => {
    const first = (e: Event) => {
      // the button and the boombox handle their own clicks
      if (e.target instanceof Element && e.target.closest('.music-toggle')) return
      if (!music.muted) music.start()
      remove()
    }
    const remove = () => {
      window.removeEventListener('pointerdown', first, true)
      window.removeEventListener('keydown', first, true)
    }
    window.addEventListener('pointerdown', first, true)
    window.addEventListener('keydown', first, true)
    return remove
  }, [])

  // fade out while hidden or while the office hero is scrolled away (homepage)
  useEffect(() => {
    const check = () => {
      const away = pathname === '/' && window.scrollY > window.innerHeight * 0.9
      music.setPaused(document.hidden || away)
    }
    check()
    document.addEventListener('visibilitychange', check)
    window.addEventListener('scroll', check, { passive: true })
    return () => {
      document.removeEventListener('visibilitychange', check)
      window.removeEventListener('scroll', check)
    }
  }, [pathname])

  return (
    <button
      type="button"
      className={`music-toggle${playing ? ' is-on' : ''}`}
      onClick={() => music.toggle()}
      aria-label={playing ? 'Mute music' : 'Play music'}
      aria-pressed={playing}
      title={playing ? 'Mute music' : 'Play music'}
    >
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor" />
        {playing ? (
          <g fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path className="wave w1" d="M16 9.5a3.5 3.5 0 0 1 0 5" />
            <path className="wave w2" d="M18.5 7a7 7 0 0 1 0 10" />
          </g>
        ) : (
          <path d="M16 9l5 6M21 9l-5 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        )}
      </svg>
    </button>
  )
}
