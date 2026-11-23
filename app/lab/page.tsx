'use client'

// The Lab: the camera is zoomed onto the arcade cabinet, which shows a "What We Build"
// select screen. Picking a tile opens an info panel here with a WhatsApp button.
// On-screen buttons let phone users drive the cabinet without a keyboard.

import { useEffect, useState } from 'react'
import { arcadeBus } from '@/components/arcadeBus'
import WhatsAppIcon, { whatsappHref } from '@/components/WhatsAppIcon'
import { site } from '@/content/site'

export default function Lab() {
  const [open, setOpen] = useState<number | null>(null)

  useEffect(() => arcadeBus.on((e) => e.type === 'select' && setOpen(e.index)), [])

  const close = () => {
    setOpen(null)
    arcadeBus.emit({ type: 'close' })
  }

  // Esc closes the panel (instead of leaving the Lab)
  useEffect(() => {
    if (open === null) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return
      e.preventDefault()
      e.stopImmediatePropagation()
      close()
    }
    window.addEventListener('keydown', onKey, true)
    return () => window.removeEventListener('keydown', onKey, true)
  }, [open])

  const press = (code: string) => ({
    onPointerDown: (e: React.PointerEvent) => {
      e.preventDefault()
      arcadeBus.emit({ type: 'key', code, down: true })
    },
    onPointerUp: () => arcadeBus.emit({ type: 'key', code, down: false }),
    onPointerLeave: () => arcadeBus.emit({ type: 'key', code, down: false }),
  })

  const item = open !== null ? site.work[open] : null
  const article = item && /^[AEIOU]/i.test(item.title) ? 'an' : 'a'
  const message = item
    ? `Hi Philips, I'm interested in ${article} ${item.title.replace(/s$/, '')} and would like to know more!`
    : ''

  return (
    <>
      {item === null ? (
        <section className="panel lab-hint">
          <h1>What I Build</h1>
          <p>Pick a build on the arcade: ← → to move · Space to select · or tap the screen. Esc to leave.</p>
        </section>
      ) : (
        <aside
          className="build-panel"
          style={{ '--accent': item.arcade.color } as React.CSSProperties}
          aria-labelledby="build-title"
        >
          <div className="build-head">
            <span className="build-eyebrow">What I Build · 0{(open ?? 0) + 1}</span>
            <button type="button" className="build-close" onClick={close} aria-label="Back to the arcade">
              ← Back <kbd>Esc</kbd>
            </button>
          </div>
          <h1 id="build-title" className="build-title">{item.title}</h1>
          <p className="build-lead">{item.description}</p>
          <p className="build-copy">{item.details}</p>
          <h2 className="build-sub">What&apos;s included</h2>
          <ul className="build-list">
            {item.includes.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
          <div className="build-meta">
            <span>Typical timeline</span>
            <b>{item.timeline}</b>
          </div>
          <ul className="build-tags">
            {item.services.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
          <a className="build-wa" href={whatsappHref(site.whatsapp, message)} target="_blank" rel="noopener noreferrer">
            <WhatsAppIcon size={22} />
            Message me on WhatsApp
          </a>
        </aside>
      )}

      {/* touch controls for the cabinet (phones / tablets) */}
      {item === null && (
        <div className="arcade-pad" aria-label="Arcade controls">
          <button type="button" aria-label="Left" {...press('ArrowLeft')}>◀</button>
          <button type="button" className="arcade-pad-go" aria-label="Select" {...press('Space')}>SELECT</button>
          <button type="button" aria-label="Right" {...press('ArrowRight')}>▶</button>
          <button type="button" aria-label="Back to menu" {...press('Escape')}>MENU</button>
        </div>
      )}
    </>
  )
}
