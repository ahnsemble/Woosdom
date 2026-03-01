import { findPath } from '../canvas/Pathfinding.ts'
import { CharacterState, BUBBLE_FADE_SEC } from '../canvas/types.ts'
import type { Character, TileType } from '../canvas/types.ts'
import type { RoomConfig } from '../config/LayoutTypes.ts'
import { EventLogStore } from '../state/EventLogStore.ts'
import { EVENT_EMOJI } from '../types/EventLog.ts'
import { READING_TOOLS } from '../shared/toolDefs.ts'

function findCharByRole(characters: Character[], role: string): Character | undefined {
  return characters.find(ch => ch.role === role)
}

function getDisplayName(characters: Character[], role: string): string {
  return characters.find(ch => ch.role === role)?.displayName ?? role
}

function walkCharToRoom(
  ch: Character,
  targetRoom: string,
  rooms: RoomConfig[],
  tileGrid: TileType[][],
  blockedTiles: Set<string>,
): void {
  const room = rooms.find(r => r.id === targetRoom)
  if (!room) return

  const targetCol = Math.floor((room.minCol + room.maxCol) / 2)
  const targetRow = Math.floor((room.minRow + room.maxRow) / 2)
  const path = findPath(ch.tileCol, ch.tileRow, targetCol, targetRow, tileGrid, blockedTiles)
  if (path.length === 0) return

  ch.path = path
  ch.moveProgress = 0
  ch.state = CharacterState.WALK
  ch.frame = 0
  ch.frameTimer = 0
  ch.isActive = false
}

export function setupIPCListeners(
  characters: Character[],
  tileGrid: TileType[][],
  blockedTiles: Set<string>,
  rooms: RoomConfig[],
  triggerPanelRefresh: () => void,
): () => void {
  const api = window.electronAPI
  if (!api) return () => { }

  const ipcCleanups: Array<() => void> = []
  const unsub1 = api.onVaultToHands((data) => {
    const brain = findCharByRole(characters, 'brain')
    if (!brain) return

    brain.bubbleType = 'communicating'
    brain.bubbleTimer = 8
    walkCharToRoom(brain, data.targetRoom, rooms, tileGrid, blockedTiles)
    EventLogStore.addEntry({
      agentRole: 'brain',
      agentDisplayName: 'Brain',
      emoji: EVENT_EMOJI.communicating,
      action: `to_hands.md dispatching to ${data.targetRoom}`,
    })
    triggerPanelRefresh()
  })
  if (typeof unsub1 === 'function') ipcCleanups.push(unsub1)

  const unsub2 = api.onVaultFromHands((data) => {
    let leadRole = 'foreman'
    if ((data.engine && String(data.engine).startsWith('codex')) || data.engine === 'claude_codex') leadRole = 'compute_lead'
    else if (data.engine && String(data.engine).startsWith('antigravity')) leadRole = 'scout_lead'

    const lead = findCharByRole(characters, leadRole)
    if (!lead) return

    lead.bubbleType = 'communicating'
    lead.bubbleTimer = 8
    walkCharToRoom(lead, 'brain', rooms, tileGrid, blockedTiles)
    EventLogStore.addEntry({
      agentRole: leadRole,
      agentDisplayName: lead.displayName,
      emoji: EVENT_EMOJI.communicating,
      action: 'Reporting to Brain HQ',
    })
    triggerPanelRefresh()
  })
  if (typeof unsub2 === 'function') ipcCleanups.push(unsub2)

  const unsub3 = api.onVaultToCodex(() => {
    const brain = findCharByRole(characters, 'brain')
    if (brain) {
      brain.bubbleType = 'communicating'
      brain.bubbleTimer = 8
      walkCharToRoom(brain, 'codex', rooms, tileGrid, blockedTiles)
    }
    for (const ch of characters) {
      if (ch.team === 'codex') {
        ch.isActive = true
        ch.currentTool = 'Compute'
      }
    }
    EventLogStore.addEntry({
      agentRole: 'compute_lead',
      agentDisplayName: getDisplayName(characters, 'compute_lead'),
      emoji: EVENT_EMOJI.active,
      action: 'Codex team activated — compute task received',
    })
    triggerPanelRefresh()
  })
  if (typeof unsub3 === 'function') ipcCleanups.push(unsub3)

  // v3 전용 이벤트 핸들러
  const unsubToCC = api.onVaultToCC(() => {
    const brain = findCharByRole(characters, 'brain')
    if (brain) {
      brain.bubbleType = 'communicating'
      brain.bubbleTimer = 8
      walkCharToRoom(brain, 'cc', rooms, tileGrid, blockedTiles)
    }
    const foreman = findCharByRole(characters, 'foreman')
    if (foreman) {
      foreman.bubbleType = 'communicating'
      foreman.bubbleTimer = 8
    }
    EventLogStore.addEntry({
      agentRole: 'foreman',
      agentDisplayName: getDisplayName(characters, 'foreman'),
      emoji: EVENT_EMOJI.communicating,
      action: 'CC dispatch received — to_claude_code.md',
    })
    triggerPanelRefresh()
  })
  if (typeof unsubToCC === 'function') ipcCleanups.push(unsubToCC)

  const unsubFromCC = api.onVaultFromCC(() => {
    const brain = findCharByRole(characters, 'brain')
    if (brain) {
      brain.bubbleType = 'done'
      brain.bubbleTimer = 3
    }
    for (const ch of characters) {
      if (ch.team === 'cc') {
        ch.isActive = false
        ch.currentTool = null
      }
    }
    EventLogStore.addEntry({
      agentRole: 'foreman',
      agentDisplayName: getDisplayName(characters, 'foreman'),
      emoji: EVENT_EMOJI.idle,
      action: 'CC team idle — from_claude_code.md',
    })
    triggerPanelRefresh()
  })
  if (typeof unsubFromCC === 'function') ipcCleanups.push(unsubFromCC)

  const unsubToAG = api.onVaultToAG(() => {
    const brain = findCharByRole(characters, 'brain')
    if (brain) {
      brain.bubbleType = 'communicating'
      brain.bubbleTimer = 8
      walkCharToRoom(brain, 'ag', rooms, tileGrid, blockedTiles)
    }
    const scoutLead = findCharByRole(characters, 'scout_lead')
    if (scoutLead) {
      scoutLead.bubbleType = 'communicating'
      scoutLead.bubbleTimer = 8
    }
    EventLogStore.addEntry({
      agentRole: 'scout_lead',
      agentDisplayName: getDisplayName(characters, 'scout_lead'),
      emoji: EVENT_EMOJI.communicating,
      action: 'AG dispatch received — to_antigravity.md',
    })
    triggerPanelRefresh()
  })
  if (typeof unsubToAG === 'function') ipcCleanups.push(unsubToAG)

  const unsubFromAG = api.onVaultFromAG(() => {
    const brain = findCharByRole(characters, 'brain')
    if (brain) {
      brain.bubbleType = 'done'
      brain.bubbleTimer = 3
    }
    for (const ch of characters) {
      if (ch.team === 'ag') {
        ch.isActive = false
        ch.currentTool = null
        ch.bubbleType = 'done'
        ch.bubbleTimer = 3
      }
    }
    EventLogStore.addEntry({
      agentRole: 'scout_lead',
      agentDisplayName: getDisplayName(characters, 'scout_lead'),
      emoji: EVENT_EMOJI.tool_done,
      action: 'AG team done — from_antigravity.md',
    })
    triggerPanelRefresh()
  })
  if (typeof unsubFromAG === 'function') ipcCleanups.push(unsubFromAG)

  const unsubFromCodex = api.onVaultFromCodex(() => {
    const brain = findCharByRole(characters, 'brain')
    if (brain) {
      brain.bubbleType = 'done'
      brain.bubbleTimer = 3
    }
    for (const ch of characters) {
      if (ch.team === 'codex') {
        ch.isActive = false
        ch.currentTool = null
        ch.bubbleType = 'done'
        ch.bubbleTimer = 3
      }
    }
    EventLogStore.addEntry({
      agentRole: 'compute_lead',
      agentDisplayName: getDisplayName(characters, 'compute_lead'),
      emoji: EVENT_EMOJI.tool_done,
      action: 'Codex team done — from_codex.md',
    })
    triggerPanelRefresh()
  })
  if (typeof unsubFromCodex === 'function') ipcCleanups.push(unsubFromCodex)

  const unsub4 = api.onVaultActiveContext(() => {
    const brain = findCharByRole(characters, 'brain')
    if (!brain) return

    brain.isActive = true
    brain.currentTool = 'Write'
    setTimeout(() => {
      brain.isActive = false
      brain.currentTool = null
    }, 10_000)
    EventLogStore.addEntry({
      agentRole: 'brain',
      agentDisplayName: 'Brain',
      emoji: EVENT_EMOJI.active,
      action: 'Context updated — writing',
    })
    triggerPanelRefresh()
  })
  if (typeof unsub4 === 'function') ipcCleanups.push(unsub4)

  const unsub5 = api.onAgentToolStart((data) => {
    const ch = findCharByRole(characters, data.agentRole)
    if (!ch) return

    ch.isActive = true
    ch.currentTool = data.toolName
    ch.bubbleType = READING_TOOLS.has(data.toolName) ? 'reading' : 'typing'
    ch.bubbleTimer = 999
    EventLogStore.addEntry({
      agentRole: data.agentRole,
      agentDisplayName: ch.displayName,
      emoji: READING_TOOLS.has(data.toolName) ? EVENT_EMOJI.reading : EVENT_EMOJI.tool_start,
      action: `Using ${data.toolName}`,
      detail: data.detail,
    })
    triggerPanelRefresh()
  })
  if (typeof unsub5 === 'function') ipcCleanups.push(unsub5)

  const unsub6 = api.onAgentToolDone((data) => {
    const ch = findCharByRole(characters, data.agentRole)
    if (!ch) return

    ch.currentTool = null
    ch.bubbleType = 'done'
    ch.bubbleTimer = 3
    EventLogStore.addEntry({
      agentRole: data.agentRole,
      agentDisplayName: ch.displayName,
      emoji: EVENT_EMOJI.tool_done,
      action: 'Tool completed',
    })
    triggerPanelRefresh()
  })
  if (typeof unsub6 === 'function') ipcCleanups.push(unsub6)

  const unsub7 = api.onAgentStatus((data) => {
    const ch = findCharByRole(characters, data.agentRole)
    if (!ch) return

    if (data.status === 'idle') {
      ch.isActive = false
      ch.currentTool = null
      if (ch.bubbleType && ch.bubbleType !== 'done' && ch.bubbleType !== 'error') {
        ch.bubbleTimer = Math.min(ch.bubbleTimer, BUBBLE_FADE_SEC)
      }
      EventLogStore.addEntry({
        agentRole: data.agentRole,
        agentDisplayName: ch.displayName,
        emoji: EVENT_EMOJI.idle,
        action: 'Idle',
      })
    } else if (data.status === 'active') {
      ch.isActive = true
      EventLogStore.addEntry({
        agentRole: data.agentRole,
        agentDisplayName: ch.displayName,
        emoji: EVENT_EMOJI.active,
        action: 'Active',
      })
    }
    triggerPanelRefresh()
  })
  if (typeof unsub7 === 'function') ipcCleanups.push(unsub7)

  return () => {
    for (const unsub of ipcCleanups) unsub()
  }
}
