'use client'
// Loading screen over the 3D hero while the office model downloads.
// Shows the real download progress, then fades away once the office has rendered.

import { useEffect, useState } from 'react'
import { useLoadProgress } from './loadProgress'

const mb = (bytes: number) => (bytes / 1024 / 1024).toFixed(1)

/** Just the visuals — also used as the fallback while the 3D code itself loads. */
export function LoaderView({ loaded = 0, total = 0, leaving = false }: { loaded?: number; total?: number; leaving?: boolean }) {
  const known = total > 0
  const pct = known ? Math.min(100, Math.floor((loaded / total) * 100)) : null
  return (
    <div className={`loader ${leaving ? 'is-leaving' : ''}`} role="status" aria-live="polite" aria-busy={!leaving}>
      <div className="loader-bottom">
        <p className="loader-label">
          <i aria-hidden /> {leaving ? 'Office ready' : 'Loading the office'}
        </p>
        <div className="loader-row">
          <span className="loader-pct">{pct ?? (loaded > 0 ? '··' : 0)}<span className="loader-pct-sign">%</span></span>
          <span className="loader-bytes">{known ? `${mb(loaded)} / ${mb(total)} MB` : loaded > 0 ? `${mb(loaded)} MB` : ''}</span>
        </div>
        <div className="loader-bar" aria-hidden>
          <div
            className={`loader-fill ${known ? '' : 'is-indeterminate'}`}
            style={known ? { transform: `scaleX(${loaded / total})` } : undefined}
          />
        </div>
      </div>
    </div>
  )
}

export default function Loader() {
  const { loaded, total, ready } = useLoadProgress()
  const [gone, setGone] = useState(false)

  useEffect(() => {
    if (!ready) return
    const t = setTimeout(() => setGone(true), 700) // matches the CSS fade
    return () => clearTimeout(t)
  }, [ready])

  if (gone) return null
  // once ready, show the bar full while it fades
  return <LoaderView loaded={ready ? total || 1 : loaded} total={ready ? total || 1 : total} leaving={ready} />
}
