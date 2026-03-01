import { TILE_SIZE } from '../constants.ts'
import { getOfficeDimensions } from '../canvas/OfficeLayout.ts'
import { centerCamera } from '../canvas/Renderer.ts'
import type { RenderState } from '../canvas/Renderer.ts'
import type { Character } from '../canvas/types.ts'

export interface InputManagerOptions {
  customizeModeRef?: { current: boolean }
  editorTileClickRef?: { current: ((col: number, row: number) => void) | null }
}

export function setupInputHandlers(
  canvas: HTMLCanvasElement,
  renderState: RenderState,
  characters: Character[],
  setSelectedAgent: (agent: Character | null) => void,
  options?: InputManagerOptions,
): () => void {
  const getFitZoom = () => {
    const { cols, rows } = getOfficeDimensions()
    const w = canvas.parentElement?.clientWidth ?? window.innerWidth
    const h = canvas.parentElement?.clientHeight ?? window.innerHeight
    return Math.min(w / (cols * TILE_SIZE), h / (rows * TILE_SIZE))
  }

  let hasUserInteracted = false
  let hasInitialCenter = false

  const clampZoomToFitWithCameraScale = (fitZoom: number) => {
    if (renderState.zoom >= fitZoom) return

    const prevZoom = renderState.zoom
    if (prevZoom > 0) {
      const zoomRatio = fitZoom / prevZoom
      renderState.cameraX *= zoomRatio
      renderState.cameraY *= zoomRatio
    }
    renderState.zoom = fitZoom
  }

  renderState.zoom = getFitZoom()

  const resize = () => {
    const parent = canvas.parentElement
    if (parent) {
      canvas.width = parent.clientWidth
      canvas.height = parent.clientHeight
    } else {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    const fitZoom = getFitZoom()
    clampZoomToFitWithCameraScale(fitZoom)

    if (!hasInitialCenter && !hasUserInteracted) {
      const camera = centerCamera(canvas.width, canvas.height, renderState.zoom)
      renderState.cameraX = camera.cameraX
      renderState.cameraY = camera.cameraY
      hasInitialCenter = true
    }
  }

  const onWheel = (e: WheelEvent) => {
    e.preventDefault()
    hasUserInteracted = true

    const delta = e.deltaY > 0 ? -1 : 1
    const fitZoom = getFitZoom()
    renderState.zoom = Math.max(fitZoom, Math.min(8, renderState.zoom + delta))
    const camera = centerCamera(canvas.width, canvas.height, renderState.zoom)
    renderState.cameraX = camera.cameraX
    renderState.cameraY = camera.cameraY
  }

  const onClick = (e: MouseEvent) => {
    const rect = canvas.getBoundingClientRect()
    const worldX = (e.clientX - rect.left + renderState.cameraX) / renderState.zoom
    const worldY = (e.clientY - rect.top + renderState.cameraY) / renderState.zoom

    if (options?.customizeModeRef?.current && options.editorTileClickRef?.current) {
      const col = Math.floor(worldX / TILE_SIZE)
      const row = Math.floor(worldY / TILE_SIZE)
      options.editorTileClickRef.current(col, row)
      return
    }

    const sorted = [...characters].sort((a, b) => b.y - a.y)
    for (const ch of sorted) {
      const hitX = ch.x - TILE_SIZE
      const hitY = ch.y - TILE_SIZE * 2
      if (
        worldX >= hitX && worldX < hitX + TILE_SIZE * 2
        && worldY >= hitY && worldY < hitY + TILE_SIZE * 2
      ) {
        setSelectedAgent(ch)
        return
      }
    }

    setSelectedAgent(null)
  }

  resize()
  window.addEventListener('resize', resize)
  const resizeObserver = new ResizeObserver(resize)
  if (canvas.parentElement) resizeObserver.observe(canvas.parentElement)
  canvas.addEventListener('wheel', onWheel, { passive: false })
  canvas.addEventListener('click', onClick)

  return () => {
    window.removeEventListener('resize', resize)
    resizeObserver.disconnect()
    canvas.removeEventListener('wheel', onWheel)
    canvas.removeEventListener('click', onClick)
  }
}
