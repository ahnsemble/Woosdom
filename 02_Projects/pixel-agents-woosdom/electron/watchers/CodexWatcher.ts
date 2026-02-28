import { watch, FSWatcher } from 'chokidar'
import * as path from 'node:path'
import type { EventBus } from './EventBus.ts'

let watcher: FSWatcher | null = null
let isActive = false

function mapFileToCodexAgent(filePath: string): string {
    const basename = path.basename(filePath)
    const ext = path.extname(filePath)

    // Quant: Python, data, math, backtest logic
    if (ext === '.py' || basename.includes('backtest') || basename.includes('data') ||
        basename.includes('quant') || basename.includes('calc')) return 'quant'

    // Backtester: test files, validation
    if (basename.includes('test') || basename.includes('Test') ||
        basename.includes('spec') || basename.includes('validate')) return 'backtester'

    // Builder: build, config, package, deps
    if (basename.includes('package') || basename.includes('config') ||
        basename.includes('build') || basename.includes('vite') ||
        basename.includes('tsconfig') || ext === '.json') return 'builder'

    // Compute Lead: default
    return 'compute_lead'
}

export function startCodexWatcher(eventBus: EventBus): () => void {
    console.log('[CodexWatcher] Initialized (inactive until Codex dispatch)')

    eventBus.on('vault:to-hands', (event) => {
        const eng = String(event.engine)
        if ((eng === 'codex' || eng === 'claude_codex') && !isActive) {
            isActive = true
            console.log('[CodexWatcher] Codex team activated — watching src/')
            const PROJECT_SRC = path.join(process.env.APP_ROOT!, 'src')

            watcher = watch(PROJECT_SRC, {
                persistent: true,
                ignoreInitial: true,
                depth: 5,
                ignored: ['**/node_modules/**', '**/.git/**', '**/dist/**'],
                awaitWriteFinish: { stabilityThreshold: 300, pollInterval: 100 },
            })

            watcher.on('change', (filePath: string) => {
                const agentRole = mapFileToCodexAgent(filePath)
                const toolName = path.extname(filePath) === '.py' ? 'Compute' : 'Edit'
                eventBus.emit({ type: 'codex:file-change', agentRole, toolName, filePath: path.basename(filePath) })
            })

            watcher.on('add', (filePath: string) => {
                const agentRole = mapFileToCodexAgent(filePath)
                eventBus.emit({ type: 'codex:file-change', agentRole, toolName: 'Create', filePath: path.basename(filePath) })
            })
        }
    })

    // to_codex.md 이벤트로도 활성화
    eventBus.on('vault:to-codex', () => {
        if (!isActive) {
            isActive = true
            console.log('[CodexWatcher] Codex team activated via to_codex.md')
            const PROJECT_SRC = path.join(process.env.APP_ROOT!, 'src')

            watcher = watch(PROJECT_SRC, {
                persistent: true,
                ignoreInitial: true,
                depth: 5,
                ignored: ['**/node_modules/**', '**/.git/**', '**/dist/**'],
                awaitWriteFinish: { stabilityThreshold: 300, pollInterval: 100 },
            })

            watcher.on('change', (filePath: string) => {
                const agentRole = mapFileToCodexAgent(filePath)
                const toolName = path.extname(filePath) === '.py' ? 'Compute' : 'Edit'
                eventBus.emit({ type: 'codex:file-change', agentRole, toolName, filePath: path.basename(filePath) })
            })

            watcher.on('add', (filePath: string) => {
                const agentRole = mapFileToCodexAgent(filePath)
                eventBus.emit({ type: 'codex:file-change', agentRole, toolName: 'Create', filePath: path.basename(filePath) })
            })
        }
    })

    eventBus.on('vault:from-hands', (event) => {
        const eng = String(event.engine)
        if ((eng === 'codex' || eng === 'claude_codex') && isActive) {
            isActive = false
            watcher?.close()
            watcher = null
            console.log('[CodexWatcher] Codex team deactivated')
        }
    })

    return () => { watcher?.close(); isActive = false }
}
