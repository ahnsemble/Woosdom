import { useState, useEffect, useRef, useCallback } from 'react'
import type { MutableRefObject } from 'react'
import { EditorTool } from './EditorState.ts'
import type { EditorTool as EditorToolValue, SelectedTile } from './EditorState.ts'
import { loadLayout, getLayoutSync, setLayout } from '../config/LayoutLoader.ts'
import { paintFloor, paintWall, eraseTile, placeFurniture, findFurnitureAt, removeFurniture } from './EditorActions.ts'
import type { LayoutConfig } from '../config/LayoutTypes.ts'

interface FurniturePresetData {
  tiles: Array<{ sx: number; sy: number; offsetCol: number; offsetRow: number }>
  blockedOffsets: [number, number][]
}

interface SingleItemData {
  sx: number
  sy: number
  blocked: boolean
}

interface TilesetMapData {
  furniturePresets?: Record<string, FurniturePresetData>
  singleTileItems?: Record<string, SingleItemData>
}

interface UseEditorOptions {
  customizeMode: boolean
  setCustomizeMode: (mode: boolean) => void
  editorTileClickRef: MutableRefObject<((col: number, row: number) => void) | null>
  refreshLayoutRef: MutableRefObject<(() => void) | null>
}

interface UseEditorResult {
  editorTool: EditorToolValue
  setEditorTool: (tool: EditorToolValue) => void
  selectedFloorTile: SelectedTile | null
  setSelectedFloorTile: (tile: SelectedTile | null) => void
  selectedWallTile: SelectedTile | null
  setSelectedWallTile: (tile: SelectedTile | null) => void
  selectedFurniturePreset: string | null
  setSelectedFurniturePreset: (preset: string | null) => void
  tilesets: HTMLImageElement[]
  handleEnterCustomize: () => Promise<void>
  handleSave: () => Promise<void>
  handleCancel: () => void
}

export function useEditor({
  customizeMode,
  setCustomizeMode,
  editorTileClickRef,
  refreshLayoutRef,
}: UseEditorOptions): UseEditorResult {
  const [editorTool, setEditorTool] = useState<EditorToolValue>(EditorTool.FLOOR_PAINT)
  const [selectedFloorTile, setSelectedFloorTile] = useState<SelectedTile | null>(null)
  const [selectedWallTile, setSelectedWallTile] = useState<SelectedTile | null>(null)
  const [selectedFurniturePreset, setSelectedFurniturePreset] = useState<string | null>(null)
  const [tilesets, setTilesets] = useState<HTMLImageElement[]>([])
  const [tilesetMapData, setTilesetMapData] = useState<TilesetMapData | null>(null)
  const originalLayoutRef = useRef<LayoutConfig | null>(null)

  useEffect(() => {
    const urls = [
      new URL('../assets/tileset.png', import.meta.url).href,
      new URL('../assets/tileset2.png', import.meta.url).href,
      new URL('../assets/tilesets/vx_ace/A2 Office Floors.png', import.meta.url).href,
      new URL('../assets/tilesets/vx_ace/A4 Office Walls.png', import.meta.url).href,
      new URL('../assets/tilesets/vx_ace/A5 Office Floors & Walls.png', import.meta.url).href,
      new URL('../assets/tilesets/vx_ace/B-C-D-E Office 1 No Shadows.png', import.meta.url).href,
      new URL('../assets/tilesets/vx_ace/B-C-D-E Office 2 No Shadows.png', import.meta.url).href,
    ]

    Promise.all(urls.map(url => new Promise<HTMLImageElement | null>((resolve) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = () => resolve(null)
      img.src = url
    }))).then(imgs => setTilesets(imgs.filter(Boolean) as HTMLImageElement[])).catch(console.error)
  }, [])

  useEffect(() => {
    fetch(new URL('../../config/tileset-map.json', import.meta.url).href)
      .then(r => r.json())
      .then((data: TilesetMapData) => setTilesetMapData(data))
      .catch(console.error)
  }, [])

  const handleEnterCustomize = useCallback(async () => {
    try {
      await loadLayout()
      const current = getLayoutSync()
      originalLayoutRef.current = JSON.parse(JSON.stringify(current))
      setCustomizeMode(true)
    } catch {
      console.error('Cannot enter customize mode - layout not loaded')
    }
  }, [setCustomizeMode])

  const handleSave = useCallback(async () => {
    try {
      const layout = getLayoutSync()
      const api = window.electronAPI
      if (api?.writeLayout) {
        await api.writeLayout(layout)
      }
      setCustomizeMode(false)
      originalLayoutRef.current = null
      refreshLayoutRef.current?.()
    } catch (err) {
      console.error('Failed to save layout:', err)
    }
  }, [refreshLayoutRef, setCustomizeMode])

  const handleCancel = useCallback(() => {
    if (originalLayoutRef.current) {
      setLayout(originalLayoutRef.current)
    }
    setCustomizeMode(false)
    originalLayoutRef.current = null
    refreshLayoutRef.current?.()
  }, [refreshLayoutRef, setCustomizeMode])

  const handleEditorTileClick = useCallback((col: number, row: number) => {
    if (!customizeMode) return

    try {
      let layout = getLayoutSync()

      if (editorTool === EditorTool.FLOOR_PAINT && selectedFloorTile) {
        layout = paintFloor(layout, col, row, selectedFloorTile.sx, selectedFloorTile.sy, selectedFloorTile.tilesetIdx)
      } else if (editorTool === EditorTool.WALL_PAINT && selectedWallTile) {
        layout = paintWall(layout, col, row, selectedWallTile.sx, selectedWallTile.sy, selectedWallTile.tilesetIdx)
      } else if (editorTool === EditorTool.WALL_PAINT) {
        layout = paintWall(layout, col, row)
      } else if (editorTool === EditorTool.ERASE) {
        const furniture = findFurnitureAt(layout, col, row)
        if (furniture) {
          layout = removeFurniture(layout, furniture.uid)
        } else {
          layout = eraseTile(layout, col, row)
        }
      } else if (editorTool === EditorTool.FURNITURE_PLACE && selectedFurniturePreset && tilesetMapData) {
        const preset = tilesetMapData.furniturePresets?.[selectedFurniturePreset]
        const singleItem = tilesetMapData.singleTileItems?.[selectedFurniturePreset]

        if (preset) {
          layout = placeFurniture(
            layout,
            selectedFurniturePreset,
            col,
            row,
            preset.tiles,
            preset.blockedOffsets,
          )
        } else if (singleItem) {
          layout = placeFurniture(
            layout,
            selectedFurniturePreset,
            col,
            row,
            [{ sx: singleItem.sx, sy: singleItem.sy, offsetCol: 0, offsetRow: 0 }],
            singleItem.blocked ? [[0, 0]] : [],
          )
        } else if (selectedFurniturePreset.startsWith('t2_')) {
          const parts = selectedFurniturePreset.split('_')
          const t2Col = Number.parseInt(parts[1], 10)
          const t2Row = Number.parseInt(parts[2], 10)
          if (!Number.isNaN(t2Col) && !Number.isNaN(t2Row)) {
            layout = placeFurniture(
              layout,
              selectedFurniturePreset,
              col,
              row,
              [{ sx: t2Col, sy: t2Row, offsetCol: 0, offsetRow: 0, tilesetIdx: 1 }],
              [[0, 0]],
            )
          }
        } else if (selectedFurniturePreset.startsWith('vx_')) {
          const parts = selectedFurniturePreset.split('_')
          const vxIdx = Number.parseInt(parts[1], 10)
          const vxCol = Number.parseInt(parts[2], 10)
          const vxRow = Number.parseInt(parts[3], 10)
          const vxSw = Number.parseInt(parts[4], 10) || 1
          const vxSh = Number.parseInt(parts[5], 10) || 1

          if (!Number.isNaN(vxIdx) && !Number.isNaN(vxCol) && !Number.isNaN(vxRow)) {
            layout = placeFurniture(
              layout,
              selectedFurniturePreset,
              col,
              row,
              [{ sx: vxCol, sy: vxRow, offsetCol: 0, offsetRow: 0, tilesetIdx: vxIdx, sw: vxSw, sh: vxSh }],
              [[0, 0]],
            )
          }
        }
      }

      setLayout(layout)
      refreshLayoutRef.current?.()
    } catch (err) {
      console.error('Editor action failed:', err)
    }
  }, [
    customizeMode,
    editorTool,
    refreshLayoutRef,
    selectedFloorTile,
    selectedFurniturePreset,
    selectedWallTile,
    tilesetMapData,
  ])

  useEffect(() => {
    editorTileClickRef.current = handleEditorTileClick
    return () => {
      if (editorTileClickRef.current === handleEditorTileClick) {
        editorTileClickRef.current = null
      }
    }
  }, [editorTileClickRef, handleEditorTileClick])

  return {
    editorTool,
    setEditorTool,
    selectedFloorTile,
    setSelectedFloorTile,
    selectedWallTile,
    setSelectedWallTile,
    selectedFurniturePreset,
    setSelectedFurniturePreset,
    tilesets,
    handleEnterCustomize,
    handleSave,
    handleCancel,
  }
}
