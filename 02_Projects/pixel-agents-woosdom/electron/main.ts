import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'node:path'
import fs from 'node:fs'
import { EventBus } from './watchers/EventBus.ts'

process.stdout.on('error', (err) => {
  if (err.code === 'EIO' || err.code === 'EPIPE') return // 파이프 끊김 무시
  console.error('[Main] stdout error:', err)
})
process.stderr.on('error', (err) => {
  if (err.code === 'EIO' || err.code === 'EPIPE') return
})
import { startVaultWatcher } from './watchers/VaultWatcher.ts'
import { startCCWatcher } from './watchers/CCWatcher.ts'
import { startAGWatcher } from './watchers/AGWatcher.ts'
import { startCodexWatcher } from './watchers/CodexWatcher.ts'
import { loadWindowState, saveWindowState, applyWindowState } from './windowState.ts'
import { getVaultRoot } from './config/appConfig.ts'
import { ENGINEER_TOOLS, GITOPS_TOOLS, READING_TOOLS } from '../src/shared/toolDefs.ts'

const __dirname = path.dirname(__filename)

process.env.APP_ROOT = path.join(__dirname, '..')
const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

const HMR_DEBOUNCE_MS = 500
const AGENT_ROLES: string[] = ['foreman', 'engineer', 'critic', 'gitops', 'vault_keeper']
const FILE_CHANGE_TOOL_DONE_MS = 1500

let mainWindow: BrowserWindow | null = null
const eventBus = new EventBus()
let cleanupVault: (() => void) | null = null
let cleanupCC: (() => void) | null = null
let cleanupAG: (() => void) | null = null
let cleanupCodex: (() => void) | null = null
const vaultRoot = getVaultRoot()

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

function extractToolDetail(toolName: string, toolInput?: Record<string, unknown>): string | undefined {
  if (!toolInput) return undefined

  const pathValue = toolInput.path ?? toolInput.file_path ?? toolInput.filePath
  if (typeof pathValue === 'string' && pathValue.trim().length > 0) {
    return path.basename(pathValue.trim())
  }

  if (toolName === 'Bash' || toolName === 'bash') {
    const cmdValue = toolInput.command ?? toolInput.cmd
    if (typeof cmdValue === 'string' && cmdValue.trim().length > 0) {
      return cmdValue.trim()
    }
  }

  return undefined
}

function mapToolToCCAgent(toolName: string, configuredVaultRoot: string, toolInput?: Record<string, unknown>): string {
  // GitOps: Bash에서 git 명령어
  if (toolName === 'Bash' || toolName === 'bash') {
    const cmd = String(toolInput?.command ?? toolInput?.cmd ?? '')
    if (/\bgit\b/.test(cmd)) return 'gitops'
  }

  // VaultKeeper: configured vault 경로 접근
  if (toolInput) {
    const filePath = String(toolInput.path ?? toolInput.file_path ?? '')
    const normalizedFilePath = filePath.replace(/\\/g, '/')
    const normalizedVaultRoot = configuredVaultRoot.replace(/\\/g, '/')
    if (normalizedFilePath.includes(normalizedVaultRoot)) return 'vault_keeper'
  }

  // Engineer: 코드 작성/수정
  if (ENGINEER_TOOLS.has(toolName)) return 'engineer'

  // Critic: 코드 읽기/검토
  if (READING_TOOLS.has(toolName)) return 'critic'

  // GitOps: git 전용 도구
  if (GITOPS_TOOLS.has(toolName)) return 'gitops'

  // Foreman: 기본값
  return 'foreman'
}

let lastActiveAgentRole = 'foreman'

function setupEventForwarding(): void {
  // Vault events -> Renderer
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

  eventBus.on('vault:from-codex', () => {
    forwardToRenderer('vault:from-codex', {})
  })

  eventBus.on('vault:to-cc', () => {
    forwardToRenderer('vault:to-cc', {})
  })

  eventBus.on('vault:from-cc', () => {
    forwardToRenderer('vault:from-cc', {})
  })

  eventBus.on('vault:to-ag', () => {
    forwardToRenderer('vault:to-ag', {})
  })

  eventBus.on('vault:from-ag', () => {
    forwardToRenderer('vault:from-ag', {})
  })

  eventBus.on('vault:active-context', () => {
    forwardToRenderer('vault:active-context', {})
  })

  // CC JSONL events -> Renderer
  eventBus.on('cc:tool-start', (event) => {
    const agentRole = mapToolToCCAgent(
      event.toolName as string,
      vaultRoot,
      event.toolInput as Record<string, unknown> | undefined,
    )
    const detail = extractToolDetail(
      event.toolName as string,
      event.toolInput as Record<string, unknown> | undefined,
    )
    lastActiveAgentRole = agentRole
    forwardToRenderer('agent:tool-start', {
      agentRole,
      toolName: event.toolName,
      detail,
    })
  })

  eventBus.on('cc:tool-done', () => {
    forwardToRenderer('agent:tool-done', {
      agentRole: lastActiveAgentRole,
    })
  })

  eventBus.on('cc:turn-end', () => {
    for (const role of AGENT_ROLES) {
      forwardToRenderer('agent:status', { agentRole: role, status: 'idle' })
    }
  })

  eventBus.on('cc:idle', () => {
    for (const role of AGENT_ROLES) {
      forwardToRenderer('agent:status', { agentRole: role, status: 'idle' })
    }
  })

  // AG & Codex File JSONL/Chokidar events -> Renderer
  eventBus.on('ag:file-change', (event) => {
    forwardToRenderer('agent:tool-start', {
      agentRole: event.agentRole,
      toolName: event.toolName,
      detail: event.filePath,
    })
    setTimeout(() => {
      forwardToRenderer('agent:tool-done', { agentRole: event.agentRole as string })
    }, FILE_CHANGE_TOOL_DONE_MS)
  })

  eventBus.on('codex:file-change', (event) => {
    forwardToRenderer('agent:tool-start', {
      agentRole: event.agentRole,
      toolName: event.toolName,
      detail: event.filePath,
    })
    setTimeout(() => {
      forwardToRenderer('agent:tool-done', { agentRole: event.agentRole as string })
    }, FILE_CHANGE_TOOL_DONE_MS)
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
let appReadyDebounceTimer: ReturnType<typeof setTimeout> | null = null
ipcMain.on('app:ready', () => {
  if (watchersStarted) {
    console.log('[Main] app:ready received again (HMR) - skipping duplicate init')
    return
  }

  if (appReadyDebounceTimer) {
    clearTimeout(appReadyDebounceTimer)
  }

  appReadyDebounceTimer = setTimeout(() => {
    if (watchersStarted) return

    watchersStarted = true
    appReadyDebounceTimer = null
    console.log('[Main] Renderer is ready - starting watchers')
    console.log('[Main] Using vault root:', vaultRoot)
    setupEventForwarding()
    cleanupVault = startVaultWatcher(eventBus, vaultRoot)
    cleanupCC = startCCWatcher(eventBus)
    cleanupAG = startAGWatcher(eventBus)
    cleanupCodex = startCodexWatcher(eventBus)
  }, HMR_DEBOUNCE_MS)
})

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (appReadyDebounceTimer) {
    clearTimeout(appReadyDebounceTimer)
    appReadyDebounceTimer = null
  }
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
