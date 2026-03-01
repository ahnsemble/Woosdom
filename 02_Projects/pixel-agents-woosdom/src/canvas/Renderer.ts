import { TILE_SIZE, DEFAULT_ZOOM, SITTING_OFFSET_PX, VOID_TILE_COLOR } from '../constants.ts'
import { TileType, CharacterState, DIRECTION_TO_SPRITE_ROW, WALK_FRAME_SEQUENCE, BUBBLE_TEXT, BUBBLE_FADE_SEC } from './types.ts'
import type { Character, FurniturePlacement } from './types.ts'
import { getOfficeDimensions } from './OfficeLayout.ts'
import { getLayoutSync, getFloorColor, getFloorTileRef } from '../config/LayoutLoader.ts'

const WALL_COLOR = '#e8e0d4'
const WALL_BORDER_COLOR = '#8a7e70'
const SPEECH_BUBBLE_MAX_WIDTH = 200
const SPEECH_BUBBLE_ELLIPSIS = '...'

export interface RenderState {
  tileGrid: TileType[][]
  furniture: FurniturePlacement[]
  characters: Character[]
  tilesets: HTMLImageElement[]
  spritesImg: HTMLImageElement | null
  zoom: number
  cameraX: number
  cameraY: number
}

export function createRenderState(): RenderState {
  return {
    tileGrid: [],
    furniture: [],
    characters: [],
    tilesets: [],
    spritesImg: null,
    zoom: DEFAULT_ZOOM,
    cameraX: 0,
    cameraY: 0,
  }
}

export function renderFrame(ctx: CanvasRenderingContext2D, state: RenderState, isCustomize = false): void {
  const { zoom, cameraX, cameraY } = state
  const canvasW = ctx.canvas.width
  const canvasH = ctx.canvas.height

  // Clear
  ctx.fillStyle = VOID_TILE_COLOR
  ctx.fillRect(0, 0, canvasW, canvasH)

  ctx.save()
  ctx.translate(-cameraX, -cameraY)
  ctx.scale(zoom, zoom)

  // 1. Draw floor tiles
  renderFloors(ctx, state)

  // 2. Draw walls
  renderWalls(ctx, state)

  // 3. Draw furniture + characters combined (Y-sorted for correct overlap)
  renderFurnitureAndCharacters(ctx, state)

  // 4. Draw overlays (name labels + speech bubbles, always on top)
  renderCharacterOverlays(ctx, state)

  // 5. Draw room labels
  renderRoomLabels(ctx)

  // 6. Grid overlay for customize mode
  if (isCustomize) {
    renderGridOverlay(ctx)
    renderSeatMarkers(ctx, state)
  }

  ctx.restore()
}

function renderFloors(ctx: CanvasRenderingContext2D, state: RenderState): void {
  const { tileGrid, tilesets } = state
  const { rows, cols } = getOfficeDimensions()

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      if (tileGrid[row]?.[col] !== TileType.FLOOR) continue

      const x = col * TILE_SIZE
      const y = row * TILE_SIZE

      // Base color fill (backdrop for semi-transparent tiles)
      ctx.fillStyle = getFloorColor(col, row)
      ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE)

      // Tileset tile on top
      const ref = getFloorTileRef(col, row)
      const tileImg = tilesets[ref.tilesetIdx ?? 0]
      if (tileImg) {
        ctx.drawImage(
          tileImg,
          ref.sx * TILE_SIZE, ref.sy * TILE_SIZE, TILE_SIZE, TILE_SIZE,
          x, y, TILE_SIZE, TILE_SIZE,
        )
      }
    }
  }
}

function renderWalls(ctx: CanvasRenderingContext2D, state: RenderState): void {
  const { tileGrid, tilesets } = state
  const { rows, cols } = getOfficeDimensions()

  // Get wall tiles + overrides from layout config
  let wallTiles: Array<{ sx: number; sy: number; tilesetIdx?: number }> = []
  let tileOverrides: Record<string, { sx: number; sy: number; tilesetIdx?: number }> | undefined
  try {
    const layout = getLayoutSync()
    wallTiles = layout.wallTiles.tiles
    tileOverrides = layout.tileOverrides
  } catch {
    // fallback
  }

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      if (tileGrid[row]?.[col] !== TileType.WALL) continue

      const x = col * TILE_SIZE
      const y = row * TILE_SIZE

      // Base color fill (fallback under tile)
      ctx.fillStyle = WALL_COLOR
      ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE)

      // Check per-tile override first, then fall back to pattern
      const override = tileOverrides?.[`${col},${row}`]
      const ref = override ?? (wallTiles.length > 0 ? wallTiles[(col + row) % wallTiles.length] : null)

      if (ref) {
        const tileImg = tilesets[ref.tilesetIdx ?? 0]
        if (tileImg) {
          ctx.drawImage(
            tileImg,
            ref.sx * TILE_SIZE, ref.sy * TILE_SIZE, TILE_SIZE, TILE_SIZE,
            x, y, TILE_SIZE, TILE_SIZE,
          )
        } else {
          ctx.strokeStyle = WALL_BORDER_COLOR
          ctx.lineWidth = 0.5
          ctx.strokeRect(x + 0.5, y + 0.5, TILE_SIZE - 1, TILE_SIZE - 1)
        }
      } else {
        ctx.strokeStyle = WALL_BORDER_COLOR
        ctx.lineWidth = 0.5
        ctx.strokeRect(x + 0.5, y + 0.5, TILE_SIZE - 1, TILE_SIZE - 1)
      }
    }
  }
}

/** Unified drawable for Y-sorted rendering */
interface Drawable {
  zY: number  // sort key: bottom-edge Y in world coordinates
  type: 'furniture' | 'character'
  furniture?: FurniturePlacement
  character?: Character
}

/** Combined furniture + character rendering with Y-sort for correct overlap */
function renderFurnitureAndCharacters(ctx: CanvasRenderingContext2D, state: RenderState): void {
  const { furniture, characters, tilesets, spritesImg } = state

  // Collect all drawables
  const drawables: Drawable[] = []

  // Furniture tiles: sort by bottom edge
  if (tilesets.length > 0) {
    for (const f of furniture) {
      const sh = f.tile.sh ?? 1
      drawables.push({
        zY: (f.row + sh) * TILE_SIZE,
        type: 'furniture',
        furniture: f,
      })
    }
  }

  // Characters: sort by feet position (character y is at tile center)
  if (spritesImg) {
    for (const ch of characters) {
      // If sitting, forcefully push their Z sorting down by 1 tile so they appear on top of tall chairs
      const sitBoost = ch.state === CharacterState.TYPE ? TILE_SIZE : 0
      drawables.push({
        zY: ch.y + TILE_SIZE / 2 + sitBoost,
        type: 'character',
        character: ch,
      })
    }
  }

  // Sort ascending by Y (back-to-front). If Y is equal, draw character on top of furniture
  drawables.sort((a, b) => {
    if (a.zY === b.zY) return a.type === 'character' ? 1 : -1
    return a.zY - b.zY
  })

  // Sprite block dimensions (RPG Maker VX format)
  const SPRITE_W = 32
  const SPRITE_H = 32
  const BLOCK_W = 96   // 3 frames × 32px
  const BLOCK_H = 128  // 4 directions × 32px

  for (const d of drawables) {
    if (d.type === 'furniture' && d.furniture) {
      const f = d.furniture
      const tileImg = tilesets[f.tile.tilesetIdx ?? 0]
      if (!tileImg) continue
      const sw = f.tile.sw ?? 1
      const sh = f.tile.sh ?? 1
      const isVxTile = (f.tile.tilesetIdx ?? 0) >= 2

      if (isVxTile && (sw > 1 || sh > 1)) {
        // VX multi-tile: compress oversized source into single 16×16 grid cell.
        // Each FurniturePlacement is already decomposed per-tile by createFurniturePlacements(),
        // so sw/sh here refers to the source region in the tileset, not destination span.
        ctx.drawImage(
          tileImg,
          f.tile.sx * TILE_SIZE, f.tile.sy * TILE_SIZE,
          sw * TILE_SIZE, sh * TILE_SIZE,
          f.col * TILE_SIZE, f.row * TILE_SIZE,
          TILE_SIZE, TILE_SIZE,
        )
      } else {
        ctx.drawImage(
          tileImg,
          f.tile.sx * TILE_SIZE, f.tile.sy * TILE_SIZE,
          sw * TILE_SIZE, sh * TILE_SIZE,
          f.col * TILE_SIZE, f.row * TILE_SIZE,
          sw * TILE_SIZE, sh * TILE_SIZE,
        )
      }
    } else if (d.type === 'character' && d.character && spritesImg) {
      const ch = d.character
      const blockX = ch.spriteCol * BLOCK_W
      const blockY = ch.spriteRow * BLOCK_H

      let frameCol: number
      if (ch.state === CharacterState.WALK) {
        frameCol = WALK_FRAME_SEQUENCE[ch.frame % 4]
      } else if (ch.state === CharacterState.TYPE) {
        frameCol = ch.frame % 2 === 0 ? 1 : 2
      } else {
        frameCol = 0
      }

      const dirRow = DIRECTION_TO_SPRITE_ROW[ch.dir]
      const srcX = blockX + frameCol * SPRITE_W
      const srcY = blockY + dirRow * SPRITE_H

      const sittingOffset = ch.state === CharacterState.TYPE ? SITTING_OFFSET_PX : 0
      const drawX = ch.x - SPRITE_W / 2
      const drawY = ch.y - SPRITE_H + 4 + sittingOffset

      ctx.drawImage(
        spritesImg,
        srcX, srcY, SPRITE_W, SPRITE_H,
        drawX, drawY, SPRITE_W, SPRITE_H,
      )
    }
  }
}

/** Render name labels + speech bubbles as overlays (always on top of all sprites) */
function renderCharacterOverlays(ctx: CanvasRenderingContext2D, state: RenderState): void {
  const SPRITE_H = 32

  for (const ch of state.characters) {
    const sittingOffset = ch.state === CharacterState.TYPE ? SITTING_OFFSET_PX : 0
    const drawY = ch.y - SPRITE_H + 4 + sittingOffset

    // Name label (above head)
    const nameY = drawY - 1
    ctx.font = '4px monospace'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'bottom'
    const textWidth = ctx.measureText(ch.displayName).width
    ctx.fillStyle = 'rgba(0,0,0,0.5)'
    ctx.fillRect(ch.x - textWidth / 2 - 1, nameY - 5, textWidth + 2, 6)
    ctx.fillStyle = '#fff'
    ctx.fillText(ch.displayName, ch.x, nameY)

    // Speech bubble (above name label)
    if (ch.bubbleType) {
      const text = BUBBLE_TEXT[ch.bubbleType] ?? ch.bubbleType
      let alpha = 1.0
      if (ch.bubbleTimer < BUBBLE_FADE_SEC) {
        alpha = Math.max(0, ch.bubbleTimer / BUBBLE_FADE_SEC)
      }
      if (alpha > 0) {
        renderSpeechBubble(ctx, ch.x, nameY - 6, text, alpha, ch.bubbleType === 'error')
      }
    }
  }
}

function truncateSpeechBubbleText(ctx: CanvasRenderingContext2D, text: string): string {
  if (ctx.measureText(text).width <= SPEECH_BUBBLE_MAX_WIDTH) return text

  const ellipsisWidth = ctx.measureText(SPEECH_BUBBLE_ELLIPSIS).width
  if (ellipsisWidth >= SPEECH_BUBBLE_MAX_WIDTH) return SPEECH_BUBBLE_ELLIPSIS

  let low = 0
  let high = text.length

  while (low < high) {
    const mid = Math.ceil((low + high) / 2)
    const candidate = `${text.slice(0, mid)}${SPEECH_BUBBLE_ELLIPSIS}`
    if (ctx.measureText(candidate).width <= SPEECH_BUBBLE_MAX_WIDTH) {
      low = mid
    } else {
      high = mid - 1
    }
  }

  return `${text.slice(0, low)}${SPEECH_BUBBLE_ELLIPSIS}`
}

function renderSpeechBubble(
  ctx: CanvasRenderingContext2D,
  x: number, y: number,
  text: string, alpha: number,
  isError: boolean,
): void {
  ctx.save()
  if (alpha < 1) ctx.globalAlpha = alpha

  ctx.font = '5px monospace'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  const displayText = truncateSpeechBubbleText(ctx, text)
  const metrics = ctx.measureText(displayText)
  const padX = 3
  const padY = 2
  const textW = metrics.width
  const textH = 5
  const bubbleW = textW + padX * 2
  const bubbleH = textH + padY * 2
  const tailH = 3
  const bx = x - bubbleW / 2
  const by = y - bubbleH - tailH
  const r = 2

  // Rounded rect background
  ctx.fillStyle = isError ? '#ffe0e0' : '#fff'
  ctx.beginPath()
  ctx.moveTo(bx + r, by)
  ctx.lineTo(bx + bubbleW - r, by)
  ctx.quadraticCurveTo(bx + bubbleW, by, bx + bubbleW, by + r)
  ctx.lineTo(bx + bubbleW, by + bubbleH - r)
  ctx.quadraticCurveTo(bx + bubbleW, by + bubbleH, bx + bubbleW - r, by + bubbleH)
  ctx.lineTo(bx + r, by + bubbleH)
  ctx.quadraticCurveTo(bx, by + bubbleH, bx, by + bubbleH - r)
  ctx.lineTo(bx, by + r)
  ctx.quadraticCurveTo(bx, by, bx + r, by)
  ctx.closePath()
  ctx.fill()

  // Border
  ctx.strokeStyle = isError ? '#c62828' : '#333'
  ctx.lineWidth = 0.5
  ctx.stroke()

  // Triangle tail
  ctx.fillStyle = isError ? '#ffe0e0' : '#fff'
  ctx.beginPath()
  ctx.moveTo(x - 2, by + bubbleH)
  ctx.lineTo(x, by + bubbleH + tailH)
  ctx.lineTo(x + 2, by + bubbleH)
  ctx.closePath()
  ctx.fill()
  ctx.beginPath()
  ctx.moveTo(x - 2, by + bubbleH)
  ctx.lineTo(x, by + bubbleH + tailH)
  ctx.lineTo(x + 2, by + bubbleH)
  ctx.strokeStyle = isError ? '#c62828' : '#333'
  ctx.stroke()

  // Text
  ctx.fillStyle = isError ? '#c62828' : '#333'
  ctx.fillText(displayText, x, by + bubbleH / 2)

  ctx.restore()
}

function renderRoomLabels(ctx: CanvasRenderingContext2D): void {
  ctx.font = 'bold 6px monospace'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'top'
  ctx.fillStyle = '#555'

  try {
    const layout = getLayoutSync()
    for (const room of layout.rooms) {
      const cx = ((room.minCol + room.maxCol) / 2) * TILE_SIZE
      const ty = room.minRow * TILE_SIZE + 2
      ctx.fillText(room.label, cx, ty)
    }
  } catch {
    // layout not loaded yet
  }
}

function renderGridOverlay(ctx: CanvasRenderingContext2D): void {
  const { cols, rows } = getOfficeDimensions()
  ctx.save()
  ctx.strokeStyle = 'rgba(255,255,255,0.15)'
  ctx.lineWidth = 0.5

  // Vertical lines
  for (let c = 0; c <= cols; c++) {
    ctx.beginPath()
    ctx.moveTo(c * TILE_SIZE, 0)
    ctx.lineTo(c * TILE_SIZE, rows * TILE_SIZE)
    ctx.stroke()
  }
  // Horizontal lines
  for (let r = 0; r <= rows; r++) {
    ctx.beginPath()
    ctx.moveTo(0, r * TILE_SIZE)
    ctx.lineTo(cols * TILE_SIZE, r * TILE_SIZE)
    ctx.stroke()
  }
  ctx.restore()
}

function renderSeatMarkers(ctx: CanvasRenderingContext2D, state: RenderState): void {
  try {
    const layout = getLayoutSync()
    for (const seat of layout.seats) {
      const cx = seat.seatCol * TILE_SIZE + TILE_SIZE / 2
      const cy = seat.seatRow * TILE_SIZE + TILE_SIZE / 2

      // Transparent circle
      ctx.fillStyle = 'rgba(76, 175, 80, 0.4)'
      ctx.beginPath()
      ctx.arc(cx, cy, TILE_SIZE * 0.4, 0, Math.PI * 2)
      ctx.fill()
      ctx.lineWidth = 1
      ctx.strokeStyle = 'rgba(76, 175, 80, 0.8)'
      ctx.stroke()

      // Facing arrow
      ctx.save()
      ctx.translate(cx, cy)
      // facingDir: 0=DOWN, 1=UP, 2=RIGHT, 3=LEFT
      let angle = 0
      if (seat.facingDir === 0) angle = Math.PI / 2
      else if (seat.facingDir === 1) angle = -Math.PI / 2
      else if (seat.facingDir === 2) angle = 0
      else if (seat.facingDir === 3) angle = Math.PI

      ctx.rotate(angle)
      ctx.fillStyle = 'white'
      ctx.beginPath()
      ctx.moveTo(4, 0)
      ctx.lineTo(-2, 3)
      ctx.lineTo(-2, -3)
      ctx.closePath()
      ctx.fill()
      ctx.restore()

      // Label
      const char = state.characters.find(c => c.seatId === seat.id)
      const label = char ? char.displayName : seat.id
      ctx.font = '5px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      // draw text outline
      ctx.lineWidth = 1.5
      ctx.strokeStyle = 'rgba(0,0,0,0.8)'
      ctx.strokeText(label, cx, cy - TILE_SIZE * 0.6)
      ctx.fillStyle = 'white'
      ctx.fillText(label, cx, cy - TILE_SIZE * 0.6)
    }
  } catch {
    // layout not ready
  }
}

/** Center camera on the office */
export function centerCamera(
  canvasWidth: number, canvasHeight: number, zoom: number,
): { cameraX: number; cameraY: number } {
  const { cols, rows } = getOfficeDimensions()
  const officeW = cols * TILE_SIZE * zoom
  const officeH = rows * TILE_SIZE * zoom
  return {
    cameraX: (officeW - canvasWidth) / 2,
    cameraY: (officeH - canvasHeight) / 2,
  }
}
