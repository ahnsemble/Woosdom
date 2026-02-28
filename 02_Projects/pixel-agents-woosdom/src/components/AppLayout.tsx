import { useState, useEffect, useRef, useCallback } from 'react'
import OfficeCanvas from './OfficeCanvas.tsx'
import ActivityLogPanel from './ActivityLogPanel.tsx'
import AgentDetailPanel from './AgentDetailPanel.tsx'
import EditorToolbar from './EditorToolbar.tsx'
import { useAppContext } from '../contexts/AppContext.tsx'
import { EditorTool } from '../editor/EditorState.ts'
import type { SelectedTile } from '../editor/EditorState.ts'
import { loadLayout, getLayoutSync, setLayout } from '../config/LayoutLoader.ts'
import { paintFloor, paintWall, eraseTile, placeFurniture, findFurnitureAt, removeFurniture } from '../editor/EditorActions.ts'
import type { LayoutConfig } from '../config/LayoutTypes.ts'

export default function AppLayout() {
  const { panelView, selectedAgent, customizeMode, setCustomizeMode } = useAppContext()
  const [panelOpen, setPanelOpen] = useState(true)

  // Editor state
  const [editorTool, setEditorTool] = useState<string>(EditorTool.FLOOR_PAINT)
  const [selectedFloorTile, setSelectedFloorTile] = useState<SelectedTile | null>(null)
  const [selectedWallTile, setSelectedWallTile] = useState<SelectedTile | null>(null)
  const [selectedFurniturePreset, setSelectedFurniturePreset] = useState<string | null>(null)
  const [tilesets, setTilesets] = useState<HTMLImageElement[]>([])
  const [tilesetMapData, setTilesetMapData] = useState<Record<string, unknown> | null>(null)
  const originalLayoutRef = useRef<LayoutConfig | null>(null)

  const customizeModeRef = useRef(customizeMode)
  customizeModeRef.current = customizeMode

  const editorClickRef = useRef<(col: number, row: number) => void>(() => { })

  // Load all tileset images for palette
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

  // Load tileset map data for furniture presets
  useEffect(() => {
    fetch(new URL('../../config/tileset-map.json', import.meta.url).href)
      .then(r => r.json())
      .then(setTilesetMapData)
      .catch(console.error)
  }, [])

  const handleEnterCustomize = useCallback(async () => {
    try {
      await loadLayout()
      const current = getLayoutSync()
      originalLayoutRef.current = JSON.parse(JSON.stringify(current))
      setCustomizeMode(true)
    } catch {
      console.error('Cannot enter customize mode — layout not loaded')
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

      // Force layout refresh without reloading the page
      // This preserves agent positions and prevents UI state loss
      const refresh = (window as unknown as Record<string, unknown>).__refreshLayout as (() => void) | undefined
      if (refresh) refresh()
    } catch (err) {
      console.error('Failed to save layout:', err)
    }
  }, [setCustomizeMode])

  const handleCancel = useCallback(() => {
    if (originalLayoutRef.current) {
      setLayout(originalLayoutRef.current)
    }
    setCustomizeMode(false)
    originalLayoutRef.current = null

    const refresh = (window as unknown as Record<string, unknown>).__refreshLayout as (() => void) | undefined
    if (refresh) refresh()
  }, [setCustomizeMode])

  // Handle canvas tile clicks in customize mode
  const handleEditorTileClick = useCallback((col: number, row: number) => {
    if (!customizeModeRef.current) return

    try {
      let layout = getLayoutSync()

      if (editorTool === EditorTool.FLOOR_PAINT && selectedFloorTile) {
        layout = paintFloor(layout, col, row, selectedFloorTile.sx, selectedFloorTile.sy, selectedFloorTile.tilesetIdx)
      } else if (editorTool === EditorTool.WALL_PAINT && selectedWallTile) {
        layout = paintWall(layout, col, row, selectedWallTile.sx, selectedWallTile.sy, selectedWallTile.tilesetIdx)
      } else if (editorTool === EditorTool.WALL_PAINT) {
        layout = paintWall(layout, col, row)
      } else if (editorTool === EditorTool.ERASE) {
        // Check if there's furniture to remove first
        const furniture = findFurnitureAt(layout, col, row)
        if (furniture) {
          layout = removeFurniture(layout, furniture.uid)
        } else {
          layout = eraseTile(layout, col, row)
        }
      } else if (editorTool === EditorTool.FURNITURE_PLACE && selectedFurniturePreset && tilesetMapData) {
        const presets = (tilesetMapData as Record<string, unknown>).furniturePresets as Record<string, unknown> | undefined
        const singleItems = (tilesetMapData as Record<string, unknown>).singleTileItems as Record<string, unknown> | undefined
        const preset = presets?.[selectedFurniturePreset] as Record<string, unknown> | undefined
        const singleItem = singleItems?.[selectedFurniturePreset] as Record<string, unknown> | undefined

        if (preset) {
          layout = placeFurniture(
            layout,
            selectedFurniturePreset,
            col, row,
            (preset.tiles as Array<{ sx: number; sy: number; offsetCol: number; offsetRow: number }>),
            (preset.blockedOffsets as [number, number][]),
          )
        } else if (singleItem) {
          layout = placeFurniture(
            layout,
            selectedFurniturePreset,
            col, row,
            [{ sx: singleItem.sx as number, sy: singleItem.sy as number, offsetCol: 0, offsetRow: 0 }],
            singleItem.blocked ? [[0, 0]] : [],
          )
        } else if (selectedFurniturePreset.startsWith('t2_')) {
          // tileset2 single tile: key format "t2_COL_ROW"
          const parts = selectedFurniturePreset.split('_')
          const t2Col = parseInt(parts[1])
          const t2Row = parseInt(parts[2])
          if (!isNaN(t2Col) && !isNaN(t2Row)) {
            layout = placeFurniture(
              layout,
              selectedFurniturePreset,
              col, row,
              [{ sx: t2Col, sy: t2Row, offsetCol: 0, offsetRow: 0, tilesetIdx: 1 }],
              [[0, 0]],
            )
          }
        } else if (selectedFurniturePreset.startsWith('vx_')) {
          // vx single tile: key format "vx_IDX_COL_ROW_SW_SH"
          const parts = selectedFurniturePreset.split('_')
          const vxIdx = parseInt(parts[1])
          const vxCol = parseInt(parts[2])
          const vxRow = parseInt(parts[3])
          const vxSw = parseInt(parts[4]) || 1
          const vxSh = parseInt(parts[5]) || 1

          if (!isNaN(vxIdx) && !isNaN(vxCol) && !isNaN(vxRow)) {
            const blockedOffsets: [number, number][] = [[0, 0]]
            layout = placeFurniture(
              layout,
              selectedFurniturePreset,
              col, row,
              [{ sx: vxCol, sy: vxRow, offsetCol: 0, offsetRow: 0, tilesetIdx: vxIdx, sw: vxSw, sh: vxSh }],
              blockedOffsets,
            )
          }
        }
      }

      setLayout(layout)
      const refresh = (window as unknown as Record<string, unknown>).__refreshLayout as (() => void) | undefined
      refresh?.()
    } catch (err) {
      console.error('Editor action failed:', err)
    }
  }, [editorTool, selectedFloorTile, selectedWallTile, selectedFurniturePreset, tilesetMapData])

  editorClickRef.current = handleEditorTileClick

  // Expose editor click handler via window for OfficeCanvas to call
  useEffect(() => {
    (window as unknown as Record<string, unknown>).__editorTileClick = (col: number, row: number) => {
      editorClickRef.current(col, row)
    }
    return () => {
      delete (window as unknown as Record<string, unknown>).__editorTileClick
    }
  }, [])

  useEffect(() => {
    (window as unknown as Record<string, unknown>).__customizeMode = customizeMode
  }, [customizeMode])

  return (
    <div style={{
      display: 'flex',
      width: '100vw',
      height: '100vh',
      overflow: 'hidden',
      background: '#1a1a2e',
    }}>
      {/* Canvas + editor toolbar area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <div style={{ flex: 1, position: 'relative', minHeight: 0 }}>
          <OfficeCanvas />

          {/* Floating buttons */}
          <div style={{
            position: 'absolute',
            top: 8,
            right: 8,
            display: 'flex',
            gap: 6,
          }}>
            {!customizeMode && (
              <button
                onClick={handleEnterCustomize}
                style={{
                  background: 'rgba(0,0,0,0.6)',
                  color: '#e8a87c',
                  border: '1px solid #e8a87c',
                  borderRadius: 4,
                  padding: '4px 10px',
                  cursor: 'pointer',
                  fontSize: '12px',
                }}
              >
                Customize
              </button>
            )}
            <button
              onClick={() => setPanelOpen(!panelOpen)}
              style={{
                background: 'rgba(0,0,0,0.6)',
                color: '#ccc',
                border: '1px solid #555',
                borderRadius: 4,
                padding: '4px 10px',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              {panelOpen ? 'Hide Panel' : 'Show Panel'}
            </button>
          </div>
        </div>

        {/* Editor toolbar (bottom) */}
        {customizeMode && (
          <EditorToolbar
            tool={editorTool}
            onToolChange={setEditorTool}
            onSave={handleSave}
            onCancel={handleCancel}
            tilesets={tilesets}
            onSelectFloorTile={setSelectedFloorTile}
            onSelectWallTile={setSelectedWallTile}
            onSelectFurniturePreset={setSelectedFurniturePreset}
            selectedFloorTile={selectedFloorTile}
            selectedWallTile={selectedWallTile}
            selectedFurniturePreset={selectedFurniturePreset}
          />
        )}
      </div>

      {/* Right panel */}
      {panelOpen && !customizeMode && (
        <div style={{
          width: 320,
          borderLeft: '2px solid #333',
          display: 'flex',
          flexDirection: 'column',
          flexShrink: 0,
        }}>
          {panelView === 'agent' && selectedAgent ? (
            <AgentDetailPanel />
          ) : (
            <ActivityLogPanel />
          )}
        </div>
      )}
    </div>
  )
}
