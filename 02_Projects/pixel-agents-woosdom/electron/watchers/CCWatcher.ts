import { watch } from 'chokidar'
import * as fs from 'node:fs'
import * as os from 'node:os'
import * as path from 'node:path'
import type { EventBus } from './EventBus.ts'

const CLAUDE_PROJECTS_DIR = path.join(os.homedir(), '.claude', 'projects')

/** Track file read offsets for incremental reading */
const fileOffsets = new Map<string, number>()

/** Read only new lines appended since last read */
function readNewLines(filePath: string): string[] {
  try {
    const stat = fs.statSync(filePath)
    const currentOffset = fileOffsets.get(filePath) ?? 0

    if (stat.size <= currentOffset) {
      // File was truncated or no new data
      if (stat.size < currentOffset) {
        fileOffsets.set(filePath, 0)
      }
      return []
    }

    const fd = fs.openSync(filePath, 'r')
    const buffer = Buffer.alloc(stat.size - currentOffset)
    fs.readSync(fd, buffer, 0, buffer.length, currentOffset)
    fs.closeSync(fd)

    fileOffsets.set(filePath, stat.size)

    const text = buffer.toString('utf-8')
    // Split into lines, filter out incomplete last line (no newline)
    const lines = text.split('\n')
    if (!text.endsWith('\n') && lines.length > 0) {
      // Last line is incomplete, save offset to re-read it
      const incomplete = lines.pop()!
      fileOffsets.set(filePath, stat.size - Buffer.byteLength(incomplete, 'utf-8'))
    }

    return lines.filter(l => l.trim().length > 0)
  } catch {
    return []
  }
}

/** Process a single JSONL line and emit events */
function processLine(line: string, eventBus: EventBus): void {
  try {
    const record = JSON.parse(line)

    // Assistant message with tool_use blocks
    if (record.type === 'assistant' && Array.isArray(record.message?.content)) {
      const blocks = record.message.content as Array<{
        type: string; id?: string; name?: string; input?: Record<string, unknown>
      }>

      for (const block of blocks) {
        if (block.type === 'tool_use' && block.name) {
          eventBus.emit({
            type: 'cc:tool-start',
            toolName: block.name,
            toolId: block.id ?? '',
            toolInput: block.input ?? {},
          })
        }
      }
    }

    // User message with tool_result
    if (record.type === 'user') {
      const content = record.message?.content
      if (Array.isArray(content)) {
        const blocks = content as Array<{ type: string; tool_use_id?: string }>
        for (const block of blocks) {
          if (block.type === 'tool_result' && block.tool_use_id) {
            eventBus.emit({
              type: 'cc:tool-done',
              toolId: block.tool_use_id,
            })
          }
        }
      }
    }

    // Turn completed
    if (record.type === 'system' && record.subtype === 'turn_duration') {
      eventBus.emit({ type: 'cc:turn-end' })
    }
  } catch {
    // Ignore malformed lines
  }
}

export function startCCWatcher(eventBus: EventBus): () => void {
  console.log('[CCWatcher] Starting Claude Code JSONL watcher')

  const jsonlGlob = path.join(CLAUDE_PROJECTS_DIR, '**', '*.jsonl')

  const watcher = watch(jsonlGlob, {
    persistent: true,
    ignoreInitial: true,
    depth: 3,
    awaitWriteFinish: {
      stabilityThreshold: 200,
      pollInterval: 50,
    },
  })

  let idleTimer: ReturnType<typeof setTimeout> | null = null

  const resetIdleTimer = () => {
    if (idleTimer) clearTimeout(idleTimer)
    idleTimer = setTimeout(() => {
      eventBus.emit({ type: 'cc:idle' })
    }, 30_000) // 30s of no JSONL activity → all CC agents idle
  }

  watcher.on('change', (filePath: string) => {
    resetIdleTimer()

    const newLines = readNewLines(filePath)
    for (const line of newLines) {
      processLine(line, eventBus)
    }
  })

  watcher.on('add', (filePath: string) => {
    // New JSONL file created — new session
    console.log(`[CCWatcher] New JSONL: ${path.basename(filePath)}`)
    fileOffsets.set(filePath, 0)

    // Read initial content
    const stat = fs.statSync(filePath)
    fileOffsets.set(filePath, stat.size)
  })

  watcher.on('error', (err) => {
    console.error('[CCWatcher] Watcher error:', err)
  })

  return () => {
    if (idleTimer) clearTimeout(idleTimer)
    watcher.close()
  }
}
