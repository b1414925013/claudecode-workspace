import type { PuzzleSize, Move } from '../types/puzzle'
import { usePuzzleLogic } from './usePuzzleLogic'

const DIRECTIONS: number[] = [0, 1, 2, 3]
const OPPOSITE: number[] = [1, 0, 3, 2]

interface Step {
  board: number[]
  move: number
}

export function useSolver() {
  const logic = usePuzzleLogic()
  let cancelled = false

  function cancel(): void { cancelled = true }
  function resetCancel(): void { cancelled = false }

  function buildManhattanTable(size: PuzzleSize): number[][] {
    const n = size * size
    const table: number[][] = Array.from({ length: n }, () => Array(n).fill(0))
    for (let v = 0; v < n; v++) {
      const goalRow = Math.floor(v / size)
      const goalCol = v % size
      for (let idx = 0; idx < n; idx++) {
        const curRow = Math.floor(idx / size)
        const curCol = idx % size
        table[v][idx] = Math.abs(curRow - goalRow) + Math.abs(curCol - goalCol)
      }
    }
    return table
  }

  function manhattan(board: number[], table: number[][]): number {
    let dist = 0
    for (let i = 0; i < board.length; i++) {
      if (board[i] !== 0) dist += table[board[i]][i]
    }
    return dist
  }

  function applyMove(board: number[], emptyIdx: number, tileIdx: number): number[] {
    const next = [...board]
    next[emptyIdx] = board[tileIdx]
    next[tileIdx] = 0
    return next
  }

  function solve(board: number[], size: PuzzleSize): number[] | null {
    cancelled = false
    const table = buildManhattanTable(size)
    const goal = logic.createSolvedBoard(size)
    const startH = manhattan(board, table)

    if (startH === 0) return []

    let bound = startH
    const maxBound = size === 3 ? 100 : size === 4 ? 120 : 80
    const path: Step[] = []

    while (bound <= maxBound) {
      if (cancelled) return null
      const result = search(board, logic.findEmpty(board), 0, bound, table, goal, size, path, -1)
      if (cancelled) return null
      if (result === 'FOUND') return path.map(s => s.move)
      if (result === Infinity) return null
      bound = result
    }
    return null
  }

  function search(
    board: number[], emptyIdx: number, g: number, bound: number,
    table: number[][], goal: number[], size: PuzzleSize,
    path: Step[], lastMoveDir: number,
  ): number | 'FOUND' {
    const f = g + manhattan(board, table)
    if (f > bound) return f
    if (board.every((v, i) => v === goal[i])) return 'FOUND'

    let min = Infinity
    const [er, ec] = [Math.floor(emptyIdx / size), emptyIdx % size]
    const neighborIndices: number[] = []
    const neighborDirs: number[] = []

    if (er > 0) { neighborIndices.push(emptyIdx - size); neighborDirs.push(0) }
    if (er < size - 1) { neighborIndices.push(emptyIdx + size); neighborDirs.push(1) }
    if (ec > 0) { neighborIndices.push(emptyIdx - 1); neighborDirs.push(2) }
    if (ec < size - 1) { neighborIndices.push(emptyIdx + 1); neighborDirs.push(3) }

    const scored = neighborIndices.map((ni, i) => ({
      ni, dir: neighborDirs[i],
      score: table[board[ni]][emptyIdx] - table[board[ni]][ni],
    }))
    scored.sort((a, b) => b.score - a.score)

    for (const { ni, dir } of scored) {
      if (dir === OPPOSITE[lastMoveDir]) continue
      const newBoard = applyMove(board, emptyIdx, ni)
      path.push({ board: newBoard, move: ni })
      const t = search(newBoard, ni, g + 1, bound, table, goal, size, path, dir)
      if (t === 'FOUND') return 'FOUND'
      if (t !== Infinity && t < min) min = t
      path.pop()
    }
    return min
  }

  return { solve, cancel, resetCancel }
}
