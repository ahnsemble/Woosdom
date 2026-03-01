export interface LoadedAssets {
  spritesImg: HTMLImageElement
  tilesets: HTMLImageElement[]
}

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

function loadOptionalTileset(src: string, label: string): Promise<HTMLImageElement | null> {
  return loadImage(src).catch((err) => {
    console.warn(`[AssetLoader] Failed to load tileset: ${label}`, err)
    return null
  })
}

export async function loadAssets(): Promise<LoadedAssets> {
  const [spritesImg, ...loadedTilesets] = await Promise.all([
    loadImage(new URL('../assets/sprites.png', import.meta.url).href),
    loadImage(new URL('../assets/tileset.png', import.meta.url).href),
    loadOptionalTileset(new URL('../assets/tileset2.png', import.meta.url).href, 'tileset2.png'),
    loadOptionalTileset(new URL('../assets/tilesets/vx_ace/A2 Office Floors.png', import.meta.url).href, 'A2 Office Floors.png'),
    loadOptionalTileset(new URL('../assets/tilesets/vx_ace/A4 Office Walls.png', import.meta.url).href, 'A4 Office Walls.png'),
    loadOptionalTileset(new URL('../assets/tilesets/vx_ace/A5 Office Floors & Walls.png', import.meta.url).href, 'A5 Office Floors & Walls.png'),
    loadOptionalTileset(new URL('../assets/tilesets/vx_ace/B-C-D-E Office 1 No Shadows.png', import.meta.url).href, 'B-C-D-E Office 1 No Shadows.png'),
    loadOptionalTileset(new URL('../assets/tilesets/vx_ace/B-C-D-E Office 2 No Shadows.png', import.meta.url).href, 'B-C-D-E Office 2 No Shadows.png'),
  ])

  return {
    spritesImg,
    tilesets: loadedTilesets.filter(Boolean) as HTMLImageElement[],
  }
}
