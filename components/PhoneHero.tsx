'use client'

// The phone homepage hero: a high-quality render of the office (made at desktop quality with
// ?capture=1, one per time of day) instead of the live 3D, which looks soft on phones.
// - People / Lab / Services bubbles and the boombox work like in 3D (tap the bubble or the area)
// - the four extra spots open their memos; one at a time they light up with the hover glass
//   (cut from a glow render) and a slow band of light, so people know they can be tapped
// - "Explore in 3D" loads the live office instead

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useDayPhase } from './daytime'
import { memoBus } from './memoBus'
import { music } from './music'
import { heroCover } from './heroMode'
import { PHONE_HERO } from './phoneHeroData'

const pct = (v: number) => `${(v * 100).toFixed(3)}%`

export default function PhoneHero({ onExplore }: { onExplore: () => void }) {
  const router = useRouter()
  const phase = useDayPhase().phase

  useEffect(() => {
    heroCover.set(true)
    return () => heroCover.set(false)
  }, [])

  const go = (link: string) => {
    if (link === '#music') return music.toggle()
    if (link.startsWith('#')) return memoBus.open(link.slice(1))
    router.push(link)
  }

  const extras = PHONE_HERO.spots.filter((s) => s.link.startsWith('#') && s.link !== '#music')
  const bubbles = PHONE_HERO.spots.filter((s) => !s.link.startsWith('#') || s.link === '#music')

  return (
    <div className="phone-hero">
      <div className="phone-hero-frame" style={{ aspectRatio: `${PHONE_HERO.width} / ${PHONE_HERO.height}` }}>
        <img
          className="phone-hero-img"
          src={`/phone-hero/${phase}.webp`}
          srcSet={`/phone-hero/${phase}-860.webp 860w, /phone-hero/${phase}.webp 1290w`}
          sizes="100vw"
          alt="Philips Bek's neon office on top of a tower in the city"
          fetchPriority="high"
        />

        {/* the "you can tap these" glow: one extra spot at a time */}
        {extras.map((s, i) => {
          const name = s.link.slice(1) as keyof typeof PHONE_HERO.glow
          const [x0, y0, x1, y1] = PHONE_HERO.glow[name]
          return (
            <img
              key={s.link}
              className="phone-hero-glow"
              src={`/phone-hero/glow-${phase}-${name}.webp`}
              alt=""
              aria-hidden="true"
              style={{ left: pct(x0), top: pct(y0), width: pct(x1 - x0), height: pct(y1 - y0), animationDelay: `${3 + i * 6}s` }}
            />
          )
        })}

        {/* tap areas */}
        {PHONE_HERO.spots.map((s) => {
          const [x0, y0, x1, y1] = s.rect
          const label = s.link === '#music' ? 'Play or mute music' : s.link.startsWith('#') ? `More about ${s.label}` : s.label
          return (
            <button
              key={s.link}
              type="button"
              className="phone-hero-spot"
              aria-label={label}
              style={{ left: pct(x0), top: pct(y0), width: pct(x1 - x0), height: pct(y1 - y0) }}
              onClick={() => go(s.link)}
            />
          )
        })}

        {/* the same speech bubbles as in 3D */}
        {bubbles.map((s, i) => {
          const music = s.link === '#music'
          return (
            <a
              key={s.link}
              href={music ? '#music' : s.link}
              className={`section-bubble phone-hero-bubble${music ? ' is-extra' : ''}`}
              style={{ left: pct(s.top[0]), top: pct(s.top[1]), ['--i' as string]: i } as React.CSSProperties}
              aria-label={music ? 'Play or mute music' : undefined}
              onClick={(e) => {
                e.preventDefault()
                go(s.link)
              }}
            >
              <span className="section-bubble-inner">
                {music ? (
                  <i className="section-bubble-info">♪</i>
                ) : (
                  <>
                    <i className="section-bubble-dot" />
                    <b>{s.label}</b>
                    <em>→</em>
                  </>
                )}
              </span>
            </a>
          )
        })}
      </div>

      <button type="button" className="phone-hero-explore" onClick={onExplore}>
        <span aria-hidden="true">◇</span> Explore in 3D
      </button>
    </div>
  )
}
