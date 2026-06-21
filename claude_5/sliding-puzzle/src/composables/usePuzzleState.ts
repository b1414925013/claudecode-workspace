import { reactive, onUnmounted } from 'vue'
import type { PuzzleSize, GameMode, PuzzleState } from '../types/puzzle'
import { usePuzzleLogic } from './usePuzzleLogic'
import { useSolver } from './useSolver'
import { useStorage } from './useStorage'
import presets from '../assets/presets'

export function usePuzzleState() {
  const logic = usePuzzleLogic()
  const solver = useSolver()
  const storage = useStorage()

  const savedDark = storage.loadDarkMode()
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const initialDark = savedDark !== null ? savedDark : prefersDark
  if (initialDark) document.documentElement.classList.add('dark')

  const state = reactive<PuzzleState>({
    board: [],
    size: 4,
    mode: 'number',
    status: 'playing',
    moves: 0,
    timer: 0,
    isRunning: false,
    bestScores: storage.loadBestScore(),
    selectedImage: null,
    isDarkMode: initialDark,
  })

  let timerInterval: ReturnType<typeof setInterval> | null = null
  let inputLocked = false
  let mSolverPath: number[] = []
  let mSolverStep = 0
  let solverTimers: ReturnType<typeof setTimeout>[] = []

  function startTimer() {
    if (timerInterval) return
    state.isRunning = true
    timerInterval = setInterval(() => { state.timer++ }, 1000)
  }

  function stopTimer() {
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
    state.isRunning = false
  }

  function initGame(size: PuzzleSize = state.size, mode: GameMode = state.mode): void {
    stopTimer()
    const solved = logic.createSolvedBoard(size)
    state.board = logic.shuffle(solved, size)
    state.size = size
    state.mode = mode
    state.status = 'playing'
    state.moves = 0
    state.timer = 0
    state.isRunning = false
    mSolverPath = []
    mSolverStep = 0
    inputLocked = false
    solver.cancel()
    solverTimers.forEach(t => clearTimeout(t))
    solverTimers = []
    storage.saveState({ board: state.board, moves: 0, timer: 0, size, mode, selectedImage: state.selectedImage })
  }

  function handleClick(index: number): void {
    if (state.status !== 'playing' || inputLocked || state.board[index] === 0) return

    const result = logic.moveTile(state.board, index, state.size)
    if (!result) return

    if (state.moves === 0) startTimer()

    state.board = result.newBoard
    state.moves++
    inputLocked = true
    setTimeout(() => { inputLocked = false }, 120)

    storage.saveState({ board: state.board, moves: state.moves, timer: state.timer, size: state.size, mode: state.mode, selectedImage: state.selectedImage })

    if (logic.isWin(state.board, state.size)) {
      stopTimer()
      state.status = 'won'
      storage.saveBestScore(state.size, state.moves, state.timer)
      state.bestScores = storage.loadBestScore()
    }
  }

  function shuffleBoard(): void {
    const solved = logic.createSolvedBoard(state.size)
    state.board = logic.shuffle(solved, state.size)
    state.moves = 0
    state.timer = 0
    state.status = 'playing'
    stopTimer()
    mSolverPath = []
    mSolverStep = 0
    storage.saveState({ board: state.board, moves: 0, timer: 0, size: state.size, mode: state.mode, selectedImage: state.selectedImage })
  }

  function startSolver(): void {
    if (state.status !== 'playing') return
    state.status = 'solving'
    mSolverPath = []
    mSolverStep = 0
    setTimeout(() => {
      const prevStatus = state.status
      const result = solver.solve(state.board, state.size)
      if (prevStatus !== 'solving') return
      if (result && result.length > 0) {
        mSolverPath = result
        mSolverStep = 0
        state.status = 'solved'
      } else {
        state.status = 'playing'
        alert('无法在合理时间内求解，请尝试打乱后重试。')
      }
    }, 50)
  }

  function applySolverStep(): void {
    if (mSolverStep >= mSolverPath.length) { state.status = 'won'; return }
    const moveIdx = mSolverPath[mSolverStep]
    const result = logic.moveTile(state.board, moveIdx, state.size)
    if (result) {
      state.board = result.newBoard
      state.moves++
      mSolverStep++
    }
    if (mSolverStep >= mSolverPath.length) {
      state.status = 'won'
      stopTimer()
      storage.saveBestScore(state.size, state.moves, state.timer)
      state.bestScores = storage.loadBestScore()
    }
  }

  function closeSolver(): void { state.status = 'playing' }

  function toggleDarkMode(): void {
    state.isDarkMode = !state.isDarkMode
    document.documentElement.classList.toggle('dark', state.isDarkMode)
    storage.saveDarkMode(state.isDarkMode)
  }

  function toggleMode(): void {
    if (state.mode === 'image') {
      initGame(state.size, 'number')
    } else {
      if (!state.selectedImage) {
        state.selectedImage = presets[0].url
        initGame(state.size, 'image')
        return
      }
      initGame(state.size, 'image')
    }
  }

  function setImage(url: string | null): void {
    state.selectedImage = url
    state.mode = 'image'
    if (url) storage.saveImageData(url)
    initGame(state.size, 'image')
  }

  function restoreOrInit(): void {
    const saved = storage.loadState()
    if (saved && Array.isArray(saved.board) && saved.board.length > 0) {
      state.board = saved.board as number[]
      state.moves = saved.moves as number
      state.timer = saved.timer as number
      state.size = saved.size as PuzzleSize
      state.mode = saved.mode as GameMode
      state.selectedImage = saved.selectedImage as string | null
      state.status = 'playing'
      state.bestScores = storage.loadBestScore()
      if (state.moves > 0 && !logic.isWin(state.board, state.size)) startTimer()
    } else {
      initGame(4)
    }
  }

  onUnmounted(() => {
    stopTimer()
    solver.cancel()
    solverTimers.forEach(t => clearTimeout(t))
  })

  return {
    state,
    mSolverPath,
    mSolverStep,
    initGame,
    handleClick,
    shuffleBoard,
    startSolver,
    applySolverStep: () => { applySolverStep(); return { solverPath: mSolverPath, solverStep: mSolverStep } },
    closeSolver,
    toggleDarkMode,
    toggleMode,
    setImage,
    restoreOrInit,
  }
}
