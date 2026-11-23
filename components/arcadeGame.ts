// The Lab arcade cabinet, drawn into a <canvas> that the 3D screen uses as a texture.
//
//   title  → "WHAT I BUILD · PRESS START"
//   select → pick one of the four What We Build entries (or the bonus game)
//   chosen → the pick flashes, then onSelect(i) fires and the Lab page opens its info panel
//   play / over → the bonus catch-the-blocks game (Esc goes back to the select screen)

type Item = { x: number; y: number; vy: number; bad: boolean }
type State = 'title' | 'select' | 'chosen' | 'play' | 'over'

export type ArcadeTile = { title: string; color: string; icon: 'landing' | 'business' | 'store' | 'app' }

const ORANGE = '#ff7a1a'
const RED = '#ff2a3d'
const DIM = '#5a2a10'
const INK = '#ffe7d1'
const BONUS = 4 // index of the bonus tile (after the four services)

// tile layout on the 512 x 400 screen: 2 x 2 services + a wide bonus bar
const TILES = [
  { x: 18, y: 58, w: 232, h: 122 },
  { x: 262, y: 58, w: 232, h: 122 },
  { x: 18, y: 190, w: 232, h: 122 },
  { x: 262, y: 190, w: 232, h: 122 },
  { x: 18, y: 322, w: 476, h: 42 },
]

export class ArcadeGame {
  /** fired once the chosen tile has flashed: the Lab page opens the info panel */
  onSelect: (index: number) => void = () => {}

  private ctx: CanvasRenderingContext2D
  private w: number
  private h: number
  private state: State = 'title'
  private t = 0
  private cursor = 0
  private chosenAt = 0
  private chosen = -1
  private px = 0
  private score = 0
  private best = 0
  private lives = 3
  private items: Item[] = []
  private spawnIn = 0
  private left = false
  private right = false
  private active = false

  constructor(canvas: HTMLCanvasElement, private tiles: ArcadeTile[]) {
    this.ctx = canvas.getContext('2d')!
    this.w = canvas.width
    this.h = canvas.height
    this.px = this.w / 2
  }

  /** active = the camera is zoomed in on the cabinet and keys go to it */
  setActive(active: boolean) {
    if (this.active === active) return
    this.active = active
    if (!active) {
      this.state = 'title'
      this.items = []
      this.chosen = -1
      this.left = this.right = false
    }
  }

  /** the info panel was closed: back to picking */
  backToSelect() {
    this.state = 'select'
    this.chosen = -1
  }

  /** returns true when the key was used (so Esc doesn't also leave the Lab) */
  key(code: string, down: boolean): boolean {
    const L = code === 'ArrowLeft' || code === 'KeyA'
    const R = code === 'ArrowRight' || code === 'KeyD'
    const U = code === 'ArrowUp' || code === 'KeyW'
    const D = code === 'ArrowDown' || code === 'KeyS'
    const go = code === 'Space' || code === 'Enter'
    const esc = code === 'Escape'

    if (this.state === 'play' || this.state === 'over') {
      if (L) this.left = down
      if (R) this.right = down
      if (!down) return L || R
      if (esc) {
        this.backToSelect()
        return true
      }
      if (go && this.state === 'over') this.startGame()
      return L || R || go
    }
    if (!down) return false

    if (this.state === 'title') {
      if (go || L || R || U || D) {
        this.state = 'select'
        return true
      }
      return false
    }
    if (this.state === 'select') {
      const c = this.cursor
      if (L) this.cursor = (c + 4) % 5
      else if (R) this.cursor = (c + 1) % 5
      else if (U) this.cursor = c === BONUS ? 2 : c >= 2 ? c - 2 : BONUS
      else if (D) this.cursor = c === BONUS ? 0 : c < 2 ? c + 2 : BONUS
      else if (go) this.choose(this.cursor)
      else if (esc) {
        this.state = 'title'
        return true
      } else return false
      return true
    }
    return false // 'chosen': the Lab page owns Esc while the panel is open
  }

  /** a click/tap on the screen, in canvas pixels */
  click(x: number, y: number) {
    if (this.state === 'title') {
      this.state = 'select'
      return
    }
    if (this.state === 'over') {
      this.startGame()
      return
    }
    if (this.state !== 'select') return
    const i = TILES.findIndex((r) => x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h)
    if (i >= 0) {
      this.cursor = i
      this.choose(i)
    }
  }

  private choose(i: number) {
    this.chosen = i
    this.chosenAt = this.t
    this.state = 'chosen'
  }

  private startGame() {
    this.state = 'play'
    this.score = 0
    this.lives = 3
    this.items = []
    this.px = this.w / 2
    this.spawnIn = 0.5
  }

  update(dt: number) {
    dt = Math.min(dt, 0.05)
    this.t += dt

    if (this.state === 'chosen' && this.t - this.chosenAt > 0.45 && this.chosenAt >= 0) {
      if (this.chosen === BONUS) this.startGame()
      else this.onSelect(this.chosen)
      this.chosenAt = -1 // fire once
    }
    if (this.state !== 'play') return

    const speed = 420
    if (this.left) this.px -= speed * dt
    if (this.right) this.px += speed * dt
    this.px = Math.max(40, Math.min(this.w - 40, this.px))

    this.spawnIn -= dt
    if (this.spawnIn <= 0) {
      this.spawnIn = Math.max(0.28, 0.9 - this.score * 0.02)
      this.items.push({
        x: 20 + Math.random() * (this.w - 40),
        y: -20,
        vy: 120 + this.score * 6 + Math.random() * 60,
        bad: Math.random() < 0.3,
      })
    }

    const paddleY = this.h - 44
    this.items = this.items.filter((it) => {
      it.y += it.vy * dt
      const hit = it.y > paddleY - 12 && it.y < paddleY + 12 && Math.abs(it.x - this.px) < 46
      if (hit) {
        if (it.bad) this.lives--
        else this.score++
        return false
      }
      return it.y < this.h + 20
    })

    if (this.lives <= 0) {
      this.state = 'over'
      this.best = Math.max(this.best, this.score)
    }
  }

  draw() {
    const { ctx, w, h } = this
    ctx.fillStyle = '#07050d'
    ctx.fillRect(0, 0, w, h)
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'

    if (this.state === 'title') this.drawTitle()
    else if (this.state === 'select') this.drawSelect()
    else if (this.state === 'chosen') {
      if (this.chosen === BONUS || this.t - this.chosenAt < 0.45) this.drawSelect()
      else this.drawChosen()
    } else this.drawGame()

    // CRT scanlines + vignette
    ctx.fillStyle = 'rgba(0,0,0,0.25)'
    for (let y = 0; y < h; y += 4) ctx.fillRect(0, y, w, 2)
    const g = ctx.createRadialGradient(w / 2, h / 2, h * 0.3, w / 2, h / 2, w * 0.7)
    g.addColorStop(0, 'rgba(0,0,0,0)')
    g.addColorStop(1, 'rgba(0,0,0,0.65)')
    ctx.fillStyle = g
    ctx.fillRect(0, 0, w, h)
  }

  /* ---------- screens ---------- */

  private drawTitle() {
    const { w, h, t } = this
    // the four service icons drifting along the bottom
    this.tiles.forEach((tile, i) => {
      const x = ((t * 40 + i * (w / 4 + 30)) % (w + 120)) - 60
      this.icon(tile.icon, x, h * 0.8, 0.8, tile.color)
    })
    this.glowText('WHAT I', w / 2, h * 0.22, 50, '#22e4ff')
    this.glowText('BUILD', w / 2, h * 0.37, 50, '#ff4fd8')
    if (Math.floor(t * 2) % 2 === 0) {
      this.glowText(this.active ? 'PRESS START' : 'CLICK THE CABINET', w / 2, h * 0.55, 22, INK)
    }
  }

  private drawSelect() {
    const { ctx, w, t } = this
    this.glowText('SELECT YOUR BUILD', w / 2, 30, 24, INK)

    TILES.forEach((r, i) => {
      const on = i === this.cursor
      const flashing = this.state === 'chosen' && i === this.chosen
      const lit = flashing ? Math.floor(t * 14) % 2 === 0 : on
      const color = i === BONUS ? ORANGE : this.tiles[i].color
      ctx.save()
      ctx.fillStyle = lit ? hexA(color, 0.22) : 'rgba(255,255,255,0.04)'
      ctx.fillRect(r.x, r.y, r.w, r.h)
      ctx.strokeStyle = lit ? color : 'rgba(255,255,255,0.18)'
      ctx.lineWidth = lit ? 3 : 1.5
      if (lit) {
        ctx.shadowColor = color
        ctx.shadowBlur = 14
      }
      ctx.strokeRect(r.x + 1, r.y + 1, r.w - 2, r.h - 2)
      ctx.restore()

      if (i === BONUS) {
        this.glowText(on ? '▶  BONUS GAME  ◀' : 'BONUS GAME', r.x + r.w / 2, r.y + r.h / 2 + 1, 18, lit ? ORANGE : DIM)
        return
      }
      const tile = this.tiles[i]
      this.icon(tile.icon, r.x + r.w / 2, r.y + 50, 1, lit ? color : hexA(color, 0.55))
      this.glowText(tile.title.toUpperCase(), r.x + r.w / 2, r.y + r.h - 20, 17, lit ? INK : '#9a93a8')
      if (on && !flashing && Math.floor(t * 3) % 2 === 0) this.glowText('▶', r.x + 16, r.y + r.h - 20, 14, color)
    })
  }

  private drawChosen() {
    const { w, h, t } = this
    const tile = this.tiles[this.chosen]
    this.icon(tile.icon, w / 2, h * 0.36, 2, tile.color)
    this.glowText(tile.title.toUpperCase(), w / 2, h * 0.66, 30, INK)
    if (Math.floor(t * 2) % 2 === 0) this.glowText('ESC TO GO BACK', w / 2, h * 0.8, 16, tile.color)
  }

  private drawGame() {
    const { ctx, w, h } = this
    for (const it of this.items) this.block(it.x, it.y, it.bad ? RED : ORANGE)
    ctx.fillStyle = '#ffd2a8'
    ctx.shadowColor = ORANGE
    ctx.shadowBlur = 16
    ctx.fillRect(this.px - 40, h - 50, 80, 12)
    ctx.shadowBlur = 0
    ctx.textAlign = 'left'
    this.glowText(`SCORE ${this.score}`, 20, 26, 20, ORANGE)
    ctx.textAlign = 'right'
    this.glowText('■'.repeat(this.lives), w - 20, 26, 20, RED)
    ctx.textAlign = 'center'
    if (this.state === 'over') {
      ctx.fillStyle = 'rgba(0,0,0,0.6)'
      ctx.fillRect(0, 0, w, h)
      this.glowText('GAME OVER', w / 2, h * 0.38, 44, RED)
      this.glowText(`SCORE ${this.score}  ·  BEST ${this.best}`, w / 2, h * 0.52, 20, '#ffd2a8')
      this.glowText('SPACE TO RETRY', w / 2, h * 0.64, 18, ORANGE)
      this.glowText('ESC FOR MENU', w / 2, h * 0.73, 16, DIM)
    }
  }

  /* ---------- drawing helpers ---------- */

  /** little neon pixel icons for each kind of website, centred on (cx, cy) */
  private icon(kind: ArcadeTile['icon'], cx: number, cy: number, s: number, color: string) {
    const { ctx } = this
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.strokeStyle = color
    ctx.fillStyle = color
    ctx.lineWidth = 3
    ctx.shadowColor = color
    ctx.shadowBlur = 10
    if (kind === 'landing') {
      // browser window: bar, big headline block, button
      ctx.strokeRect(-34, -26, 68, 52)
      ctx.fillRect(-34, -26, 68, 8)
      ctx.fillRect(-24, -10, 34, 6)
      ctx.fillRect(-24, 0, 24, 4)
      ctx.fillRect(-24, 11, 18, 7)
      ctx.globalAlpha = 0.6
      ctx.fillRect(12, -8, 14, 22)
    } else if (kind === 'business') {
      // shop front: roof, windows, door
      ctx.strokeRect(-30, -18, 60, 44)
      ctx.beginPath()
      ctx.moveTo(-36, -18)
      ctx.lineTo(0, -32)
      ctx.lineTo(36, -18)
      ctx.stroke()
      ctx.fillRect(-22, -8, 12, 10)
      ctx.fillRect(10, -8, 12, 10)
      ctx.fillRect(-6, 8, 12, 18)
    } else if (kind === 'store') {
      // shopping bag
      ctx.strokeRect(-26, -12, 52, 40)
      ctx.beginPath()
      ctx.arc(0, -12, 13, Math.PI, 0)
      ctx.stroke()
      ctx.fillRect(-26, -12, 52, 6)
      ctx.fillRect(-4, 6, 8, 8)
    } else {
      // dashboard: frame, sidebar, bar chart
      ctx.strokeRect(-34, -26, 68, 52)
      ctx.fillRect(-34, -26, 14, 52)
      ctx.fillRect(-12, 6, 8, 14)
      ctx.fillRect(0, -4, 8, 24)
      ctx.fillRect(12, -14, 8, 34)
    }
    ctx.restore()
  }

  private block(x: number, y: number, color: string) {
    const { ctx } = this
    ctx.fillStyle = color
    ctx.shadowColor = color
    ctx.shadowBlur = 12
    ctx.fillRect(x - 9, y - 9, 18, 18)
    ctx.shadowBlur = 0
  }

  private glowText(text: string, x: number, y: number, size: number, color: string) {
    const { ctx } = this
    ctx.font = `bold ${size}px ui-monospace, Consolas, monospace`
    ctx.fillStyle = color
    ctx.shadowColor = color
    ctx.shadowBlur = 10
    ctx.fillText(text, x, y)
    ctx.shadowBlur = 0
  }
}

function hexA(hex: string, a: number) {
  const n = parseInt(hex.slice(1), 16)
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`
}
