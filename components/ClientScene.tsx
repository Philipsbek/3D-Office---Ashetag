'use client'
// Loads the 3D scene in the browser only (three.js needs window/document).
// On phones the homepage shows a high-quality picture instead (components/PhoneHero.tsx); the 3D
// loads the first time the visitor goes to People / Lab / Services or taps "Explore in 3D".
import dynamic from 'next/dynamic'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'
import { LoaderView } from './Loader'
import { PHONE_IMAGE_HERO } from './heroMode'
import PhoneHero from './PhoneHero'

const Scene = dynamic(() => import('./Scene'), {
  ssr: false,
  // same loading screen while the 3D code itself downloads
  loading: () => (
    <div className="scene">
      <LoaderView />
    </div>
  ),
})

export default function ClientScene() {
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)
  const [explore, setExplore] = useState(false) // the visitor asked for the live 3D on the homepage
  const [need3d, setNeed3d] = useState(false)
  useEffect(() => setMounted(true), [])
  useEffect(() => {
    if (pathname !== '/') setNeed3d(true)
  }, [pathname])

  if (!mounted) return <div className="scene" /> // decided in the browser (screen size)
  if (!PHONE_IMAGE_HERO) return <Scene />
  const image = pathname === '/' && !explore
  return (
    <>
      {(need3d || explore) && <Scene />}
      {image && (
        <PhoneHero
          onExplore={() => {
            setExplore(true)
            setNeed3d(true)
          }}
        />
      )}
    </>
  )
}
