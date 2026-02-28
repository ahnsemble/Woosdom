import { useEffect, useRef } from 'react'
import { startGameLoop } from '../canvas/GameLoop.ts'
import {
  createTileGrid,
  createFurniturePlacements,
  createSeats,
  getBlockedTiles,
  initRooms,
  getOfficeDimensions,
} from '../canvas/OfficeLayout.ts'
import { createRenderState, renderFrame, centerCamera } from '../canvas/Renderer.ts'
import { createCharacter, updateCharacter } from '../canvas/Characters.ts'
import { findPath } from '../canvas/Pathfinding.ts'
import { initAgentDefinitions, AGENT_DEFINITIONS } from '../agents/AgentDefs.ts'
import { getWalkableTilesInRegion } from '../canvas/Pathfinding.ts'
import { TILE_SIZE } from '../constants.ts'
import { BUBBLE_FADE_SEC } from '../canvas/types.ts'
import type { Character, Seat } from '../canvas/types.ts'
import { loadLayout, getLayoutSync } from '../config/LayoutLoader.ts'
import { useAppContext } from '../contexts/AppContext.tsx'
import { EventLogStore } from '../state/EventLogStore.ts'
import { EVENT_EMOJI } from '../types/EventLog.ts'

interface ElectronAPI {
  sendReady: () => void
  readLayout: () => Promise<unknown>
  writeLayout: (data: unknown) => Promise<unknown>
  onVaultToHands: (cb: (data: { engine: string; targetRoom: string }) => void) => (() => void) | void
  onVaultFromHands: (cb: (data: { engine: string }) => void) => (() => void) | void
  onVaultToCodex: (cb: (data: Record<string, never>) => void) => (() => void) | void
  onVaultActiveContext: (cb: (data: Record<string, never>) => void) => (() => void) | void
  onAgentToolStart: (cb: (data: { agentRole: string; toolName: string }) => void) => (() => void) | void
  onAgentToolDone: (cb: (data: { agentRole: string }) => void) => (() => void) | void
  onAgentStatus: (cb: (data: { agentRole: string; status: string }) => void) => (() => void) | void
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI
  }
}

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

function findCharByRole(characters: Character[], role: string): Character | undefined {
  return characters.find(ch => ch.role === role)
}

function getDisplayName(characters: Character[], role: string): string {
  return characters.find(ch => ch.role === role)?.displayName ?? role
}

export default function OfficeCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const { setSelectedAgent, charactersRef, triggerPanelRefresh } = useAppContext()
  const renderStateRef = useRef<ReturnType<typeof createRenderState> | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    let aborted = false
    let cleanup: (() => void) | null = null
    const canvasEl = canvas

    async function init() {
      // 1. Load layout config
      await loadLayout()
      if (aborted) return  // StrictMode: first init aborted
      initRooms()
      initAgentDefinitions()
      const layout = getLayoutSync()

      // 2. Load assets
      const [spritesImg, ...loadedTilesets] = await Promise.all([
        loadImage(new URL('../assets/sprites.png', import.meta.url).href),
        loadImage(new URL('../assets/tileset.png', import.meta.url).href),
        loadImage(new URL('../assets/tileset2.png', import.meta.url).href).catch(() => null),
        loadImage(new URL('../assets/tilesets/vx_ace/A2 Office Floors.png', import.meta.url).href).catch(() => null),
        loadImage(new URL('../assets/tilesets/vx_ace/A4 Office Walls.png', import.meta.url).href).catch(() => null),
        loadImage(new URL('../assets/tilesets/vx_ace/A5 Office Floors & Walls.png', import.meta.url).href).catch(() => null),
        loadImage(new URL('../assets/tilesets/vx_ace/B-C-D-E Office 1 No Shadows.png', import.meta.url).href).catch(() => null),
        loadImage(new URL('../assets/tilesets/vx_ace/B-C-D-E Office 2 No Shadows.png', import.meta.url).href).catch(() => null),
      ])
      if (aborted) return  // StrictMode: first init aborted

      // 3. Create layout
      let tileGrid = createTileGrid()
      let furniture = createFurniturePlacements()
      const seatList = createSeats()
      let blockedTiles = getBlockedTiles(furniture)

      const seats = new Map<string, Seat>()
      for (const s of seatList) seats.set(s.id, s)

      const characters: Character[] = AGENT_DEFINITIONS.map(def => {
        const seat = seats.get(def.seatId) ?? null
        return createCharacter(def, seat)
      })
      charactersRef.current = characters

      // Pre-compute walkable tiles
      const roomWalkableTiles = new Map<string, Array<{ col: number; row: number }>>()
      for (const room of layout.rooms) {
        roomWalkableTiles.set(
          room.id,
          getWalkableTilesInRegion(room.minCol, room.maxCol, room.minRow, room.maxRow, tileGrid, blockedTiles),
        )
      }
      const allWalkable = getWalkableTilesInRegion(0, tileGrid[0].length - 1, 0, tileGrid.length - 1, tileGrid, blockedTiles)
      roomWalkableTiles.set('brain', allWalkable)

      console.log('codex walkable:', roomWalkableTiles.get('codex')?.length)

      // Render state
      const renderState = createRenderState()
      renderState.tileGrid = tileGrid
      renderState.furniture = furniture
      renderState.characters = characters
      renderState.tilesets = loadedTilesets.filter(Boolean) as HTMLImageElement[]
      renderState.spritesImg = spritesImg
      renderStateRef.current = renderState

        // Expose layout refresh for customize mode (editor updates layoutConfig,
        // but renderState.tileGrid / furniture need rebuilding)
        ; (window as unknown as Record<string, unknown>).__refreshLayout = () => {
          tileGrid = createTileGrid()
          furniture = createFurniturePlacements()
          blockedTiles = getBlockedTiles(furniture)

          renderState.tileGrid = tileGrid
          renderState.furniture = furniture

          // Re-compute walkable regions
          for (const room of getLayoutSync().rooms) {
            roomWalkableTiles.set(
              room.id,
              getWalkableTilesInRegion(room.minCol, room.maxCol, room.minRow, room.maxRow, tileGrid, blockedTiles),
            )
          }
          const allWalkable = getWalkableTilesInRegion(0, tileGrid[0].length - 1, 0, tileGrid.length - 1, tileGrid, blockedTiles)
          roomWalkableTiles.set('brain', allWalkable)

          console.log('codex walkable (refresh):', roomWalkableTiles.get('codex')?.length)
        }

      // Auto-fit zoom: calculate zoom level that fits entire office in viewport
      const getFitZoom = () => {
        const { cols, rows } = getOfficeDimensions()
        const w = canvasEl.parentElement?.clientWidth ?? window.innerWidth
        const h = canvasEl.parentElement?.clientHeight ?? window.innerHeight
        return Math.min(w / (cols * TILE_SIZE), h / (rows * TILE_SIZE))
      }

      // Set initial zoom to fit entire office
      renderState.zoom = getFitZoom()

      // Resize handler
      const resize = () => {
        const parent = canvasEl.parentElement
        if (parent) {
          canvasEl.width = parent.clientWidth
          canvasEl.height = parent.clientHeight
        } else {
          canvasEl.width = window.innerWidth
          canvasEl.height = window.innerHeight
        }
        const fitZoom = getFitZoom()
        if (renderState.zoom < fitZoom) {
          renderState.zoom = fitZoom
        }
        const camera = centerCamera(canvasEl.width, canvasEl.height, renderState.zoom)
        renderState.cameraX = camera.cameraX
        renderState.cameraY = camera.cameraY
      }
      resize()
      window.addEventListener('resize', resize)
      // Also observe parent element resize
      const resizeObserver = new ResizeObserver(resize)
      if (canvasEl.parentElement) resizeObserver.observe(canvasEl.parentElement)

      // Zoom
      const onWheel = (e: WheelEvent) => {
        e.preventDefault()
        const delta = e.deltaY > 0 ? -1 : 1
        const fitZoom = getFitZoom()
        renderState.zoom = Math.max(fitZoom, Math.min(8, renderState.zoom + delta))
        const camera = centerCamera(canvasEl.width, canvasEl.height, renderState.zoom)
        renderState.cameraX = camera.cameraX
        renderState.cameraY = camera.cameraY
      }
      canvasEl.addEventListener('wheel', onWheel, { passive: false })

      // Click → hit detection or editor action
      const onClick = (e: MouseEvent) => {
        const rect = canvasEl.getBoundingClientRect()
        const worldX = (e.clientX - rect.left + renderState.cameraX) / renderState.zoom
        const worldY = (e.clientY - rect.top + renderState.cameraY) / renderState.zoom

        // In customize mode, forward to editor
        const editorClick = (window as unknown as Record<string, unknown>).__editorTileClick as
          | ((col: number, row: number) => void)
          | undefined
        const isCustomize = (window as unknown as Record<string, unknown>).__customizeMode as boolean | undefined
        if (isCustomize && editorClick) {
          const col = Math.floor(worldX / TILE_SIZE)
          const row = Math.floor(worldY / TILE_SIZE)
          editorClick(col, row)
          return
        }

        // Check characters (reverse Y order for front-to-back)
        const sorted = [...characters].sort((a, b) => b.y - a.y)
        for (const ch of sorted) {
          const hitX = ch.x - TILE_SIZE
          const hitY = ch.y - TILE_SIZE * 2
          if (worldX >= hitX && worldX < hitX + TILE_SIZE * 2 &&
            worldY >= hitY && worldY < hitY + TILE_SIZE * 2) {
            setSelectedAgent(ch)
            return
          }
        }
        // Empty click → deselect
        setSelectedAgent(null)
      }
      canvasEl.addEventListener('click', onClick)

      // ---- IPC Event Handlers ----
      const api = window.electronAPI
      console.log('[Renderer] electronAPI available:', !!api)
      const rooms = layout.rooms
      const ipcCleanups: Array<() => void> = []

      function walkCharToRoom(ch: Character, targetRoom: string) {
        const room = rooms.find(r => r.id === targetRoom)
        if (!room) return
        const targetCol = Math.floor((room.minCol + room.maxCol) / 2)
        const targetRow = Math.floor((room.minRow + room.maxRow) / 2)
        const path = findPath(ch.tileCol, ch.tileRow, targetCol, targetRow, tileGrid, blockedTiles)
        if (path.length > 0) {
          ch.path = path
          ch.moveProgress = 0
          ch.state = 1
          ch.frame = 0
          ch.frameTimer = 0
          ch.isActive = false
        }
      }

      const unsub1 = api?.onVaultToHands((data) => {
        const brain = findCharByRole(characters, 'brain')
        if (brain) {
          brain.bubbleType = 'communicating'
          brain.bubbleTimer = 8
          walkCharToRoom(brain, data.targetRoom)
          EventLogStore.addEntry({
            agentRole: 'brain',
            agentDisplayName: 'Brain',
            emoji: EVENT_EMOJI.communicating,
            action: `to_hands.md dispatching to ${data.targetRoom}`,
          })
          triggerPanelRefresh()
        }
      })
      if (unsub1) ipcCleanups.push(unsub1)

      const unsub2 = api?.onVaultFromHands((data) => {
        let leadRole = 'foreman'
        if (data.engine === 'codex' || data.engine === 'claude_codex') leadRole = 'compute_lead'
        else if (data.engine === 'antigravity') leadRole = 'scout_lead'

        const lead = findCharByRole(characters, leadRole)
        if (lead) {
          lead.bubbleType = 'communicating'
          lead.bubbleTimer = 8
          walkCharToRoom(lead, 'brain')
          EventLogStore.addEntry({
            agentRole: leadRole,
            agentDisplayName: lead.displayName,
            emoji: EVENT_EMOJI.communicating,
            action: 'Reporting to Brain HQ',
          })
          triggerPanelRefresh()
        }
      })
      if (unsub2) ipcCleanups.push(unsub2)

      const unsub3 = api?.onVaultToCodex(() => {
        for (const ch of characters) {
          if (ch.team === 'codex') {
            ch.isActive = true
            ch.currentTool = 'Compute'
          }
        }
        EventLogStore.addEntry({
          agentRole: 'compute_lead',
          agentDisplayName: getDisplayName(characters, 'compute_lead'),
          emoji: EVENT_EMOJI.active,
          action: 'Codex team activated — compute task received',
        })
        triggerPanelRefresh()
      })
      if (unsub3) ipcCleanups.push(unsub3)

      const unsub4 = api?.onVaultActiveContext(() => {
        const brain = findCharByRole(characters, 'brain')
        if (brain) {
          brain.isActive = true
          brain.currentTool = 'Write'
          setTimeout(() => { brain.isActive = false; brain.currentTool = null }, 10_000)
          EventLogStore.addEntry({
            agentRole: 'brain',
            agentDisplayName: 'Brain',
            emoji: EVENT_EMOJI.active,
            action: 'Context updated — writing',
          })
          triggerPanelRefresh()
        }
      })
      if (unsub4) ipcCleanups.push(unsub4)

      const READING_TOOLS = new Set(['Read', 'Grep', 'Glob', 'WebFetch', 'WebSearch'])
      const unsub5 = api?.onAgentToolStart((data) => {
        const ch = findCharByRole(characters, data.agentRole)
        if (ch) {
          ch.isActive = true
          ch.currentTool = data.toolName
          ch.bubbleType = READING_TOOLS.has(data.toolName) ? 'reading' : 'typing'
          ch.bubbleTimer = 999
          EventLogStore.addEntry({
            agentRole: data.agentRole,
            agentDisplayName: ch.displayName,
            emoji: READING_TOOLS.has(data.toolName) ? EVENT_EMOJI.reading : EVENT_EMOJI.tool_start,
            action: `Using ${data.toolName}`,
          })
          triggerPanelRefresh()
        }
      })
      if (unsub5) ipcCleanups.push(unsub5)

      const unsub6 = api?.onAgentToolDone((data) => {
        const ch = findCharByRole(characters, data.agentRole)
        if (ch) {
          ch.currentTool = null
          ch.bubbleType = 'done'
          ch.bubbleTimer = 3
          EventLogStore.addEntry({
            agentRole: data.agentRole,
            agentDisplayName: ch.displayName,
            emoji: EVENT_EMOJI.tool_done,
            action: 'Tool completed',
          })
          triggerPanelRefresh()
        }
      })
      if (unsub6) ipcCleanups.push(unsub6)

      const unsub7 = api?.onAgentStatus((data) => {
        const ch = findCharByRole(characters, data.agentRole)
        if (ch) {
          if (data.status === 'idle') {
            ch.isActive = false
            ch.currentTool = null
            if (ch.bubbleType && ch.bubbleType !== 'done' && ch.bubbleType !== 'error') {
              ch.bubbleTimer = Math.min(ch.bubbleTimer, BUBBLE_FADE_SEC)
            }
            EventLogStore.addEntry({
              agentRole: data.agentRole,
              agentDisplayName: ch.displayName,
              emoji: EVENT_EMOJI.idle,
              action: 'Idle',
            })
          } else if (data.status === 'active') {
            ch.isActive = true
            EventLogStore.addEntry({
              agentRole: data.agentRole,
              agentDisplayName: ch.displayName,
              emoji: EVENT_EMOJI.active,
              action: 'Active',
            })
          }
          triggerPanelRefresh()
        }
      })
      if (unsub7) ipcCleanups.push(unsub7)

      // Game loop
      const stopLoop = startGameLoop(canvasEl, {
        update(dt: number) {
          for (const ch of characters) {
            const walkable = roomWalkableTiles.get(ch.room) ?? []
            updateCharacter(ch, dt, walkable, seats, tileGrid, blockedTiles)
          }
        },
        render(ctx: CanvasRenderingContext2D) {
          renderFrame(ctx, renderState)
        },
      })

      cleanup = () => {
        stopLoop()
        window.removeEventListener('resize', resize)
        resizeObserver.disconnect()
        canvasEl.removeEventListener('wheel', onWheel)
        canvasEl.removeEventListener('click', onClick)
        delete (window as unknown as Record<string, unknown>).__refreshLayout
        // Remove IPC listeners to prevent duplicates on HMR
        for (const unsub of ipcCleanups) unsub()
      }

      api?.sendReady()
      console.log('[Renderer] Office initialized with', characters.length, 'agents, sendReady:', !!api?.sendReady)
    }

    init().catch(console.error)

    return () => { aborted = true; cleanup?.() }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <canvas
      ref={canvasRef}
      style={{ display: 'block', width: '100%', height: '100%', cursor: 'default' }}
    />
  )
}
