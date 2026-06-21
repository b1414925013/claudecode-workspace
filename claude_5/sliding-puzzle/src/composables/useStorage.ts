import type { PuzzleSize, PuzzleState } from '../types/puzzle'

const STATE_KEY = 'puzzle-game-state'
const BEST_KEY = 'puzzle-best-scores'
const DARK_KEY = 'puzzle-dark-mode'
const IMAGE_KEY = 'puzzle-image-data'

export function useStorage() {
  function isAvailable(): boolean {
    try {
      const k = '__test__'
      localStorage.setItem(k, '1')
      localStorage.removeItem(k)
      return true
    } catch {
      return false
    }
  }

  const available = isAvailable()

  function saveState(state: Pick<PuzzleState, 'board' | 'moves' | 'timer' | 'size' | 'mode' | 'selectedImage'>): void {
    if (!available) return
    try {
      localStorage.setItem(STATE_KEY, JSON.stringify(state))
    } catch { /* silent */ }
  }

  function loadState(): Record<string, unknown> | null {
    if (!available) return null
    try {
      const raw = localStorage.getItem(STATE_KEY)
      if (!raw) return null
      const parsed = JSON.parse(raw)
      if (!Array.isArray(parsed.board)) {
        localStorage.removeItem(STATE_KEY)
        return null
      }
      return parsed
    } catch {
      localStorage.removeItem(STATE_KEY)
      return null
    }
  }

  function clearState(): void {
    if (!available) return
    try { localStorage.removeItem(STATE_KEY) } catch { /* silent */ }
  }

  function saveBestScore(size: PuzzleSize, moves: number, time: number): void {
    if (!available) return
    try {
      const scores = loadBestScore()
      const key = `${size}x${size}`
      const prev = scores[key]
      if (!prev || moves < prev.moves || (moves === prev.moves && time < prev.time)) {
        scores[key] = { moves, time }
      }
      localStorage.setItem(BEST_KEY, JSON.stringify(scores))
    } catch { /* silent */ }
  }

  function loadBestScore(): Record<string, { moves: number; time: number }> {
    if (!available) return {}
    try {
      const raw = localStorage.getItem(BEST_KEY)
      return raw ? JSON.parse(raw) : {}
    } catch {
      return {}
    }
  }

  function saveDarkMode(isDark: boolean): void {
    if (!available) return
    try { localStorage.setItem(DARK_KEY, JSON.stringify(isDark)) } catch { /* silent */ }
  }

  function loadDarkMode(): boolean | null {
    if (!available) return null
    try {
      const raw = localStorage.getItem(DARK_KEY)
      return raw ? JSON.parse(raw) : null
    } catch {
      return null
    }
  }

  function saveImageData(data: string): void {
    if (!available) return
    try { localStorage.setItem(IMAGE_KEY, data) } catch { /* silent */ }
  }

  function loadImageData(): string | null {
    if (!available) return null
    try { return localStorage.getItem(IMAGE_KEY) } catch { return null }
  }

  return { saveState, loadState, clearState, saveBestScore, loadBestScore, saveDarkMode, loadDarkMode, saveImageData, loadImageData }
}
