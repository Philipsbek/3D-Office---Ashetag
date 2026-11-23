// Tiny message bus between the arcade cabinet (drawn inside the 3D scene) and the
// Lab page's HTML (info panel + on-screen buttons). Both sides import this module.

export type ArcadeEvent =
  | { type: 'select'; index: number } // the cabinet picked a What I Build entry
  | { type: 'close' } // the info panel was closed: back to the select screen
  | { type: 'key'; code: string; down: boolean } // on-screen buttons (phones)

type Listener = (e: ArcadeEvent) => void
const listeners = new Set<Listener>()

export const arcadeBus = {
  emit(e: ArcadeEvent) {
    listeners.forEach((l) => l(e))
  },
  on(l: Listener) {
    listeners.add(l)
    return () => {
      listeners.delete(l)
    }
  },
}
