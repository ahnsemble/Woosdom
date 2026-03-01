import { createContext, useContext, useState, useCallback, useRef } from 'react'
import type { Character } from '../canvas/types.ts'

interface AppContextValue {
  selectedAgent: Character | null
  setSelectedAgent: (agent: Character | null) => void
  customizeMode: boolean
  setCustomizeMode: (mode: boolean) => void
  panelView: 'log' | 'agent'
  setPanelView: (view: 'log' | 'agent') => void
  charactersRef: React.MutableRefObject<Character[]>
  triggerPanelRefresh: () => void
  panelRefreshCounter: number
  editorTileClickRef: React.MutableRefObject<((col: number, row: number) => void) | null>
  refreshLayoutRef: React.MutableRefObject<(() => void) | null>
}

const AppContext = createContext<AppContextValue | null>(null)

export function AppContextProvider({ children }: { children: React.ReactNode }) {
  const [selectedAgent, setSelectedAgent] = useState<Character | null>(null)
  const [customizeMode, setCustomizeMode] = useState(false)
  const [panelView, setPanelView] = useState<'log' | 'agent'>('log')
  const [panelRefreshCounter, setPanelRefreshCounter] = useState(0)
  const charactersRef = useRef<Character[]>([])
  const editorTileClickRef = useRef<((col: number, row: number) => void) | null>(null)
  const refreshLayoutRef = useRef<(() => void) | null>(null)

  const triggerPanelRefresh = useCallback(() => {
    setPanelRefreshCounter(c => c + 1)
  }, [])

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
      editorTileClickRef,
      refreshLayoutRef,
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
