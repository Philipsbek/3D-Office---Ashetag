'use client'
// Loads the 3D scene in the browser only (three.js needs window/document).
import dynamic from 'next/dynamic'
import { LoaderView } from './Loader'

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
  return <Scene />
}
