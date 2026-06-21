import type { TileData, BoardSize, Direction } from '../types/game'

interface SlideRowResult {
  result: (TileData | null)[]
  score: number
  moved: boolean
}

export function useGameLogic() {
  let nextTileId = 1

  function generateId(): number {
    return nextTileId++
  }

  function resetIdCounter(maxId?: number): void {
    nextTileId = (maxId || 0) + 1
  }

  function shuffle<T>(arr: T[]): T[] {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]]
    }
    return arr
  }

  function createInitialTiles(size: BoardSize): TileData[] {
    const positions: [number, number][] = []
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        positions.push([r, c])
      }
    }
    shuffle(positions)

    const tiles: TileData[] = []
    for (let i = 0; i < 2; i++) {
      tiles.push({
        id: generateId(),
        value: Math.random() < 0.9 ? 2 : 4,
        row: positions[i][0],
        col: positions[i][1],
        isNew: true,
      })
    }
    return tiles
  }

  function slideRow(line: (TileData | null)[], size: number): SlideRowResult {
    const tiles = line.filter((t): t is TileData => t !== null)
    if (tiles.length === 0) {
      return { result: Array(size).fill(null), score: 0, moved: false }
    }

    const result: (TileData | null)[] = Array(size).fill(null)
    let score = 0
    let outputIdx = 0
    let i = 0

    while (i < tiles.length) {
      if (i + 1 < tiles.length && tiles[i].value === tiles[i + 1].value) {
        result[outputIdx] = {
          id: tiles[i].id,
          value: tiles[i].value * 2,
          row: tiles[i].row,
          col: outputIdx,
          isMerged: true,
        }
        score += tiles[i].value * 2
        i += 2
      } else {
        result[outputIdx] = {
          ...tiles[i],
          col: outputIdx,
          isNew: false,
          isMerged: false,
        }
        i++
      }
      outputIdx++
    }

    let moved = false
    for (let j = 0; j < size; j++) {
      const orig = line[j]
      const next = result[j]
      if (orig === null && next !== null) moved = true
      else if (orig !== null && next === null) moved = true
      else if (orig !== null && next !== null && orig.id !== next.id) moved = true
    }

    return { result, score, moved }
  }

  function dirCoords(dir: Direction, lineIdx: number, pos: number, size: number): { r: number; c: number } {
    switch (dir) {
      case 'left':  return { r: lineIdx, c: pos }
      case 'right': return { r: lineIdx, c: size - 1 - pos }
      case 'up':    return { r: pos, c: lineIdx }
      case 'down':  return { r: size - 1 - pos, c: lineIdx }
    }
  }

  function executeMove(tiles: TileData[], direction: Direction, size: BoardSize): {
    tiles: TileData[]
    score: number
    moved: boolean
  } {
    let totalScore = 0
    let anyMoved = false
    const newTiles: TileData[] = []

    for (let i = 0; i < size; i++) {
      const line: (TileData | null)[] = Array(size).fill(null)
      for (let j = 0; j < size; j++) {
        const { r, c } = dirCoords(direction, i, j, size)
        const tile = tiles.find(t => t.row === r && t.col === c)
        line[j] = tile || null
      }

      const { result, score, moved } = slideRow(line, size)
      totalScore += score
      if (moved) anyMoved = true

      for (let j = 0; j < size; j++) {
        const tile = result[j]
        if (tile) {
          const { r, c } = dirCoords(direction, i, j, size)
          newTiles.push({ ...tile, row: r, col: c })
        }
      }
    }

    return { tiles: newTiles, score: totalScore, moved: anyMoved }
  }

  function generateTile(tiles: TileData[], size: BoardSize): TileData {
    const occupied = new Set(tiles.map(t => `${t.row},${t.col}`))
    const empty: [number, number][] = []
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        if (!occupied.has(`${r},${c}`)) empty.push([r, c])
      }
    }
    const [row, col] = empty[Math.floor(Math.random() * empty.length)]
    return {
      id: generateId(),
      value: Math.random() < 0.9 ? 2 : 4,
      row,
      col,
      isNew: true,
    }
  }

  function checkWin(tiles: TileData[]): boolean {
    return tiles.some(t => t.value >= 2048)
  }

  function checkLose(tiles: TileData[], size: BoardSize): boolean {
    if (tiles.length < size * size) return false
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        const tile = tiles.find(t => t.row === r && t.col === c)
        if (!tile) return false
        const right = tiles.find(t => t.row === r && t.col === c + 1)
        if (right && right.value === tile.value) return false
        const down = tiles.find(t => t.row === r + 1 && t.col === c)
        if (down && down.value === tile.value) return false
      }
    }
    return true
  }

  function canMove(tiles: TileData[], size: BoardSize): boolean {
    if (tiles.length < size * size) return true
    return !checkLose(tiles, size)
  }

  return {
    createInitialTiles,
    executeMove,
    generateTile,
    checkWin,
    checkLose,
    canMove,
    resetIdCounter,
    shuffle,
  }
}
