'use client'

// "What I Build" rows. Clicking a row's image lifts it off the page like picking up a letter
// in a game: it glides to the centre of the screen while growing, tips up a little, then
// flips over to show the back, which lists my past projects for that row.
// Esc, the close button or a click outside puts it back (the same motion in reverse).

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { site } from '@/content/site'

type Work = (typeof site.work)[number]
type Rect = { left: number; top: number; width: number; height: number }

const OPEN_MS = 1150
const CLOSE_MS = 950
const EASE = 'cubic-bezier(.22, .8, .24, 1)'

/** Where the open card sits: centred, as big as fits (16:9 on wide screens, taller on phones). */
function targetRect(): Rect {
  const vw = window.innerWidth
  const vh = window.innerHeight
  let width: number, height: number
  if (vw < 760) {
    width = vw - 24
    height = Math.min(vh - 96, 720)
  } else {
    width = Math.min(1120, vw * 0.9, ((vh * 0.84) * 16) / 9)
    height = (width * 9) / 16
  }
  return { left: (vw - width) / 2, top: (vh - height) / 2, width, height }
}

const px = (r: Rect) => ({ left: `${r.left}px`, top: `${r.top}px`, width: `${r.width}px`, height: `${r.height}px` })

function reducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

export default function WorkShowcase() {
  const [open, setOpen] = useState<{ index: number; from: Rect } | null>(null)
  const media = useRef<(HTMLButtonElement | null)[]>([])

  const show = (index: number) => {
    const el = media.current[index]
    if (!el || open) return
    const r = el.getBoundingClientRect()
    setOpen({ index, from: { left: r.left, top: r.top, width: r.width, height: r.height } })
  }

  return (
    <>
      <ol className="projects">
        {site.work.map((p, i) => (
          <li key={p.title} className="project">
            <button
              type="button"
              ref={(el) => {
                media.current[i] = el
              }}
              className={`project-media project-flip${open?.index === i ? ' is-lifted' : ''}`}
              onClick={() => show(i)}
              aria-haspopup="dialog"
              aria-label={`${p.title}: see my past projects`}
            >
              <img src={p.image} alt="" width={1600} height={900} loading="lazy" />
              <span className="project-hint" aria-hidden="true">
                <span className="project-hint-icon">↻</span> Past projects
              </span>
            </button>
            <p className="body concrete project-desc">{p.description}</p>
            <h3 className="project-title">{p.title}</h3>
            <ul className="project-services body">
              {p.services.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
          </li>
        ))}
      </ol>
      {open && (
        <ProjectLetter
          work={site.work[open.index]}
          from={open.from}
          source={() => media.current[open.index]}
          onClosed={() => {
            const back = media.current[open.index]
            setOpen(null)
            back?.focus({ preventScroll: true })
          }}
        />
      )}
    </>
  )
}

function ProjectLetter({ work, from, source, onClosed }: { work: Work; from: Rect; source: () => HTMLElement | null; onClosed: () => void }) {
  const card = useRef<HTMLDivElement>(null)
  const inner = useRef<HTMLDivElement>(null)
  const backdrop = useRef<HTMLDivElement>(null)
  const closeBtn = useRef<HTMLButtonElement>(null)
  const [rect, setRect] = useState<Rect>(() => targetRect())
  const closing = useRef(false)

  // open: from the image's place on the page to the centre, then flip
  useLayoutEffect(() => {
    const c = card.current!, n = inner.current!, b = backdrop.current!
    const to = targetRect()
    if (reducedMotion()) {
      n.style.transform = 'rotateY(180deg)'
      b.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 200, fill: 'both' })
      c.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 200, fill: 'both' })
    } else {
      b.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 450, easing: 'ease-out', fill: 'both' })
      c.animate(
        [
          { ...px(from), transform: 'translateY(0) rotate(0deg)', boxShadow: '0 0 0 rgba(0,0,0,0)' },
          { offset: 0.55, ...px(to), transform: 'translateY(-14px) rotate(-2.2deg)', boxShadow: '0 40px 80px rgba(0,0,0,.7)' },
          { ...px(to), transform: 'translateY(0) rotate(0deg)', boxShadow: '0 30px 70px rgba(0,0,0,.6)' },
        ],
        { duration: OPEN_MS, easing: EASE, fill: 'both' },
      )
      n.animate(
        [
          { transform: 'rotateY(0deg) rotateX(0deg)' },
          { offset: 0.38, transform: 'rotateY(0deg) rotateX(8deg)' },
          { offset: 0.8, transform: 'rotateY(172deg) rotateX(-2deg)' },
          { transform: 'rotateY(180deg) rotateX(0deg)' },
        ],
        { duration: OPEN_MS, easing: 'cubic-bezier(.45, .05, .25, 1)', fill: 'both' },
      )
    }
    const t = window.setTimeout(() => closeBtn.current?.focus({ preventScroll: true }), reducedMotion() ? 200 : OPEN_MS - 150)
    return () => clearTimeout(t)
  }, [from])

  const close = useCallback(() => {
    if (closing.current) return
    closing.current = true
    const c = card.current!, n = inner.current!, b = backdrop.current!
    const el = source()
    const r = el?.getBoundingClientRect()
    const home: Rect = r ? { left: r.left, top: r.top, width: r.width, height: r.height } : from
    const now = targetRect()
    c.getAnimations().forEach((a) => a.cancel())
    n.getAnimations().forEach((a) => a.cancel())
    if (reducedMotion()) {
      b.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 180, fill: 'both' })
      c.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 180, fill: 'both' }).onfinish = onClosed
      return
    }
    b.animate([{ opacity: 1 }, { opacity: 0 }], { duration: CLOSE_MS, easing: 'ease-in', fill: 'both' })
    n.animate(
      [
        { transform: 'rotateY(180deg) rotateX(0deg)' },
        { offset: 0.5, transform: 'rotateY(8deg) rotateX(6deg)' },
        { transform: 'rotateY(0deg) rotateX(0deg)' },
      ],
      { duration: CLOSE_MS, easing: 'cubic-bezier(.45, .05, .3, 1)', fill: 'both' },
    )
    c.animate(
      [
        { ...px(now), transform: 'translateY(0) rotate(0deg)', boxShadow: '0 30px 70px rgba(0,0,0,.6)' },
        { offset: 0.45, ...px(now), transform: 'translateY(-10px) rotate(1.6deg)', boxShadow: '0 40px 80px rgba(0,0,0,.7)' },
        { ...px(home), transform: 'translateY(0) rotate(0deg)', boxShadow: '0 0 0 rgba(0,0,0,0)' },
      ],
      { duration: CLOSE_MS, easing: EASE, fill: 'both' },
    ).onfinish = onClosed
  }, [from, onClosed, source])

  // Esc closes; keep Tab inside the card; no page scrolling behind it
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        close()
      } else if (e.key === 'Tab') {
        const f = card.current?.querySelectorAll<HTMLElement>('a[href], button')
        if (!f || !f.length) return
        const first = f[0], last = f[f.length - 1]
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault()
          last.focus()
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault()
          first.focus()
        }
      }
    }
    const onResize = () => {
      if (closing.current) return
      const r = targetRect()
      card.current?.getAnimations().forEach((a) => a.cancel())
      setRect(r)
    }
    const html = document.documentElement
    const prev = html.style.overflow
    html.style.overflow = 'hidden'
    window.addEventListener('keydown', onKey)
    window.addEventListener('resize', onResize)
    return () => {
      html.style.overflow = prev
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('resize', onResize)
    }
  }, [close])

  return createPortal(
    <div className="letter-layer">
      <div ref={backdrop} className="letter-backdrop" onClick={close} />
      <div
        ref={card}
        className="letter"
        style={px(rect)}
        role="dialog"
        aria-modal="true"
        aria-labelledby="letter-title"
      >
        <div ref={inner} className="letter-inner" style={{ transform: 'rotateY(180deg)' }}>
          <div className="letter-face letter-front" aria-hidden="true">
            <img src={work.image} alt="" />
          </div>
          <div className="letter-face letter-back">
            <header className="letter-head">
              <div>
                <p className="letter-eyebrow">Past projects<sup className="counter">({work.projects.length})</sup></p>
                <h2 id="letter-title" className="letter-title">{work.title}</h2>
              </div>
              <button ref={closeBtn} type="button" className="build-close" onClick={close} aria-label="Close past projects">
                Close <kbd>Esc</kbd>
              </button>
            </header>
            <ul className="letter-grid">
              {work.projects.map((p) => (
                <li key={p.name} className="letter-project">
                  <div className="letter-shot">
                    <img src={p.image} alt={`${p.name} screenshot`} loading="lazy" />
                  </div>
                  <div className="letter-meta">
                    <h3>{p.name}</h3>
                    <p>
                      {p.type} · {p.year}
                    </p>
                  </div>
                  {p.url ? (
                    <a className="letter-link" href={p.url} target="_blank" rel="noopener noreferrer">
                      Visit site ↗
                    </a>
                  ) : (
                    <span className="letter-link is-soon">Link coming soon</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  )
}
