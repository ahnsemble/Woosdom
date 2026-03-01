import { useState } from 'react'
import OfficeCanvas from './OfficeCanvas.tsx'
import ActivityLogPanel from './ActivityLogPanel.tsx'
import AgentDetailPanel from './AgentDetailPanel.tsx'
import EditorToolbar from './EditorToolbar.tsx'
import BrainHUD from './BrainHUD.tsx'
import { useAppContext } from '../contexts/AppContext.tsx'
import { useEditor } from '../editor/useEditor.ts'

export default function AppLayout() {
  const {
    panelView,
    selectedAgent,
    customizeMode,
    setCustomizeMode,
    editorTileClickRef,
    refreshLayoutRef,
  } = useAppContext()

  const [panelOpen, setPanelOpen] = useState(true)

  const {
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
  } = useEditor({
    customizeMode,
    setCustomizeMode,
    editorTileClickRef,
    refreshLayoutRef,
  })

  return (
    <div style={{
      display: 'flex',
      width: '100vw',
      height: '100vh',
      overflow: 'hidden',
      background: '#1a1a2e',
    }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <div style={{ flex: 1, position: 'relative', minHeight: 0 }}>
          <OfficeCanvas />
          {!customizeMode && <BrainHUD />}

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
