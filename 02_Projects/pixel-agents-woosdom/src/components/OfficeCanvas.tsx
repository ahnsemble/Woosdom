import { useEffect, useRef } from 'react'
import { startGameLoop } from '../canvas/GameLoop.ts'
import { createTileGrid, createFurniturePlacements, createSeats, getBlockedTiles } from '../canvas/OfficeLayout.ts'
import { createRenderState, renderFrame } from '../canvas/Renderer.ts'
import { createCharacter, updateCharacter } from '../canvas/Characters.ts'
import { getWalkableTilesInRegion } from '../canvas/Pathfinding.ts'
import type { Character, Seat } from '../canvas/types.ts'
import { loadLayout, getLayoutSync } from '../config/LayoutLoader.ts'
import { getAgentDefinitions } from '../agents/AgentDefs.ts'
import { useAppContext } from '../contexts/AppContext.tsx'
import { loadAssets } from '../loaders/AssetLoader.ts'
import { setupIPCListeners } from '../ipc/IPCHandlers.ts'
import { setupInputHandlers } from '../input/InputManager.ts'

export default function OfficeCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const customizeModeRef = useRef(false)
  const {
    setSelectedAgent,
    charactersRef,
    triggerPanelRefresh,
    customizeMode,
    editorTileClickRef,
    refreshLayoutRef,
  } = useAppContext()

  customizeModeRef.current = customizeMode

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    let aborted = false
    let cleanup: (() => void) | null = null
    const canvasEl = canvas

    async function init() {
      await loadLayout()
      if (aborted) return

      const { spritesImg, tilesets } = await loadAssets()
      if (aborted) return

      const tileGrid = createTileGrid()
      let furniture = createFurniturePlacements()
      const blockedTiles = getBlockedTiles(furniture)

      const seats = new Map<string, Seat>()
      for (const seat of createSeats()) {
        seats.set(seat.id, seat)
      }

      const characters: Character[] = getAgentDefinitions().map(def => {
        const seat = seats.get(def.seatId) ?? null
        return createCharacter(def, seat)
      })
      charactersRef.current = characters

      const rooms = [...getLayoutSync().rooms]
      const roomWalkableTiles = new Map<string, Array<{ col: number; row: number }>>()

      const rebuildRoomWalkables = () => {
        roomWalkableTiles.clear()
        for (const room of rooms) {
          roomWalkableTiles.set(
            room.id,
            getWalkableTilesInRegion(room.minCol, room.maxCol, room.minRow, room.maxRow, tileGrid, blockedTiles),
          )
        }
        if (tileGrid.length > 0 && tileGrid[0]?.length > 0) {
          roomWalkableTiles.set(
            'brain',
            getWalkableTilesInRegion(0, tileGrid[0].length - 1, 0, tileGrid.length - 1, tileGrid, blockedTiles),
          )
        } else {
          roomWalkableTiles.set('brain', [])
        }
      }

      rebuildRoomWalkables()

      const renderState = createRenderState()
      renderState.tileGrid = tileGrid
      renderState.furniture = furniture
      renderState.characters = characters
      renderState.tilesets = tilesets
      renderState.spritesImg = spritesImg

      const refreshLayout = () => {
        const nextTileGrid = createTileGrid()
        const nextFurniture = createFurniturePlacements()
        const nextBlockedTiles = getBlockedTiles(nextFurniture)
        const nextRooms = getLayoutSync().rooms

        tileGrid.length = 0
        tileGrid.push(...nextTileGrid)
        furniture = nextFurniture
        blockedTiles.clear()
        for (const key of nextBlockedTiles) blockedTiles.add(key)

        rooms.length = 0
        rooms.push(...nextRooms)

        renderState.tileGrid = tileGrid
        renderState.furniture = furniture
        rebuildRoomWalkables()
      }

      refreshLayoutRef.current = refreshLayout

      if (aborted) return

      const cleanupIPC = setupIPCListeners(
        characters,
        tileGrid,
        blockedTiles,
        rooms,
        triggerPanelRefresh,
      )

      const cleanupInput = setupInputHandlers(
        canvasEl,
        renderState,
        characters,
        setSelectedAgent,
        { customizeModeRef, editorTileClickRef },
      )

      const stopLoop = startGameLoop(canvasEl, {
        update(dt: number) {
          for (const ch of characters) {
            const walkable = roomWalkableTiles.get(ch.room) ?? []
            updateCharacter(ch, dt, walkable, seats, tileGrid, blockedTiles)
          }
        },
        render(ctx: CanvasRenderingContext2D) {
          renderFrame(ctx, renderState, customizeModeRef.current)
        },
      })

      cleanup = () => {
        stopLoop()
        cleanupIPC()
        cleanupInput()
        if (refreshLayoutRef.current === refreshLayout) {
          refreshLayoutRef.current = null
        }
      }

      window.electronAPI?.sendReady()
    }

    init().catch(console.error)

    return () => {
      aborted = true
      cleanup?.()
    }
  }, [charactersRef, editorTileClickRef, refreshLayoutRef, setSelectedAgent, triggerPanelRefresh])

  return (
    <canvas
      ref={canvasRef}
      style={{ display: 'block', width: '100%', height: '100%', cursor: 'default' }}
    />
  )
}
