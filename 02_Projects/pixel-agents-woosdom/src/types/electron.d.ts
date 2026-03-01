export {}

declare global {
  interface Window {
    electronAPI?: import('../../electron/preload').ElectronAPI
  }
}
