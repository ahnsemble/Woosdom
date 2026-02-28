import type { AgentTeam } from '../canvas/types.ts'
import { getLayoutSync } from '../config/LayoutLoader.ts'

export interface AgentDefinition {
  id: number
  role: string
  displayName: string
  team: AgentTeam
  room: string
  seatId: string
  spriteRow: number  // row in 32x32folk sprite sheet
  spriteCol: number  // col in 32x32folk sprite sheet
}

/**
 * Load agent definitions from layout.json config.
 * 14 agents across 4 teams.
 * sprites.png = 384x256, RPG Maker VX format: 4 cols × 2 rows of character blocks.
 * Each block = 96×128px (3 frames × 4 directions of 32×32 sprites).
 * spriteCol/spriteRow = character BLOCK index (col 0-3, row 0-1).
 * 8 blocks total, 14 agents → some blocks are shared (differentiated by name labels).
 */
export function getAgentDefinitions(): AgentDefinition[] {
  const layout = getLayoutSync()
  return layout.agents.map(a => ({
    id: a.id,
    role: a.role,
    displayName: a.displayName,
    team: a.team as AgentTeam,
    room: a.room,
    seatId: a.seatId,
    spriteRow: a.spriteRow,
    spriteCol: a.spriteCol,
  }))
}

/** Legacy export — populated after layout load via initAgentDefinitions() */
export const AGENT_DEFINITIONS: AgentDefinition[] = []

/** Initialize AGENT_DEFINITIONS after layout is loaded */
export function initAgentDefinitions(): void {
  AGENT_DEFINITIONS.length = 0
  AGENT_DEFINITIONS.push(...getAgentDefinitions())
}
