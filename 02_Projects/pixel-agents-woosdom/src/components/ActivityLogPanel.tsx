import { useEffect, useRef, useState } from 'react'
import { EventLogStore } from '../state/EventLogStore.ts'
import type { LogEntry } from '../types/EventLog.ts'
import { useAppContext } from '../contexts/AppContext.tsx'

function formatTime(date: Date): string {
  const h = String(date.getHours()).padStart(2, '0')
  const m = String(date.getMinutes()).padStart(2, '0')
  return `${h}:${m}`
}

export default function ActivityLogPanel() {
  const [entries, setEntries] = useState<LogEntry[]>(EventLogStore.getEntries())
  const listRef = useRef<HTMLDivElement>(null)
  const stickToBottom = useRef(true)
  const { setSelectedAgent, charactersRef } = useAppContext()

  useEffect(() => {
    return EventLogStore.subscribe(() => {
      setEntries([...EventLogStore.getEntries()])
    })
  }, [])

  // Auto-scroll
  useEffect(() => {
    if (stickToBottom.current && listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [entries])

  const handleScroll = () => {
    if (!listRef.current) return
    const { scrollTop, scrollHeight, clientHeight } = listRef.current
    stickToBottom.current = scrollHeight - scrollTop - clientHeight < 30
  }

  const handleAgentClick = (role: string) => {
    const ch = charactersRef.current.find(c => c.role === role)
    if (ch) setSelectedAgent(ch)
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: '#1a1a2e',
      color: '#e0e0e0',
    }}>
      <div style={{
        padding: '8px 12px',
        borderBottom: '1px solid #333',
        fontWeight: 'bold',
        fontSize: '13px',
        color: '#aaa',
      }}>
        Activity Log
      </div>
      <div
        ref={listRef}
        onScroll={handleScroll}
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '4px 8px',
          fontFamily: 'monospace',
          fontSize: '11px',
          lineHeight: '18px',
        }}
      >
        {entries.length === 0 && (
          <div style={{ color: '#666', padding: '20px', textAlign: 'center' }}>
            No events yet...
          </div>
        )}
        {entries.map(entry => (
          <div key={entry.id} style={{ padding: '1px 0' }}>
            <span style={{ color: '#666' }}>[{formatTime(entry.timestamp)}]</span>
            {' '}
            <span>{entry.emoji}</span>
            {' '}
            <span
              style={{
                color: '#7ec8e3',
                cursor: 'pointer',
                textDecoration: 'underline',
                textDecorationColor: 'transparent',
              }}
              onMouseEnter={e => (e.currentTarget.style.textDecorationColor = '#7ec8e3')}
              onMouseLeave={e => (e.currentTarget.style.textDecorationColor = 'transparent')}
              onClick={() => handleAgentClick(entry.agentRole)}
            >
              {entry.agentDisplayName}
            </span>
            {' \u2014 '}
            <span style={{ color: '#ccc' }}>{entry.action}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
