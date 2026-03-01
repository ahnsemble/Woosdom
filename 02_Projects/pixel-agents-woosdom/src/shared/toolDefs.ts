export const READING_TOOL_NAMES = [
  'Read',
  'Grep',
  'Glob',
  'LS',
  'ListDir',
  'WebFetch',
  'WebSearch',
] as const

export const READING_TOOLS = new Set<string>(READING_TOOL_NAMES)

export const ENGINEER_TOOLS = new Set<string>([
  'Edit',
  'Write',
  'MultiEdit',
  'Create',
  'InsertCodeBlock',
])

export const GITOPS_TOOLS = new Set<string>([
  'GitDiff',
  'GitLog',
  'GitCommit',
  'GitStatus',
])
