import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'node:path'
import fs from 'node:fs'
import { EventBus } from './watchers/EventBus.ts'
import { startVaultWatcher } from './watchers/VaultWatcher.ts'
import { startCCWatcher } from './watchers/CCWatcher.ts'
import { startAGWatcher } from './watchers/AGWatcher.ts'
import { startCodexWatcher } from './watchers/CodexWatcher.ts'
import { loadWindowState, saveWindowState, applyWindowState } from './windowState.ts'

const __dirname = path.dirname(__filename)

process.env.APP_ROOT = path.join(__dirname, '..')
const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

let mainWindow: BrowserWindow | null = null
const eventBus = new EventBus()
let cleanupVault: (() => void) | null = null
let cleanupCC: (() => void) | null = null
let cleanupAG: (() => void) | null = null
let cleanupCodex: (() => void) | null = null

function createWindow(): void {
  const savedState = loadWindowState()

  mainWindow = new BrowserWindow({
    width: savedState?.width ?? 1200,
    height: savedState?.height ?? 800,
    minWidth: 800,
    minHeight: 600,
    title: 'Pixel Agents Woosdom',
    backgroundColor: '#1a1a2e',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // Restore window position
  if (savedState) {
    applyWindowState(mainWindow, savedState)
  }

  if (VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }

  // Save window state on close/resize
  mainWindow.on('close', () => {
    if (mainWindow) saveWindowState(mainWindow)
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function forwardToRenderer(channel: string, data: unknown): void {
  if (mainWindow && !mainWindow.isDestroyed()) {
    console.log('[Main] Forwarding to renderer:', channel)
    mainWindow.webContents.send(channel, data)
  }
}

function mapToolToCCAgent(toolName: string, toolInput?: Record<string, unknown>): string {
  // GitOps: Bash에서 git 명령어
  if (toolName === 'Bash' || toolName === 'bash') {
    const cmd = String(toolInput?.command ?? toolInput?.cmd ?? '')
    if (/\bgit\b/.test(cmd)) return 'gitops'
  }

  // VaultKeeper: Obsidian vault 경로 접근
  if (toolInput) {
    const filePath = String(toolInput.path ?? toolInput.file_path ?? '')
    if (filePath.includes('Woosdom_Brain')) return 'vault_keeper'
  }

  // Engineer: 코드 작성/수정
  if (['Edit', 'Write', 'MultiEdit', 'Create', 'InsertCodeBlock'].includes(toolName)) return 'engineer'

  // Critic: 코드 읽기/검토
  if (['Read', 'Grep', 'Glob', 'LS', 'ListDir'].includes(toolName)) return 'critic'

  // GitOps: git 전용 도구
  if (['GitDiff', 'GitLog', 'GitCommit', 'GitStatus'].includes(toolName)) return 'gitops'

  // Foreman: 기본값
  return 'foreman'
}

let lastActiveAgentRole = 'foreman'

function setupEventForwarding(): void {
  // Vault events → Renderer
  eventBus.on('vault:to-hands', (event) => {
    forwardToRenderer('vault:to-hands', {
      engine: event.engine,
      targetRoom: event.targetRoom,
    })
  })

  eventBus.on('vault:from-hands', (event) => {
    forwardToRenderer('vault:from-hands', {
      engine: event.engine,
    })
  })

  eventBus.on('vault:to-codex', () => {
    forwardToRenderer('vault:to-codex', {})
  })

  eventBus.on('vault:active-context', () => {
    forwardToRenderer('vault:active-context', {})
  })

  // CC JSONL events → Renderer
  eventBus.on('cc:tool-start', (event) => {
    const agentRole = mapToolToCCAgent(
      event.toolName as string,
      event.toolInput as Record<string, unknown> | undefined
    )
    lastActiveAgentRole = agentRole
    forwardToRenderer('agent:tool-start', {
      agentRole,
      toolName: event.toolName,
    })
  })

  eventBus.on('cc:tool-done', () => {
    forwardToRenderer('agent:tool-done', {
      agentRole: lastActiveAgentRole,
    })
  })

  eventBus.on('cc:turn-end', () => {
    for (const role of ['foreman', 'engineer', 'critic', 'gitops', 'vault_keeper']) {
      forwardToRenderer('agent:status', { agentRole: role, status: 'idle' })
    }
  })

  eventBus.on('cc:idle', () => {
    for (const role of ['foreman', 'engineer', 'critic', 'gitops', 'vault_keeper']) {
      forwardToRenderer('agent:status', { agentRole: role, status: 'idle' })
    }
  })

  // AG & Codex File JSONL/Chokidar events → Renderer
  eventBus.on('ag:file-change', (event) => {
    forwardToRenderer('agent:tool-start', {
      agentRole: event.agentRole,
      toolName: `${event.toolName}: ${event.filePath}`,
    })
    setTimeout(() => {
      forwardToRenderer('agent:tool-done', { agentRole: event.agentRole as string })
    }, 1500)
  })

  eventBus.on('codex:file-change', (event) => {
    forwardToRenderer('agent:tool-start', {
      agentRole: event.agentRole,
      toolName: `${event.toolName}: ${event.filePath}`,
    })
    setTimeout(() => {
      forwardToRenderer('agent:tool-done', { agentRole: event.agentRole as string })
    }, 1500)
  })
}

// IPC: layout file I/O
const LAYOUT_PATH = path.join(process.env.APP_ROOT!, 'config', 'layout.json')

ipcMain.handle('layout:read', async () => {
  try {
    const data = fs.readFileSync(LAYOUT_PATH, 'utf-8')
    return JSON.parse(data)
  } catch (err) {
    console.error('[Main] Failed to read layout.json:', err)
    return null
  }
})

ipcMain.handle('layout:write', async (_event, layoutData: unknown) => {
  try {
    fs.mkdirSync(path.dirname(LAYOUT_PATH), { recursive: true })
    fs.writeFileSync(LAYOUT_PATH, JSON.stringify(layoutData, null, 2), 'utf-8')
    console.log('[Main] layout.json saved')
    return { success: true }
  } catch (err) {
    console.error('[Main] Failed to write layout.json:', err)
    return { success: false, error: String(err) }
  }
})

// IPC: renderer ready signal (guard against duplicate calls from HMR)
let watchersStarted = false
ipcMain.on('app:ready', () => {
  if (watchersStarted) {
    console.log('[Main] app:ready received again (HMR) — skipping duplicate init')
    return
  }
  watchersStarted = true
  console.log('[Main] Renderer is ready — starting watchers')
  setupEventForwarding()
  cleanupVault = startVaultWatcher(eventBus)
  cleanupCC = startCCWatcher(eventBus)
  cleanupAG = startAGWatcher(eventBus)
  cleanupCodex = startCodexWatcher(eventBus)
})

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  cleanupVault?.()
  cleanupCC?.()
  cleanupAG?.()
  cleanupCodex?.()
  eventBus.removeAllListeners()
  app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})
