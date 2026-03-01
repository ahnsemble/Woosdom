import { watch, FSWatcher } from 'chokidar'
import * as path from 'node:path'
import type { EventBus } from './EventBus.ts'

let watcher: FSWatcher | null = null
let isActive = false

function mapFileToAgAgent(filePath: string): string {
    const basename = path.basename(filePath)
    const ext = path.extname(filePath)

    if (basename.includes('layout') || basename.includes('Layout') ||
        basename.includes('config') || basename.includes('Type') ||
        ext === '.json') return 'architect'
    if (basename.includes('fetch') || basename.includes('api') ||
        basename.includes('search') || basename.includes('Scout')) return 'web_scout'
    if (basename.includes('test') || basename.includes('Test') ||
        basename.includes('experiment') || basename.includes('tmp')) return 'experiment'
    return 'scout_lead'
}

export function startAGWatcher(eventBus: EventBus): () => void {
    console.log('[AGWatcher] Initialized (inactive until AG dispatch)')

    function activateAG() {
        if (isActive) return
        isActive = true
        console.log('[AGWatcher] AG team activated — watching src/')
        const PROJECT_SRC = path.join(process.env.APP_ROOT!, 'src')

        watcher = watch(PROJECT_SRC, {
            persistent: true,
            ignoreInitial: true,
            depth: 5,
            ignored: ['**/node_modules/**', '**/.git/**', '**/dist/**'],
            awaitWriteFinish: { stabilityThreshold: 300, pollInterval: 100 },
        })

        watcher.on('change', (filePath: string) => {
            const agentRole = mapFileToAgAgent(filePath)
            const toolName = path.extname(filePath) === '.css' ? 'Style' :
                path.extname(filePath) === '.json' ? 'Configure' : 'Edit'
            eventBus.emit({ type: 'ag:file-change', agentRole, toolName, filePath: path.basename(filePath) })
        })

        watcher.on('add', (filePath: string) => {
            const agentRole = mapFileToAgAgent(filePath)
            eventBus.emit({ type: 'ag:file-change', agentRole, toolName: 'Create', filePath: path.basename(filePath) })
        })
    }

    function deactivateAG() {
        if (!isActive) return
        isActive = false
        watcher?.close()
        watcher = null
        console.log('[AGWatcher] AG team deactivated')
    }

    eventBus.on('vault:to-hands', (event) => {
        if (String(event.engine).startsWith('antigravity')) {
            activateAG()
        }
    })

    eventBus.on('vault:from-hands', (event) => {
        if (String(event.engine).startsWith('antigravity')) {
            deactivateAG()
        }
    })

    // v3 전용 이벤트
    eventBus.on('vault:to-ag', () => { activateAG() })
    eventBus.on('vault:from-ag', () => { deactivateAG() })

    return () => { watcher?.close(); isActive = false }
}
