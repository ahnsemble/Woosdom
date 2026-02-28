import { EditorTool } from '../editor/EditorState.ts'
import type { SelectedTile } from '../editor/EditorState.ts'
import TilePalette from '../editor/TilePalette.tsx'

interface Props {
  onSave: () => void
  onCancel: () => void
  tool: string
  onToolChange: (tool: string) => void
  tilesets: HTMLImageElement[]
  onSelectFloorTile: (tile: SelectedTile) => void
  onSelectWallTile: (tile: SelectedTile) => void
  onSelectFurniturePreset: (key: string) => void
  selectedFloorTile: SelectedTile | null
  selectedWallTile?: SelectedTile | null
  selectedFurniturePreset: string | null
}

const TOOLS = [
  { id: EditorTool.FLOOR_PAINT, label: 'Floor', icon: '\u2B1B' },
  { id: EditorTool.WALL_PAINT, label: 'Wall', icon: '\uD83E\uDDF1' },
  { id: EditorTool.FURNITURE_PLACE, label: 'Furniture', icon: '\uD83E\uDE91' },
  { id: EditorTool.ERASE, label: 'Erase', icon: '\uD83D\uDDD1\uFE0F' },
]

export default function EditorToolbar({
  onSave, onCancel, tool, onToolChange, tilesets,
  onSelectFloorTile, onSelectWallTile, onSelectFurniturePreset,
  selectedFloorTile, selectedWallTile, selectedFurniturePreset,
}: Props) {
  return (
    <div style={{
      background: '#1a1a2e',
      borderTop: '2px solid #555',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Toolbar header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        padding: '6px 12px',
        borderBottom: '1px solid #333',
        gap: '8px',
      }}>
        <span style={{ color: '#e8a87c', fontWeight: 'bold', fontSize: '13px' }}>
          Customize Mode
        </span>
        <div style={{ flex: 1 }} />
        <button
          onClick={onSave}
          style={{
            background: '#2d5a27',
            color: '#fff',
            border: 'none',
            borderRadius: '3px',
            padding: '4px 12px',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          Save
        </button>
        <button
          onClick={onCancel}
          style={{
            background: '#5a2727',
            color: '#fff',
            border: 'none',
            borderRadius: '3px',
            padding: '4px 12px',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          Cancel
        </button>
      </div>

      {/* Tool buttons */}
      <div style={{
        display: 'flex',
        gap: '4px',
        padding: '6px 12px',
        borderBottom: '1px solid #333',
      }}>
        {TOOLS.map(t => (
          <button
            key={t.id}
            onClick={() => onToolChange(t.id)}
            style={{
              background: tool === t.id ? '#3a3a5e' : 'transparent',
              color: tool === t.id ? '#7ec8e3' : '#888',
              border: tool === t.id ? '1px solid #7ec8e3' : '1px solid #444',
              borderRadius: '3px',
              padding: '4px 10px',
              cursor: 'pointer',
              fontSize: '11px',
            }}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* Tile palette */}
      <TilePalette
        tool={tool as any}
        tilesets={tilesets}
        onSelectFloorTile={onSelectFloorTile}
        onSelectWallTile={onSelectWallTile}
        onSelectFurniturePreset={onSelectFurniturePreset}
        selectedFloorTile={selectedFloorTile}
        selectedWallTile={selectedWallTile}
        selectedFurniturePreset={selectedFurniturePreset}
      />
    </div>
  )
}
