import { watch } from 'chokidar'
import * as fs from 'node:fs'
import path from 'path'
import type { EventBus } from './EventBus.ts'

// Vault root = 레포 루트 
// process.env.APP_ROOT는 main.ts에서 pixel-agents-woosdom/ 로 설정됨
// pixel-agents-woosdom/ -> ../ = 02_Projects/ -> ../ = 레포 루트 = 볼트 루트
const VAULT_ROOT = process.env.WOOSDOM_VAULT
  ?? path.resolve(process.env.APP_ROOT!, '..', '..')

const WATCH_FILES = [
  path.join(VAULT_ROOT, '00_System/Templates/from_hands.md'),
  path.join(VAULT_ROOT, '00_System/Templates/to_codex.md'),
  path.join(VAULT_ROOT, '00_System/Prompts/Ontology/active_context.md'),
]

/** Set of basenames we care about */
const WATCH_BASENAMES = new Set(WATCH_FILES.map(p => path.basename(p)))

/** Map basename → full path for reading */
const BASENAME_TO_PATH = new Map(WATCH_FILES.map(p => [path.basename(p), p]))

/** Unique parent directories to watch */
const WATCH_DIRS = [...new Set(WATCH_FILES.map(p => path.dirname(p)))]

/** Parse YAML frontmatter engine field */
function parseEngine(content: string): string | null {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/)
  if (!match) return null
  const frontmatter = match[1]
  const engineMatch = frontmatter.match(/engine:\s*["']?(\w+)["']?/)
  return engineMatch ? engineMatch[1] : null
}

export function startVaultWatcher(eventBus: EventBus): () => void {
  console.log('[VaultWatcher] Starting vault file watcher for dirs:', WATCH_DIRS)

  // Watch parent directories instead of individual files for reliable macOS detection
  const watcher = watch(WATCH_DIRS, {
    persistent: true,
    ignoreInitial: true,
    depth: 0,
    awaitWriteFinish: {
      stabilityThreshold: 500,
      pollInterval: 100,
    },
  })

  watcher.on('change', (filePath: string) => {
    const basename = path.basename(filePath)
    if (!WATCH_BASENAMES.has(basename)) return

    console.log(`[VaultWatcher] File changed: ${basename}`)

    // Use the canonical path for reading (in case chokidar returns a different path format)
    const readPath = BASENAME_TO_PATH.get(basename) ?? filePath

    try {
      switch (basename) {
        case 'to_hands.md': {
          const content = fs.readFileSync(readPath, 'utf-8')
          const engine = parseEngine(content)
          const targetRoom = engine === 'codex' || engine === 'claude_codex'
            ? 'codex'
            : engine?.startsWith('antigravity')
              ? 'ag'
              : 'cc'

          eventBus.emit({
            type: 'vault:to-hands',
            engine: engine ?? 'unknown',
            targetRoom,
            content,
          })
          console.log(`[VaultWatcher] to_hands.md → engine=${engine ?? 'unknown'}, room=${targetRoom}`)
          break
        }
        case 'from_hands.md': {
          const content = fs.readFileSync(readPath, 'utf-8')
          const engine = parseEngine(content)
          eventBus.emit({
            type: 'vault:from-hands',
            engine: engine ?? 'unknown',
            content,
          })
          console.log(`[VaultWatcher] from_hands.md → engine=${engine}`)
          break
        }
        case 'to_codex.md': {
          eventBus.emit({ type: 'vault:to-codex' })
          console.log(`[VaultWatcher] to_codex.md changed`)
          break
        }
        case 'active_context.md': {
          eventBus.emit({ type: 'vault:active-context' })
          console.log(`[VaultWatcher] active_context.md changed`)
          break
        }
      }
    } catch (err) {
      console.error(`[VaultWatcher] Error processing ${basename}:`, err)
    }
  })

  watcher.on('ready', () => {
    console.log('[VaultWatcher] Watcher ready — monitoring', WATCH_DIRS.length, 'directories')
  })

  watcher.on('error', (err) => {
    console.error('[VaultWatcher] Watcher error:', err)
  })

  return () => {
    watcher.close()
  }
}
