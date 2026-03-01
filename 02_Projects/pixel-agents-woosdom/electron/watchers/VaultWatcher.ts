import { watch } from 'chokidar'
import * as fs from 'node:fs'
import * as path from 'node:path'
import type { EventBus } from './EventBus.ts'

function safeLog(...args: unknown[]) {
  try { safeLog(...args) } catch { /* EIO/EPIPE 무시 */ }
}
function safeError(...args: unknown[]) {
  try { safeError(...args) } catch { /* EIO/EPIPE 무시 */ }
}

function buildWatchFiles(vaultRoot: string): string[] {
  return [
    path.join(vaultRoot, '00_System', 'Templates', 'to_hands.md'),
    path.join(vaultRoot, '00_System', 'Templates', 'from_hands.md'),
    path.join(vaultRoot, '00_System', 'Templates', 'to_codex.md'),
    path.join(vaultRoot, '00_System', 'Templates', 'from_codex.md'),
    path.join(vaultRoot, '00_System', 'Templates', 'to_claude_code.md'),
    path.join(vaultRoot, '00_System', 'Templates', 'from_claude_code.md'),
    path.join(vaultRoot, '00_System', 'Templates', 'to_antigravity.md'),
    path.join(vaultRoot, '00_System', 'Templates', 'from_antigravity.md'),
    path.join(vaultRoot, '00_System', 'Prompts', 'Ontology', 'active_context.md'),
  ]
}

/** Parse YAML frontmatter engine field */
function parseEngine(content: string): string | null {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/)
  if (!match) return null
  const frontmatter = match[1]
  const engineMatch = frontmatter.match(/engine:\s*["']?(\w+)["']?/)
  return engineMatch ? engineMatch[1] : null
}

export function startVaultWatcher(eventBus: EventBus, vaultRoot: string): () => void {
  const watchFiles = buildWatchFiles(vaultRoot)

  /** Set of basenames we care about */
  const watchBasenames = new Set(watchFiles.map(p => path.basename(p)))

  /** Map basename -> full path for reading */
  const basenameToPath = new Map(watchFiles.map(p => [path.basename(p), p]))

  /** Unique parent directories to watch */
  const watchDirs = [...new Set(watchFiles.map(p => path.dirname(p)))]

  safeLog('[VaultWatcher] Starting vault file watcher for dirs:', watchDirs)

  // Watch parent directories instead of individual files for reliable macOS detection
  const watcher = watch(watchDirs, {
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
    if (!watchBasenames.has(basename)) return

    safeLog(`[VaultWatcher] File changed: ${basename}`)

    // Use the canonical path for reading (in case chokidar returns a different path format)
    const readPath = basenameToPath.get(basename) ?? filePath

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
          safeLog(`[VaultWatcher] to_hands.md -> engine=${engine ?? 'unknown'}, room=${targetRoom}`)
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
          safeLog(`[VaultWatcher] from_hands.md -> engine=${engine}`)
          break
        }
        case 'to_codex.md': {
          eventBus.emit({ type: 'vault:to-codex' })
          safeLog('[VaultWatcher] to_codex.md changed')
          break
        }
        case 'from_codex.md': {
          eventBus.emit({ type: 'vault:from-codex' })
          safeLog('[VaultWatcher] from_codex.md changed')
          break
        }
        case 'to_claude_code.md': {
          eventBus.emit({ type: 'vault:to-cc' })
          safeLog('[VaultWatcher] to_claude_code.md changed')
          break
        }
        case 'from_claude_code.md': {
          eventBus.emit({ type: 'vault:from-cc' })
          safeLog('[VaultWatcher] from_claude_code.md changed')
          break
        }
        case 'to_antigravity.md': {
          eventBus.emit({ type: 'vault:to-ag' })
          safeLog('[VaultWatcher] to_antigravity.md changed')
          break
        }
        case 'from_antigravity.md': {
          eventBus.emit({ type: 'vault:from-ag' })
          safeLog('[VaultWatcher] from_antigravity.md changed')
          break
        }
        case 'active_context.md': {
          eventBus.emit({ type: 'vault:active-context' })
          safeLog('[VaultWatcher] active_context.md changed')
          break
        }
      }
    } catch (err) {
      safeError(`[VaultWatcher] Error processing ${basename}:`, err)
    }
  })

  watcher.on('ready', () => {
    safeLog('[VaultWatcher] Watcher ready - monitoring', watchDirs.length, 'directories')
  })

  watcher.on('error', (err) => {
    safeError('[VaultWatcher] Watcher error:', err)
  })

  return () => {
    watcher.close()
  }
}
