import { contextBridge, ipcRenderer } from 'electron'

/** Helper: register IPC listener and return cleanup function */
function onIpc<T>(channel: string, callback: (data: T) => void): () => void {
  const handler = (_event: Electron.IpcRendererEvent, data: T) => callback(data)
  ipcRenderer.on(channel, handler)
  return () => ipcRenderer.removeListener(channel, handler)
}

const electronAPI = {
  // Renderer -> Main
  sendReady: () => ipcRenderer.send('app:ready'),

  // Layout I/O
  readLayout: () => ipcRenderer.invoke('layout:read'),
  writeLayout: (data: unknown) => ipcRenderer.invoke('layout:write', data),

  // Main -> Renderer: Vault events (return cleanup functions)
  onVaultToHands: (callback: (data: { engine: string; targetRoom: string }) => void) => {
    return onIpc('vault:to-hands', callback)
  },
  onVaultFromHands: (callback: (data: { engine: string }) => void) => {
    return onIpc('vault:from-hands', callback)
  },
  onVaultToCodex: (callback: (data: Record<string, never>) => void) => {
    return onIpc('vault:to-codex', callback)
  },
  onVaultActiveContext: (callback: (data: Record<string, never>) => void) => {
    return onIpc('vault:active-context', callback)
  },

  // Main -> Renderer: CC Agent events
  onAgentToolStart: (callback: (data: { agentRole: string; toolName: string }) => void) => {
    return onIpc('agent:tool-start', callback)
  },
  onAgentToolDone: (callback: (data: { agentRole: string }) => void) => {
    return onIpc('agent:tool-done', callback)
  },
  onAgentStatus: (callback: (data: { agentRole: string; status: string }) => void) => {
    return onIpc('agent:status', callback)
  },
}

contextBridge.exposeInMainWorld('electronAPI', electronAPI)

export type ElectronAPI = typeof electronAPI
