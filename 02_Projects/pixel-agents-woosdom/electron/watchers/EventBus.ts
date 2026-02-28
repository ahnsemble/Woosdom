export interface WoosdomEvent {
  type: string
  [key: string]: unknown
}

type EventListener = (event: WoosdomEvent) => void

export class EventBus {
  private listeners = new Map<string, Set<EventListener>>()

  on(type: string, listener: EventListener): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set())
    }
    this.listeners.get(type)!.add(listener)
    return () => {
      this.listeners.get(type)?.delete(listener)
    }
  }

  emit(event: WoosdomEvent): void {
    const typeListeners = this.listeners.get(event.type)
    if (typeListeners) {
      for (const listener of typeListeners) {
        listener(event)
      }
    }
    // Also emit to wildcard listeners
    const wildcardListeners = this.listeners.get('*')
    if (wildcardListeners) {
      for (const listener of wildcardListeners) {
        listener(event)
      }
    }
  }

  removeAllListeners(): void {
    this.listeners.clear()
  }
}
