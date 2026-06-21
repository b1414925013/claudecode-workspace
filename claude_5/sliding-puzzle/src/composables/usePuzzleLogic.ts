import type { PuzzleSize, Move } from '../types/puzzle'

export function usePuzzleLogic() {
  function createSolvedBoard(size: PuzzleSize): number[] {
    const len = size * size
    return Array.from({ length: len }, (_, i) => (i + 1) % len)
  }

  function findEmpty(board: number[]): number {
    return board.indexOf(0)
  }

  function getRowCol(index: number, size: PuzzleSize): [number, number] {
    return [Math.floor(index / size), index % size]
  }

  function isAdjacent(i1: number, i2: number, size: PuzzleSize): boolean {
    const [r1, c1] = getRowCol(i1, size)
    const [r2, c2] = getRowCol(i2, size)
    return Math.abs(r1 - r2) + Math.abs(c1 - c2) === 1
  }

  function getMoveDirection(emptyIdx: number, tileIdx: number, size: PuzzleSize): Move['direction'] {
    const [er, ec] = getRowCol(emptyIdx, size)
    const [tr, tc] = getRowCol(tileIdx, size)
    if (tr === er && tc === ec + 1) return 'left'
    if (tr === er && tc === ec - 1) return 'right'
    if (tc === ec && tr === er + 1) return 'up'
    return 'down'
  }

  function moveTile(board: number[], index: number, size: PuzzleSize): { newBoard: number[]; move: Move } | null {
    const emptyIdx = findEmpty(board)
    if (!isAdjacent(index, emptyIdx, size)) return null

    const direction = getMoveDirection(emptyIdx, index, size)
    const newBoard = [...board]
    newBoard[emptyIdx] = board[index]
    newBoard[index] = 0

    return { newBoard, move: { index, direction } }
  }

  function shuffle(board: number[], size: PuzzleSize, iterations: number = size * size * 50): number[] {
    let current = [...board]
    let lastEmpty = -1

    for (let i = 0; i < iterations; i++) {
      const emptyIdx = findEmpty(current)
      const neighbors = getNeighbors(emptyIdx, size).filter(n => n !== lastEmpty)
      if (neighbors.length === 0) continue
      const pick = neighbors[Math.floor(Math.random() * neighbors.length)]
      lastEmpty = emptyIdx
      const result = moveTile(current, pick, size)
      if (result) current = result.newBoard
    }

    const solved = createSolvedBoard(size)
    if (current.every((v, i) => v === solved[i])) {
      const nonEmpty = current.map((v, i) => v !== 0 ? i : -1).filter(i => i >= 0)
      if (nonEmpty.length >= 2) {
        const a = nonEmpty[0], b = nonEmpty[1]
        ;[current[a], current[b]] = [current[b], current[a]]
      }
    }

    return current
  }

  function getNeighbors(index: number, size: PuzzleSize): number[] {
    const [r, c] = getRowCol(index, size)
    const neighbors: number[] = []
    if (r > 0) neighbors.push(index - size)
    if (r < size - 1) neighbors.push(index + size)
    if (c > 0) neighbors.push(index - 1)
    if (c < size - 1) neighbors.push(index + 1)
    return neighbors
  }

  function isWin(board: number[], size: PuzzleSize): boolean {
    const solved = createSolvedBoard(size)
    return board.every((v, i) => v === solved[i])
  }

  function isSolvable(board: number[], size: PuzzleSize): boolean {
    const flat = board.filter(v => v !== 0)
    let inversions = 0
    for (let i = 0; i < flat.length; i++) {
      for (let j = i + 1; j < flat.length; j++) {
        if (flat[i] > flat[j]) inversions++
      }
    }
    if (size % 2 === 1) {
      return inversions % 2 === 0
    } else {
      const emptyIdx = findEmpty(board)
      const emptyRowFromBottom = size - Math.floor(emptyIdx / size)
      return (inversions + emptyRowFromBottom) % 2 === 0
    }
  }

  return { createSolvedBoard, findEmpty, getRowCol, isAdjacent, moveTile, shuffle, getNeighbors, isWin, isSolvable }
}
