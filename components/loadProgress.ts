// Tiny shared store for the office download, read by the loading screen.
// - progress: bytes received / total (0..1), or null if the size is unknown
// - ready: the model is parsed and on screen

import { useSyncExternalStore } from 'react'

type State = { loaded: number; total: number; ready: boolean }

let state: State = { loaded: 0, total: 0, ready: false }
const listeners = new Set<() => void>()
const emit = (next: Partial<State>) => {
  state = { ...state, ...next }
  listeners.forEach((l) => l())
}

// Used when the server doesn't send the file size (e.g. compressed responses).
let expectedBytes = 0
export const setExpectedBytes = (bytes: number) => (expectedBytes = bytes)

export const reportBytes = (loaded: number, total: number) => {
  if (!total && expectedBytes) {
    total = expectedBytes
    loaded = Math.min(loaded, total * 0.99) // never claim 100% before it's really done
  }
  emit({ loaded, total })
}
export const markReady = () => emit({ ready: true })

const subscribe = (l: () => void) => {
  listeners.add(l)
  return () => listeners.delete(l)
}
export const useLoadProgress = () => useSyncExternalStore(subscribe, () => state, () => state)

/**
 * Passed to useGLTF as its "extendLoader" hook: wraps loader.load so download
 * progress events reach the store (drei doesn't expose them otherwise).
 */
export function trackProgress(loader: { load: (...args: never[]) => unknown }) {
  const l = loader as unknown as {
    load: (url: string, onLoad: unknown, onProgress?: (e: ProgressEvent) => void, onError?: unknown) => unknown
  }
  if ((l as { __tracked?: boolean }).__tracked) return
  ;(l as { __tracked?: boolean }).__tracked = true
  const original = l.load.bind(l)
  l.load = (url, onLoad, onProgress, onError) =>
    original(
      url,
      onLoad,
      (e: ProgressEvent) => {
        reportBytes(e.loaded, e.lengthComputable ? e.total : 0)
        onProgress?.(e)
      },
      onError,
    )
}
