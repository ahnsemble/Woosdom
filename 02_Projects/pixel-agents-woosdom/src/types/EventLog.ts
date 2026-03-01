/** Activity Log 이벤트 엔트리 */
export interface LogEntry {
  id: number
  timestamp: Date
  agentRole: string
  agentDisplayName: string
  emoji: string
  action: string
  detail?: string
}

/** 이벤트 타입별 이모지 매핑 */
export const EVENT_EMOJI: Record<string, string> = {
  tool_start: '\u2328\uFE0F',    // ⌨️
  tool_done: '\u2705',            // ✅
  idle: '\uD83D\uDCA4',          // 💤
  active: '\uD83D\uDD28',        // 🔨
  communicating: '\uD83D\uDCE1', // 📡
  reading: '\uD83D\uDCD6',       // 📖
  error: '\u274C',                // ❌
  vault_change: '\uD83D\uDCC2',  // 📂
}
