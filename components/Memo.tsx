'use client'

// A small sticky-memo card about someone in the office (e.g. Philips, napping at the
// lounge table). Opened via memoBus when you click them in 3D: the camera flies in and
// frames them on the left while this card slides in on the right (from the bottom on
// phones). Esc / × / clicking the scene closes it and the camera flies back.

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { memoBus, useOpenMemo } from './memoBus'
import { site } from '@/content/site'

export default function Memo() {
  const id = useOpenMemo()
  const setId = (v: null) => (v === null ? memoBus.close() : undefined)

  // deep link: /?memo=pinball opens that memo once the page loads
  useEffect(() => {
    const want = new URLSearchParams(window.location.search).get('memo')
    if (want && site.memos[want]) {
      const t = setTimeout(() => memoBus.open(want), 1500) // after the office has appeared
      return () => clearTimeout(t)
    }
  }, [])

  // going to another page closes it
  const pathname = usePathname()
  useEffect(() => {
    if (memoBus.current) memoBus.close()
  }, [pathname])

  useEffect(() => {
    if (!id) return
    // capture phase: Esc closes the memo instead of flying back to the lobby
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return
      e.preventDefault()
      e.stopImmediatePropagation()
      setId(null)
    }
    window.addEventListener('keydown', onKey, true)
    return () => window.removeEventListener('keydown', onKey, true)
  }, [id])

  const memo = id ? site.memos[id] : null
  if (!memo) return null

  return (
    <div className="memo-backdrop" onClick={() => setId(null)}>
      <article className="memo" role="dialog" aria-labelledby="memo-name" onClick={(e) => e.stopPropagation()}>
        <span className="memo-tape" aria-hidden />
        <header className="memo-head">
          <span className="memo-eyebrow">{memo.sleepy ? 'Staff memo' : 'Memo'}</span>
          <button type="button" className="memo-close" onClick={() => setId(null)} aria-label="Close memo">
            ×
          </button>
        </header>
        <h2 id="memo-name" className="memo-name">
          {memo.name}
          {memo.sleepy && (
            <span className="memo-zzz" aria-hidden>
              z z Z
            </span>
          )}
        </h2>
        <p className="memo-role">{memo.role}</p>
        <p className="memo-status">
          <i aria-hidden /> {memo.status}
        </p>
        <p className="memo-note">{memo.note}</p>
        <dl className="memo-facts">
          {memo.facts.map(([k, v]) => (
            <div key={k}>
              <dt>{k}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
        <p className="memo-signoff">{memo.signoff}</p>
      </article>
    </div>
  )
}
