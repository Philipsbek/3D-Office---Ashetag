// Opens a memo card (components/Memo.tsx) from anywhere, e.g. clicking Philips napping in the 3D office.
// The camera (Scene.tsx) also listens, and flies in to frame whoever the memo is about.

type Listener = (id: string | null) => void
const listeners = new Set<Listener>()
let current: string | null = null

export const memoBus = {
  get current() {
    return current
  },
  open(id: string) {
    current = id
    listeners.forEach((l) => l(id))
  },
  close() {
    current = null
    listeners.forEach((l) => l(null))
  },
  on(l: Listener) {
    listeners.add(l)
    return () => {
      listeners.delete(l)
    }
  },
}

/** React hook: the open memo's id, or null */
import { useEffect, useState } from 'react'
export function useOpenMemo() {
  const [id, setId] = useState<string | null>(current)
  useEffect(() => memoBus.on(setId), [])
  return id
}
