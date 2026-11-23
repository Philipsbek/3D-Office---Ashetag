import HomeContent from '@/components/HomeContent'

// The 3D office (rendered in the layout) fills the first screen as the hero.
// This transparent spacer reserves that screen; the content then scrolls up over it.
export default function Home() {
  return (
    <>
      <div className="hero" aria-label="Interactive 3D office — click a glowing marker to explore">
        <p className="hero-hint">Click the office to explore · Scroll ↓</p>
      </div>
      <HomeContent />
    </>
  )
}
