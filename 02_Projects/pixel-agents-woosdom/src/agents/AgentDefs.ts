import type { AgentTeam } from '../canvas/types.ts'
import { getLayoutSync } from '../config/LayoutLoader.ts'

export interface AgentDefinition {
  id: number
  role: string
  displayName: string
  team: AgentTeam
  room: string
  seatId: string
  spriteRow: number
  spriteCol: number
}

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
