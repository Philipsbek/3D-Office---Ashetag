'use client'

// An ORIGINAL lo-fi synthwave loop played live with the Web Audio API (nothing to download):
// warm detuned pads over Am – F – C – G, a soft sub bass, a gentle four-on-the-floor kick,
// off-beat hats and a delayed arpeggio. ~92 BPM, 8-bar loop.
//
// Browsers only allow sound after the visitor interacts with the page, so music starts on
// the first click/tap/key (unless they muted it before). `music.on(...)` reports state and
// beats (the boombox pulses on them).

type Listener = (e: { playing: boolean; beat?: number }) => void

const BPM = 92
const BEAT = 60 / BPM
const CHORDS = [
  [57, 60, 64], // A minor
  [53, 57, 60], // F
  [48, 52, 55], // C
  [55, 59, 62], // G
]
const ARP = [0, 1, 2, 1, 2, 0, 1, 2]
const hz = (m: number) => 440 * Math.pow(2, (m - 69) / 12)
const STORE = 'pb-music-muted'

class Music {
  private ctx: AudioContext | null = null
  private master: GainNode | null = null
  private delay: DelayNode | null = null
  private timer: number | null = null
  private nextTime = 0
  private step = 0 // 8th-note steps
  private listeners = new Set<Listener>()
  playing = false
  private startedAt = 0
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
    const master = ctx.createGain()
    master.gain.value = 0
    const comp = ctx.createDynamicsCompressor()
    master.connect(comp).connect(ctx.destination)
    // shared echo for the arpeggio
    const delay = ctx.createDelay(1)
    delay.delayTime.value = BEAT * 0.75
    const fb = ctx.createGain()
    fb.gain.value = 0.32
    const wet = ctx.createGain()
    wet.gain.value = 0.35
    delay.connect(fb).connect(delay)
    delay.connect(wet).connect(master)
    this.ctx = ctx
    this.master = master
    this.delay = delay
  }

  private volume() {
    const phone = typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches
    return phone ? 0.16 : 0.22
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
    this.nextTime = ctx.currentTime + 0.1
    this.fade(this.paused ? 0 : this.volume(), 2.5)
    if (this.timer === null) this.timer = window.setInterval(() => this.schedule(), 25)
    this.emit()
  }

  stop() {
    if (!this.playing) return
    this.playing = false
    this.fade(0, 0.8)
    window.setTimeout(() => {
      if (!this.playing && this.timer !== null) {
        clearInterval(this.timer)
        this.timer = null
      }
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

  // ---------------------------------------------------------------- the song
  private schedule() {
    const ctx = this.ctx!
    while (this.nextTime < ctx.currentTime + 0.12) {
      this.playStep(this.step, this.nextTime)
      this.nextTime += BEAT / 2
      this.step = (this.step + 1) % 64 // 8 bars of 8 eighths
    }
  }

  private playStep(s: number, t: number) {
    const bar = Math.floor(s / 8)
    const chord = CHORDS[bar % 4]
    const e = s % 8 // eighth inside the bar
    if (e === 0) this.pad(chord, t, BEAT * 4)
    if (e % 2 === 0) {
      this.kick(t)
      this.bass(chord[0] - 24, t, BEAT * 0.9)
      const beat = s / 2
      const delayMs = Math.max(0, (t - this.ctx!.currentTime) * 1000)
      window.setTimeout(() => this.emit(beat), delayMs)
    } else this.hat(t)
    if (bar >= 2) this.arp(chord[ARP[e]] + 12, t, BEAT * 0.45)
  }

  private env(g: GainNode, t: number, a: number, peak: number, d: number) {
    g.gain.setValueAtTime(0.0001, t)
    g.gain.exponentialRampToValueAtTime(peak, t + a)
    g.gain.exponentialRampToValueAtTime(0.0001, t + a + d)
  }

  private pad(notes: number[], t: number, len: number) {
    const ctx = this.ctx!
    const lp = ctx.createBiquadFilter()
    lp.type = 'lowpass'
    lp.frequency.setValueAtTime(700, t)
    lp.frequency.linearRampToValueAtTime(1600, t + len * 0.5)
    lp.frequency.linearRampToValueAtTime(800, t + len)
    const g = ctx.createGain()
    g.gain.setValueAtTime(0.0001, t)
    g.gain.exponentialRampToValueAtTime(0.11, t + 0.6)
    g.gain.setValueAtTime(0.11, t + len - 0.4)
    g.gain.exponentialRampToValueAtTime(0.0001, t + len + 0.3)
    lp.connect(g).connect(this.master!)
    for (const n of notes)
      for (const det of [-8, 8]) {
        const o = ctx.createOscillator()
        o.type = 'sawtooth'
        o.frequency.value = hz(n)
        o.detune.value = det
        o.connect(lp)
        o.start(t)
        o.stop(t + len + 0.4)
      }
  }

  private bass(n: number, t: number, len: number) {
    const ctx = this.ctx!
    const o = ctx.createOscillator()
    o.type = 'triangle'
    o.frequency.value = hz(n)
    const g = ctx.createGain()
    this.env(g, t, 0.02, 0.22, len)
    o.connect(g).connect(this.master!)
    o.start(t)
    o.stop(t + len + 0.1)
  }

  private kick(t: number) {
    const ctx = this.ctx!
    const o = ctx.createOscillator()
    o.frequency.setValueAtTime(120, t)
    o.frequency.exponentialRampToValueAtTime(42, t + 0.18)
    const g = ctx.createGain()
    this.env(g, t, 0.005, 0.5, 0.28)
    o.connect(g).connect(this.master!)
    o.start(t)
    o.stop(t + 0.35)
  }

  private noise: AudioBuffer | null = null
  private hat(t: number) {
    const ctx = this.ctx!
    if (!this.noise) {
      this.noise = ctx.createBuffer(1, ctx.sampleRate * 0.2, ctx.sampleRate)
      const d = this.noise.getChannelData(0)
      for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1
    }
    const src = ctx.createBufferSource()
    src.buffer = this.noise
    const hp = ctx.createBiquadFilter()
    hp.type = 'highpass'
    hp.frequency.value = 7000
    const g = ctx.createGain()
    this.env(g, t, 0.003, 0.06, 0.05)
    src.connect(hp).connect(g).connect(this.master!)
    src.start(t)
    src.stop(t + 0.1)
  }

  private arp(n: number, t: number, len: number) {
    const ctx = this.ctx!
    const o = ctx.createOscillator()
    o.type = 'square'
    o.frequency.value = hz(n)
    const lp = ctx.createBiquadFilter()
    lp.type = 'lowpass'
    lp.frequency.value = 2200
    const g = ctx.createGain()
    this.env(g, t, 0.01, 0.045, len)
    o.connect(lp).connect(g)
    g.connect(this.master!)
    g.connect(this.delay!)
    o.start(t)
    o.stop(t + len + 0.05)
  }
}

export const music = new Music()
