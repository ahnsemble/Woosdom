import { useState, useEffect } from 'react'
import { useAppContext } from '../contexts/AppContext.tsx'
import { EventLogStore } from '../state/EventLogStore.ts'
import { EVENT_EMOJI } from '../types/EventLog.ts'

function relativeTime(date: Date): string {
  const diffSec = Math.floor((Date.now() - date.getTime()) / 1000)
  if (diffSec < 60) return '방금'
  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `${diffMin}분 전`
  return `${Math.floor(diffMin / 60)}시간 전`
}

function dot(active: boolean): string {
  return active ? '🟢' : '🔴'
}

export default function BrainHUD() {
  const { charactersRef, panelRefreshCounter } = useAppContext()
  const [tick, setTick] = useState(0)

  useEffect(() => {
    const unsub = EventLogStore.subscribe(() => setTick(t => t + 1))
    return unsub
  }, [])

  useEffect(() => {
    const id = setInterval(() => setTick(t => t + 1), 10_000)
    return () => clearInterval(id)
  }, [])

  // tick & panelRefreshCounter used only to trigger re-render
  void tick
  void panelRefreshCounter

  const characters = charactersRef.current
  const ccActive = characters.some(ch => ch.team === 'cc' && ch.isActive)
  const codexActive = characters.some(ch => ch.team === 'codex' && ch.isActive)
  const agActive = characters.some(ch => ch.team === 'ag' && ch.isActive)

  const activeCount = characters.filter(ch => ch.isActive).length
  const totalCount = characters.length

  const entries = EventLogStore.getEntries()
  const lastDispatch = [...entries].reverse().find(e => e.emoji === EVENT_EMOJI.communicating) ?? null

  return (
    <div style={{
      position: 'absolute',
      top: 8,
      left: 8,
      zIndex: 10,
      background: 'rgba(0,0,0,0.7)',
      borderRadius: 8,
      padding: '8px 12px',
      minWidth: 160,
      fontSize: 12,
      color: '#ccc',
      pointerEvents: 'none',
    }}>
      <div style={{ marginBottom: 4, color: '#e8a87c', fontWeight: 'bold', letterSpacing: 1 }}>
        Brain HUD
      </div>
      <div>
        CC {dot(ccActive)}&nbsp;&nbsp;Codex {dot(codexActive)}&nbsp;&nbsp;AG {dot(agActive)}
      </div>
      <div style={{ marginTop: 4 }}>
        에이전트: <span style={{ color: activeCount > 0 ? '#e8a87c' : '#ccc' }}>{activeCount}</span>/{totalCount}
      </div>
      {lastDispatch && (
        <div style={{ marginTop: 4 }}>
          마지막 디스패치:{' '}
          <span style={{ color: '#e8a87c' }}>{relativeTime(lastDispatch.timestamp)}</span>
        </div>
      )}
    </div>
  )
}
