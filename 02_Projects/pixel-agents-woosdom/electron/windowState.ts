import * as fs from 'node:fs'
import * as path from 'node:path'
import * as os from 'node:os'
import type { BrowserWindow } from 'electron'

interface WindowState {
  x: number
  y: number
  width: number
  height: number
  isMaximized: boolean
}

const STATE_DIR = path.join(os.homedir(), '.pixel-agents-woosdom')
const STATE_FILE = path.join(STATE_DIR, 'window-state.json')

export function loadWindowState(): WindowState | null {
  try {
    if (fs.existsSync(STATE_FILE)) {
      const data = fs.readFileSync(STATE_FILE, 'utf-8')
      return JSON.parse(data)
    }
  } catch {
    // Ignore corrupted state
  }
  return null
}

export function saveWindowState(win: BrowserWindow): void {
  try {
    const bounds = win.getBounds()
    const state: WindowState = {
      x: bounds.x,
      y: bounds.y,
      width: bounds.width,
      height: bounds.height,
      isMaximized: win.isMaximized(),
    }

    fs.mkdirSync(STATE_DIR, { recursive: true })
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2))
  } catch {
    // Ignore write errors
  }
}

export function applyWindowState(
  win: BrowserWindow,
  state: WindowState,
): void {
  win.setBounds({
    x: state.x,
    y: state.y,
    width: state.width,
    height: state.height,
  })
  if (state.isMaximized) {
    win.maximize()
  }
}
