import { createContext, useContext, useState, useCallback, useRef } from 'react'
import type { Character } from '../canvas/types.ts'

interface AppContextValue {
  selectedAgent: Character | null
  setSelectedAgent: (agent: Character | null) => void
  customizeMode: boolean
  setCustomizeMode: (mode: boolean) => void
  panelView: 'log' | 'agent'
  setPanelView: (view: 'log' | 'agent') => void
  // Imperative character list ref (updated by game loop, not React state)
  charactersRef: React.MutableRefObject<Character[]>
  // Trigger panel re-render (called on IPC events)
  triggerPanelRefresh: () => void
  panelRefreshCounter: number
}

const AppContext = createContext<AppContextValue | null>(null)

export function AppContextProvider({ children }: { children: React.ReactNode }) {
  const [selectedAgent, setSelectedAgent] = useState<Character | null>(null)
  const [customizeMode, setCustomizeMode] = useState(false)
  const [panelView, setPanelView] = useState<'log' | 'agent'>('log')
  const [panelRefreshCounter, setPanelRefreshCounter] = useState(0)
  const charactersRef = useRef<Character[]>([])

  const triggerPanelRefresh = useCallback(() => {
    setPanelRefreshCounter(c => c + 1)
  }, [])

  // When an agent is selected, switch to agent view
  const handleSelectAgent = useCallback((agent: Character | null) => {
    setSelectedAgent(agent)
    if (agent) {
      setPanelView('agent')
    } else {
      setPanelView('log')
    }
  }, [])

  return (
    <AppContext.Provider value={{
      selectedAgent,
      setSelectedAgent: handleSelectAgent,
      customizeMode,
      setCustomizeMode,
      panelView,
      setPanelView,
      charactersRef,
      triggerPanelRefresh,
      panelRefreshCounter,
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useAppContext(): AppContextValue {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useAppContext must be used inside AppContextProvider')
  return ctx
}
