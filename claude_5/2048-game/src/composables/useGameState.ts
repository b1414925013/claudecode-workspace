import { reactive } from 'vue'
import type { GameState, Direction } from '../types/game'
import { useGameLogic } from './useGameLogic'
import { useStorage } from './useStorage'

export function useGameState() {
  const logic = useGameLogic()
  const storage = useStorage()

  const savedDark = storage.loadDarkMode()
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const initialDark = savedDark !== null ? savedDark : prefersDark
  if (initialDark) document.documentElement.classList.add('dark')

  const state = reactive<GameState>({
    tiles: [],
    score: 0,
    bestScore: storage.loadBestScore(),
    status: 'playing',
    boardSize: 4,
    history: [],
    isDarkMode: initialDark,
  })

  let animationLocked = false

  function initGame(size: number = state.boardSize): void {
    const boardSize = size as 4 | 5 | 6
    state.tiles = logic.createInitialTiles(boardSize)
    state.score = 0
    state.boardSize = boardSize
    state.status = 'playing'
    state.history = []
    animationLocked = false
    storage.saveState({ tiles: state.tiles, score: state.score, boardSize: state.boardSize })
  }

  function restoreOrInit(): void {
    const saved = storage.loadState()
    if (saved && saved.tiles.length > 0 && saved.boardSize) {
      state.tiles = saved.tiles.map(t => ({ ...t, isNew: false, isMerged: false }))
      state.score = saved.score
      state.boardSize = saved.boardSize
      state.status = 'playing'
      state.history = []
      state.bestScore = storage.loadBestScore()
    } else {
      initGame(4)
    }
  }

  function handleMove(direction: Direction): void {
    if (state.status !== 'playing') return
    if (animationLocked) return

    state.history.push({
      tiles: state.tiles.map(t => ({ ...t, isNew: false, isMerged: false })),
      score: state.score,
    })
    if (state.history.length > 10) state.history.shift()

    const result = logic.executeMove(state.tiles, direction, state.boardSize)

    if (!result.moved) {
      state.history.pop()
      return
    }

    state.score += result.score
    state.tiles = result.tiles

    const spawnTile = logic.generateTile(state.tiles, state.boardSize)
    state.tiles.push(spawnTile)

    animationLocked = true
    setTimeout(() => { animationLocked = false }, 150)

    setTimeout(() => {
      state.tiles.forEach(t => { t.isNew = false; t.isMerged = false })
    }, 250)

    storage.saveState({ tiles: state.tiles, score: state.score, boardSize: state.boardSize })

    if (state.score > (state.bestScore[state.boardSize] || 0)) {
      state.bestScore[state.boardSize] = state.score
      storage.saveBestScore(state.boardSize, state.score)
    }

    if (logic.checkWin(state.tiles)) {
      state.status = 'won'
    } else if (logic.checkLose(state.tiles, state.boardSize)) {
      state.status = 'lost'
    }
  }

  function undo(): void {
    if (state.history.length === 0) return
    const last = state.history.pop()!
    state.tiles = last.tiles.map(t => ({ ...t, isNew: false, isMerged: false }))
    state.score = last.score
    state.status = 'playing'
    storage.saveState({ tiles: state.tiles, score: state.score, boardSize: state.boardSize })
  }

  function toggleDarkMode(): void {
    state.isDarkMode = !state.isDarkMode
    document.documentElement.classList.toggle('dark', state.isDarkMode)
    storage.saveDarkMode(state.isDarkMode)
  }

  function newGame(size?: number): void {
    const s = size || state.boardSize
    if (s !== state.boardSize) {
      state.bestScore = storage.loadBestScore()
    }
    initGame(s)
  }

  return {
    state,
    initGame,
    restoreOrInit,
    handleMove,
    undo,
    toggleDarkMode,
    newGame,
  }
}
