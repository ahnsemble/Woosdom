import type { LayoutConfig } from '../config/LayoutTypes.ts'

export const EditorTool = {
  FLOOR_PAINT: 'floor_paint',
  WALL_PAINT: 'wall_paint',
  FURNITURE_PLACE: 'furniture_place',
  ERASE: 'erase',
} as const
export type EditorTool = (typeof EditorTool)[keyof typeof EditorTool]

export interface SelectedTile {
  sx: number
  sy: number
  tilesetIdx?: number
}

export interface EditorState {
  active: boolean
  tool: EditorTool
  selectedFloorTile: SelectedTile | null
  selectedWallTile: SelectedTile | null
  selectedFurniturePreset: string | null
  ghostCol: number
  ghostRow: number
  isDragging: boolean
  isDirty: boolean
  workingLayout: LayoutConfig | null
  originalLayout: LayoutConfig | null
}

export function createEditorState(): EditorState {
  return {
    active: false,
    tool: EditorTool.FLOOR_PAINT,
    selectedFloorTile: null,
    selectedWallTile: null,
    selectedFurniturePreset: null,
    ghostCol: -1,
    ghostRow: -1,
    isDragging: false,
    isDirty: false,
    workingLayout: null,
    originalLayout: null,
  }
}
