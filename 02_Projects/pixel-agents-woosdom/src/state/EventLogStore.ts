import { EVENT_DEDUP_WINDOW_MS } from '../constants.ts'
import type { LogEntry } from '../types/EventLog.ts'

const MAX_ENTRIES = 200

type Listener = () => void

class EventLogStoreClass {
  private entries: LogEntry[] = []
  private nextId = 1
  private listeners: Set<Listener> = new Set()

  addEntry(entry: Omit<LogEntry, 'id' | 'timestamp'>): void {
    // Drop only identical action+detail for the same agent within a short dedup window.
    const lastEntryForAgent = [...this.entries].reverse().find(e => e.agentRole === entry.agentRole)
    const isSameAction = lastEntryForAgent?.action === entry.action
    const isSameDetail = lastEntryForAgent?.detail === entry.detail
    if (lastEntryForAgent && isSameAction && isSameDetail) {
      const elapsed = Date.now() - lastEntryForAgent.timestamp.getTime()
      if (elapsed < EVENT_DEDUP_WINDOW_MS) return // Silently drop identical consecutive logs within dedup window
    }

    this.entries.push({
      ...entry,
      id: this.nextId++,
      timestamp: new Date(),
    })
    if (this.entries.length > MAX_ENTRIES) {
      this.entries = this.entries.slice(-MAX_ENTRIES)
    }
    this.notify()
  }

  getEntries(): LogEntry[] {
    return this.entries
  }

  getEntriesForAgent(agentRole: string, limit = 10): LogEntry[] {
    return this.entries
      .filter(e => e.agentRole === agentRole)
      .slice(-limit)
  }

  getAgentEventCount(agentRole: string): number {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return this.entries.filter(
      e => e.agentRole === agentRole && e.timestamp >= today
    ).length
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  private notify(): void {
    for (const listener of this.listeners) {
      listener()
    }
  }
}

export const EventLogStore = new EventLogStoreClass()
