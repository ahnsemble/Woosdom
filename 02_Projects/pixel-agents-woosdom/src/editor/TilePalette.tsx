import { useEffect, useRef, useState } from 'react'
import type { EditorTool, SelectedTile } from './EditorState.ts'

interface TileInfo {
  col: number
  row: number
  avgColor: number[]
  transparency: number
}

interface Tileset2Map {
  tileSize: number
  gridCols: number
  gridRows: number
  tiles: Array<{ col: number; row: number; label: string; transparency: number }>
}

interface FurniturePreset {
  label: string
  description: string
  tiles: Array<{ sx: number; sy: number; offsetCol: number; offsetRow: number }>
  footprint: [number, number]
  blockedOffsets: [number, number][]
}

interface TilesetMap {
  tileSize: number
  gridCols: number
  gridRows: number
  categories: Record<string, TileInfo[]>
  furniturePresets: Record<string, FurniturePreset>
  singleTileItems: Record<string, { sx: number; sy: number; category: string; label: string; blocked: boolean }>
}

interface Props {
  tool: EditorTool
  tilesets: HTMLImageElement[]
  onSelectFloorTile: (tile: SelectedTile) => void
  onSelectWallTile: (tile: SelectedTile) => void
  onSelectFurniturePreset: (key: string) => void
  selectedFloorTile: SelectedTile | null
  selectedWallTile?: SelectedTile | null
  selectedFurniturePreset: string | null
}

const PREVIEW_SIZE = 22  // Slightly larger than 16px to fit 15 per row without overflow
const TILE_SIZE = 16

const CATEGORY_FOR_TOOL: Record<string, string[]> = {
  floor_paint: ['floor', 'rug'],
  wall_paint: ['wall'],
  furniture_place: ['desk', 'chair', 'bookshelf', 'sofa', 'appliance', 'computer', 'plant', 'box', 'decoration', 'misc'],
  erase: [],
}

export default function TilePalette({
  tool, tilesets,
  onSelectFloorTile, onSelectWallTile, onSelectFurniturePreset,
  selectedFloorTile, selectedWallTile, selectedFurniturePreset,
}: Props) {
  const [tilesetMap, setTilesetMap] = useState<TilesetMap | null>(null)
  const [tilesetMap2, setTilesetMap2] = useState<Tileset2Map | null>(null)
  const [tilesetVxMap, setTilesetVxMap] = useState<any>(null)

  useEffect(() => {
    fetch(new URL('../../config/tileset-map.json', import.meta.url).href)
      .then(r => r.json())
      .then(setTilesetMap)
      .catch(console.error)
    fetch(new URL('../../config/tileset2-map.json', import.meta.url).href)
      .then(r => r.json())
      .then(setTilesetMap2)
      .catch(console.error)
    fetch(new URL('../../config/tileset-vx-map.json', import.meta.url).href)
      .then(r => r.json())
      .then(setTilesetVxMap)
      .catch(console.error)
  }, [])

  if (!tilesetMap || tilesets.length === 0 || !tilesets[0]) return null

  const categories = CATEGORY_FOR_TOOL[tool] ?? []

  // For furniture tool, also show presets
  if (tool === 'furniture_place') {
    return (
      <div style={{ padding: '8px', overflow: 'auto', maxHeight: '300px' }}>
        <div style={{ color: '#888', fontSize: '10px', marginBottom: '6px', fontWeight: 'bold' }}>
          FURNITURE PRESETS
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2px', marginBottom: '12px' }}>
          {Object.entries(tilesetMap.furniturePresets).map(([key, preset]) => (
            <PresetButton
              key={key}
              preset={preset}
              tilesetImg={tilesets[0]}
              isSelected={selectedFurniturePreset === key}
              onClick={() => onSelectFurniturePreset(key)}
            />
          ))}
        </div>
        <div style={{ color: '#888', fontSize: '10px', marginBottom: '6px', fontWeight: 'bold' }}>
          SINGLE ITEMS
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2px', marginBottom: '12px' }}>
          {Object.entries(tilesetMap.singleTileItems).map(([key, item]) => (
            <TileButton
              key={key}
              sx={item.sx}
              sy={item.sy}
              tilesetImg={tilesets[0]}
              label={item.label}
              isSelected={selectedFurniturePreset === key}
              onClick={() => onSelectFurniturePreset(key)}
            />
          ))}
        </div>

        {tilesets[1] && tilesetMap2 && tilesetMap2.tiles.length > 0 && (
          <>
            <div style={{ color: '#e8a87c', fontSize: '10px', marginBottom: '6px', fontWeight: 'bold' }}>
              OFFICE PACK 2 ({tilesetMap2.tiles.length} tiles)
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2px', marginBottom: '12px' }}>
              {tilesetMap2.tiles.map((t: any) => {
                const key = `t2_${t.col}_${t.row}`
                return (
                  <TileButton
                    key={key}
                    sx={t.col}
                    sy={t.row}
                    tilesetImg={tilesets[1]}
                    label={t.label}
                    isSelected={selectedFurniturePreset === key}
                    onClick={() => onSelectFurniturePreset(key)}
                  />
                )
              })}
            </div>
          </>
        )}

        {tilesetVxMap && tilesetVxMap.images.filter((img: any) => img.category === 'furniture').map((img: any) => (
          <div key={img.file}>
            <div style={{ color: '#e8a87c', fontSize: '10px', marginBottom: '6px', fontWeight: 'bold' }}>
              {img.file.toUpperCase().replace('.PNG', '')} ({img.tiles.length} tiles)
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2px', marginBottom: '12px' }}>
              {img.tiles.map((t: any) => {
                const sw = t.sw ?? 1
                const sh = t.sh ?? 1
                const key = `vx_${t.tilesetIdx}_${t.col}_${t.row}_${sw}_${sh}`
                const imgRef = tilesets[t.tilesetIdx]
                if (!imgRef) return null
                return (
                  <TileButton
                    key={key}
                    sx={t.col}
                    sy={t.row}
                    sw={sw}
                    sh={sh}
                    tilesetImg={imgRef}
                    label={img.file}
                    isSelected={selectedFurniturePreset === key}
                    onClick={() => onSelectFurniturePreset(key)}
                  />
                )
              })}
            </div>
          </div>
        ))}
      </div>
    )
  }

  // For floor/wall tools, show category tiles
  const tiles: (TileInfo & { tilesetIdx?: number })[] = []
  for (const cat of categories) {
    tiles.push(...(tilesetMap.categories[cat] ?? []).map((t: any) => ({ ...t, tilesetIdx: 0 })))
  }

  // Add VX tiles
  if (tilesetVxMap) {
    for (const img of tilesetVxMap.images) {
      if ((tool === 'floor_paint' && img.category === 'floor') ||
        (tool === 'wall_paint' && img.category === 'wall')) {
        tiles.push(...img.tiles.map((t: any) => ({ col: t.col, row: t.row, avgColor: [], transparency: 0, tilesetIdx: t.tilesetIdx })))
      }
    }
  }

  if (tool === 'erase') {
    return (
      <div style={{ padding: '12px', color: '#e88', fontSize: '12px', textAlign: 'center' }}>
        Click on map to erase tiles / furniture
      </div>
    )
  }

  return (
    <div style={{ padding: '8px', overflow: 'auto', maxHeight: '300px' }}>
      <div style={{ color: '#888', fontSize: '10px', marginBottom: '6px', fontWeight: 'bold' }}>
        {tool === 'floor_paint' ? 'FLOOR TILES' : 'WALL TILES'}
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2px' }}>
        {tiles.map(t => {
          const isSelected = tool === 'floor_paint'
            ? selectedFloorTile?.sx === t.col && selectedFloorTile?.sy === t.row && (selectedFloorTile?.tilesetIdx ?? 0) === (t.tilesetIdx ?? 0)
            : tool === 'wall_paint'
              ? selectedWallTile?.sx === t.col && selectedWallTile?.sy === t.row && (selectedWallTile?.tilesetIdx ?? 0) === (t.tilesetIdx ?? 0)
              : false
          return (
            <TileButton
              key={`${t.tilesetIdx ?? 0},${t.col},${t.row}`}
              sx={t.col}
              sy={t.row}
              tilesetImg={tilesets[t.tilesetIdx ?? 0]}
              isSelected={isSelected}
              onClick={() => {
                if (tool === 'floor_paint') onSelectFloorTile({ sx: t.col, sy: t.row, tilesetIdx: t.tilesetIdx ?? 0 })
                else if (tool === 'wall_paint') onSelectWallTile({ sx: t.col, sy: t.row, tilesetIdx: t.tilesetIdx ?? 0 })
              }}
            />
          )
        })}
      </div>
    </div>
  )
}

function TileButton({ sx, sy, sw = 1, sh = 1, tilesetImg, isSelected, onClick, label }: {
  sx: number
  sy: number
  sw?: number
  sh?: number
  tilesetImg: HTMLImageElement
  isSelected: boolean
  onClick: () => void
  label?: string
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!canvasRef.current) return
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return
    ctx.imageSmoothingEnabled = false
    ctx.clearRect(0, 0, PREVIEW_SIZE, PREVIEW_SIZE)
    ctx.fillStyle = '#3a3a5e'
    ctx.fillRect(0, 0, PREVIEW_SIZE, PREVIEW_SIZE)
    ctx.drawImage(
      tilesetImg,
      sx * TILE_SIZE, sy * TILE_SIZE, sw * TILE_SIZE, sh * TILE_SIZE,
      0, 0, PREVIEW_SIZE, PREVIEW_SIZE,
    )
  }, [sx, sy, sw, sh, tilesetImg])

  return (
    <canvas
      ref={canvasRef}
      width={PREVIEW_SIZE}
      height={PREVIEW_SIZE}
      title={label ?? `Tile (${sx}, ${sy})`}
      onClick={onClick}
      style={{
        cursor: 'pointer',
        border: isSelected ? '2px solid #7ec8e3' : '1px solid #444',
        borderRadius: '1px',
        imageRendering: 'pixelated',
        transition: 'transform 0.1s',
      }}
      onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.2)' }}
      onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)' }}
    />
  )
}

function PresetButton({ preset, tilesetImg, isSelected, onClick }: {
  preset: FurniturePreset
  tilesetImg: HTMLImageElement
  isSelected: boolean
  onClick: () => void
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [w, h] = preset.footprint
  const canvasW = w * PREVIEW_SIZE
  const canvasH = h * PREVIEW_SIZE

  useEffect(() => {
    if (!canvasRef.current) return
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return
    ctx.imageSmoothingEnabled = false
    ctx.clearRect(0, 0, canvasW, canvasH)
    ctx.fillStyle = '#3a3a5e'
    ctx.fillRect(0, 0, canvasW, canvasH)
    for (const t of preset.tiles) {
      ctx.drawImage(
        tilesetImg,
        t.sx * TILE_SIZE, t.sy * TILE_SIZE, TILE_SIZE, TILE_SIZE,
        t.offsetCol * PREVIEW_SIZE, t.offsetRow * PREVIEW_SIZE, PREVIEW_SIZE, PREVIEW_SIZE,
      )
    }
  }, [preset, tilesetImg, canvasW, canvasH])

  return (
    <div
      onClick={onClick}
      title={preset.description}
      style={{
        cursor: 'pointer',
        border: isSelected ? '2px solid #7ec8e3' : '1px solid #444',
        borderRadius: '2px',
        padding: '1px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        transition: 'transform 0.1s',
      }}
      onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.15)' }}
      onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)' }}
    >
      <canvas
        ref={canvasRef}
        width={canvasW}
        height={canvasH}
        style={{ imageRendering: 'pixelated' }}
      />
      <div style={{ fontSize: '9px', color: '#aaa', marginTop: '2px' }}>
        {preset.label}
      </div>
    </div>
  )
}
