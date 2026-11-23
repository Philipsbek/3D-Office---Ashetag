'use client'

// The office music: an audio track (public/audio/office-music.m4a) on loop, routed through the
// Web Audio API so it can fade in / out smoothly. A small analyser listens to the low end and
// reports kicks as "beats" (the boombox pulses on them).
//
// Browsers only allow sound after the visitor interacts with the page, so music starts on
// the first click/tap/key (unless they muted it before). `music.on(...)` reports state and beats.

type Listener = (e: { playing: boolean; beat?: number }) => void

const SRC = '/audio/office-music.m4a'
const STORE = 'pb-music-muted'

class Music {
  private ctx: AudioContext | null = null
  private master: GainNode | null = null
  private audio: HTMLAudioElement | null = null
  private analyser: AnalyserNode | null = null
  private bins: Uint8Array<ArrayBuffer> | null = null
  private raf: number | null = null
  private stopTimer: number | null = null
  private listeners = new Set<Listener>()
  playing = false
  private startedAt = 0
  // beat detection
  private avg = 0
  private lastBeat = 0
  private beats = 0
  /** the visitor chose to mute (remembered between visits) */
  muted = (() => {
    try {
      return localStorage.getItem(STORE) === '1'
    } catch {
      return false
    }
  })()
  private paused = false // auto-pause (tab hidden / scrolled away), not the visitor's choice

  on(l: Listener) {
    this.listeners.add(l)
    return () => void this.listeners.delete(l)
  }
  private emit(beat?: number) {
    this.listeners.forEach((l) => l({ playing: this.playing, beat }))
  }

  private build() {
    if (this.ctx) return
    const Ctx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext
    const ctx = new Ctx()
    const audio = new Audio(SRC)
    audio.loop = true
    audio.preload = 'auto'
    audio.crossOrigin = 'anonymous'
    const src = ctx.createMediaElementSource(audio)
    const master = ctx.createGain()
    master.gain.value = 0
    src.connect(master).connect(ctx.destination)
    const analyser = ctx.createAnalyser()
    analyser.fftSize = 1024
    analyser.smoothingTimeConstant = 0.6
    src.connect(analyser)
    this.ctx = ctx
    this.audio = audio
    this.master = master
    this.analyser = analyser
    this.bins = new Uint8Array(analyser.frequencyBinCount)
  }

  private volume() {
    const phone = typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches
    // soft background level: a mastered song is loud, so keep it well under full volume
    return phone ? 0.14 : 0.18
  }

  private fade(to: number, secs: number) {
    if (!this.ctx || !this.master) return
    const g = this.master.gain
    const t = this.ctx.currentTime
    g.cancelScheduledValues(t)
    g.setValueAtTime(g.value, t)
    g.linearRampToValueAtTime(to, t + secs)
  }

  /** start (from a click / tap / key: browsers need that) */
  start() {
    this.build()
    const ctx = this.ctx!
    if (ctx.state === 'suspended') void ctx.resume()
    if (this.playing) return
    this.playing = true
    this.startedAt = performance.now()
    if (this.stopTimer !== null) {
      clearTimeout(this.stopTimer)
      this.stopTimer = null
    }
    void this.audio!.play().catch(() => {
      // blocked (no user gesture yet): stay off until the next interaction
      this.playing = false
      this.emit()
    })
    this.fade(this.paused ? 0 : this.volume(), 2.5)
    if (this.raf === null) this.listen()
    this.emit()
  }

  stop() {
    if (!this.playing) return
    this.playing = false
    this.fade(0, 0.8)
    this.stopTimer = window.setTimeout(() => {
      this.stopTimer = null
      if (!this.playing) this.audio?.pause()
    }, 900)
    this.emit()
  }

  /** the visitor's own on/off (button or boombox): remembered */
  toggle() {
    // the same click that just auto-started the music (e.g. the first click was on the
    // boombox) shouldn't immediately switch it off again
    if (this.playing && performance.now() - this.startedAt < 600) return
    if (this.playing) {
      this.muted = true
      this.stop()
    } else {
      this.muted = false
      this.start()
    }
    try {
      localStorage.setItem(STORE, this.muted ? '1' : '0')
    } catch {}
  }

  /** soft pause while the tab is hidden or the office is scrolled away */
  setPaused(p: boolean) {
    if (this.paused === p) return
    this.paused = p
    if (this.playing) this.fade(p ? 0 : this.volume(), p ? 0.6 : 1.5)
  }

  // ------------------------------------------------- kick detection for the boombox pulse
  private listen() {
    const tick = () => {
      if (!this.playing) {
        this.raf = null
        return
      }
      this.raf = requestAnimationFrame(tick)
      if (this.paused) return
      const a = this.analyser!
      const b = this.bins!
      a.getByteFrequencyData(b)
      // ~0–150 Hz: the kick / bass
      const hzPerBin = this.ctx!.sampleRate / a.fftSize
      const n = Math.max(2, Math.round(150 / hzPerBin))
      let e = 0
      for (let i = 1; i <= n; i++) e += b[i]
      e /= n
      const now = performance.now()
      if (e > 120 && e > this.avg * 1.18 && now - this.lastBeat > 280) {
        this.lastBeat = now
        this.emit(this.beats++)
      }
      this.avg = this.avg * 0.92 + e * 0.08
    }
    this.raf = requestAnimationFrame(tick)
  }
}

export const music = new Music()
