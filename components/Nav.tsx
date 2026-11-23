'use client'
// Fixed 36px top bar: wordmark left, links centred, live status + contact right.
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { site } from '@/content/site'

const LINKS = [
  { href: '/#work', label: 'Work', count: site.work.length },
  { href: '/#services', label: 'Services', count: site.capabilities.columns.length },
  { href: '/people', label: 'People' },
  { href: '/lab', label: 'Lab' },
]

export default function Nav() {
  const pathname = usePathname()
  const router = useRouter()

  // Esc always flies back to the lobby
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && pathname !== '/') router.push('/')
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [pathname, router])

  return (
    <header className="topbar">
      <Link href="/" className="wordmark-link">
        {site.name}
      </Link>
      <nav className="topbar-links" aria-label="Main">
        {LINKS.map((l) => (
          <Link key={l.href} href={l.href} aria-current={pathname === l.href ? 'page' : undefined}>
            {l.label}
            {l.count !== undefined && <sup className="counter">({l.count})</sup>}
          </Link>
        ))}
      </nav>
      <div className="topbar-right">
        <span className="online">
          <i aria-hidden /> Online
        </span>
        <Link href="/#contact">Contact me</Link>
      </div>
    </header>
  )
}
