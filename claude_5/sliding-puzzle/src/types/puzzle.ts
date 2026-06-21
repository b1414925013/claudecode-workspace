export type PuzzleSize = 3 | 4 | 5
export type GameMode = 'number' | 'image'
export type GameStatus = 'playing' | 'won' | 'solving' | 'solved'

export interface BestScoreData {
  moves: number
  time: number
}

export interface Move {
  index: number
  direction: 'up' | 'down' | 'left' | 'right'
}

export interface PuzzleState {
  board: number[]
  size: PuzzleSize
  mode: GameMode
  status: GameStatus
  moves: number
  timer: number
  isRunning: boolean
  bestScores: Record<string, BestScoreData>
  selectedImage: string | null
  isDarkMode: boolean
}
