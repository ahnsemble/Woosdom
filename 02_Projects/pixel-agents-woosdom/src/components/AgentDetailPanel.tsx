import { useEffect, useRef, useState } from 'react'
import type { Character } from '../canvas/types.ts'
import { CharacterState } from '../canvas/types.ts'
import { EventLogStore } from '../state/EventLogStore.ts'
import type { LogEntry } from '../types/EventLog.ts'
import { useAppContext } from '../contexts/AppContext.tsx'

const STATE_LABELS: Record<number, string> = {
  [CharacterState.IDLE]: 'Idle',
  [CharacterState.WALK]: 'Walking',
  [CharacterState.TYPE]: 'Typing',
}

function formatTime(date: Date): string {
  const h = String(date.getHours()).padStart(2, '0')
  const m = String(date.getMinutes()).padStart(2, '0')
  return `${h}:${m}`
}

function timeSince(date: Date): string {
  const secs = Math.floor((Date.now() - date.getTime()) / 1000)
  if (secs < 60) return `${secs}s ago`
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  return `${Math.floor(secs / 3600)}h ago`
}

interface SpritePreviewProps {
  character: Character
  spritesImg: HTMLImageElement | null
}

function SpritePreview({ character, spritesImg }: SpritePreviewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!canvasRef.current || !spritesImg) return
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return

    const SPRITE_W = 32
    const SPRITE_H = 32
    const BLOCK_W = 96
    const BLOCK_H = 128
    const SCALE = 2

    canvasRef.current.width = SPRITE_W * SCALE
    canvasRef.current.height = SPRITE_H * SCALE

    ctx.imageSmoothingEnabled = false
    const blockX = character.spriteCol * BLOCK_W
    const blockY = character.spriteRow * BLOCK_H
    // Standing pose (frame 0), facing down (row 0)
    ctx.drawImage(
      spritesImg,
      blockX, blockY, SPRITE_W, SPRITE_H,
      0, 0, SPRITE_W * SCALE, SPRITE_H * SCALE,
    )
  }, [character, spritesImg])

  return <canvas ref={canvasRef} style={{ imageRendering: 'pixelated' }} />
}

export default function AgentDetailPanel() {
  const { selectedAgent, setSelectedAgent, panelRefreshCounter } = useAppContext()
  const [recentLogs, setRecentLogs] = useState<LogEntry[]>([])
  const [eventCount, setEventCount] = useState(0)
  const [spritesImg, setSpritesImg] = useState<HTMLImageElement | null>(null)

  // Load sprites image once
  useEffect(() => {
    const img = new Image()
    img.onload = () => setSpritesImg(img)
    img.src = new URL('../assets/sprites.png', import.meta.url).href
  }, [])

  // Update logs when agent changes or refresh triggers
  useEffect(() => {
    if (!selectedAgent) return
    setRecentLogs(EventLogStore.getEntriesForAgent(selectedAgent.role, 10))
    setEventCount(EventLogStore.getAgentEventCount(selectedAgent.role))
  }, [selectedAgent, panelRefreshCounter])

  // Periodic refresh for "time since" display
  useEffect(() => {
    const interval = setInterval(() => {
      if (!selectedAgent) return
      setRecentLogs(EventLogStore.getEntriesForAgent(selectedAgent.role, 10))
      setEventCount(EventLogStore.getAgentEventCount(selectedAgent.role))
    }, 2000)
    return () => clearInterval(interval)
  }, [selectedAgent])

  if (!selectedAgent) return null

  const lastLog = recentLogs[recentLogs.length - 1]
  const teamColors: Record<string, string> = {
    cc: '#e8a87c',
    codex: '#7ec8e3',
    ag: '#82b74b',
    brain: '#c5b9cd',
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: '#1a1a2e',
      color: '#e0e0e0',
    }}>
      {/* Header */}
      <div style={{
        padding: '12px',
        borderBottom: '1px solid #333',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}>
        <SpritePreview character={selectedAgent} spritesImg={spritesImg} />
        <div>
          <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
            {selectedAgent.displayName}
          </div>
          <div style={{
            fontSize: '11px',
            color: teamColors[selectedAgent.team] ?? '#aaa',
            marginTop: '2px',
          }}>
            {selectedAgent.role} / {selectedAgent.team.toUpperCase()} Team
          </div>
        </div>
        <button
          onClick={() => setSelectedAgent(null)}
          style={{
            marginLeft: 'auto',
            background: 'none',
            border: '1px solid #555',
            color: '#aaa',
            padding: '2px 8px',
            cursor: 'pointer',
            borderRadius: '3px',
            fontSize: '11px',
          }}
        >
          Close
        </button>
      </div>

      {/* Status */}
      <div style={{ padding: '10px 12px', borderBottom: '1px solid #333' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '12px' }}>
          <div>
            <span style={{ color: '#888' }}>Status: </span>
            <span>{STATE_LABELS[selectedAgent.state] ?? 'Unknown'}</span>
          </div>
          <div>
            <span style={{ color: '#888' }}>Room: </span>
            <span>{selectedAgent.room}</span>
          </div>
          {selectedAgent.currentTool && (
            <div>
              <span style={{ color: '#888' }}>Tool: </span>
              <span style={{ color: '#7ec8e3' }}>{selectedAgent.currentTool}</span>
            </div>
          )}
          <div>
            <span style={{ color: '#888' }}>Events: </span>
            <span>{eventCount}</span>
          </div>
          {lastLog && (
            <div style={{ gridColumn: '1 / -1' }}>
              <span style={{ color: '#888' }}>Last activity: </span>
              <span>{timeSince(lastLog.timestamp)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Recent Logs */}
      <div style={{
        flex: 1,
        overflow: 'auto',
        padding: '8px 12px',
      }}>
        <div style={{ color: '#888', fontSize: '11px', marginBottom: '6px', fontWeight: 'bold' }}>
          Recent Activity
        </div>
        {recentLogs.length === 0 ? (
          <div style={{ color: '#555', fontSize: '11px' }}>No activity yet</div>
        ) : (
          recentLogs.map(entry => (
            <div key={entry.id} style={{
              fontSize: '11px',
              fontFamily: 'monospace',
              padding: '2px 0',
              lineHeight: '16px',
            }}>
              <span style={{ color: '#666' }}>{formatTime(entry.timestamp)}</span>
              {' '}
              <span>{entry.emoji}</span>
              {' '}
              <span style={{ color: '#ccc' }}>{entry.action}</span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
