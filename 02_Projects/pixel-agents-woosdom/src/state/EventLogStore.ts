import type { LogEntry } from '../types/EventLog.ts'

const MAX_ENTRIES = 200

type Listener = () => void

class EventLogStoreClass {
  private entries: LogEntry[] = []
  private nextId = 1
  private listeners: Set<Listener> = new Set()

  addEntry(entry: Omit<LogEntry, 'id' | 'timestamp'>): void {
    // Only log if the action is different from the VERY LAST action recorded for this specific agent
    // OR if it's been more than 10 seconds since the last identical action
    const lastEntryForAgent = [...this.entries].reverse().find(e => e.agentRole === entry.agentRole)
    if (lastEntryForAgent && lastEntryForAgent.action === entry.action) {
      const elapsed = Date.now() - lastEntryForAgent.timestamp.getTime()
      if (elapsed < 10_000) return // Silently drop identical consecutive logs within 10s
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
