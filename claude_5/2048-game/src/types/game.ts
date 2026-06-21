export interface TileData {
  id: number
  value: number
  row: number
  col: number
  isNew?: boolean
  isMerged?: boolean
}

export type BoardSize = 4 | 5 | 6
export type Direction = 'up' | 'down' | 'left' | 'right'
export type GameStatus = 'playing' | 'won' | 'lost'

export interface SerializedTile {
  id: number
  value: number
  row: number
  col: number
}

export interface StorageData {
  tiles: SerializedTile[]
  score: number
  boardSize: BoardSize
}

export interface GameState {
  tiles: TileData[]
  score: number
  bestScore: Record<BoardSize, number>
  status: GameStatus
  boardSize: BoardSize
  history: { tiles: TileData[]; score: number }[]
  isDarkMode: boolean
}
