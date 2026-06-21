import type { BoardSize, GameState, StorageData } from '../types/game'

const STATE_KEY = '2048-game-state'
const BEST_KEY = '2048-best-score'
const DARK_KEY = '2048-dark-mode'

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

  function saveState(state: Pick<GameState, 'tiles' | 'score' | 'boardSize'>): void {
    if (!available) return
    try {
      const data: StorageData = {
        tiles: state.tiles.map(t => ({ id: t.id, value: t.value, row: t.row, col: t.col })),
        score: state.score,
        boardSize: state.boardSize,
      }
      localStorage.setItem(STATE_KEY, JSON.stringify(data))
    } catch { /* silent fallback */ }
  }

  function loadState(): StorageData | null {
    if (!available) return null
    try {
      const raw = localStorage.getItem(STATE_KEY)
      if (!raw) return null
      const parsed = JSON.parse(raw) as StorageData
      if (!parsed.tiles || typeof parsed.score !== 'number') {
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

  function saveBestScore(size: BoardSize, score: number): void {
    if (!available) return
    try {
      const scores = loadBestScore()
      scores[size] = Math.max(scores[size] || 0, score)
      localStorage.setItem(BEST_KEY, JSON.stringify(scores))
    } catch { /* silent */ }
  }

  function loadBestScore(): Record<BoardSize, number> {
    if (!available) return { 4: 0, 5: 0, 6: 0 }
    try {
      const raw = localStorage.getItem(BEST_KEY)
      return raw ? { 4: 0, 5: 0, 6: 0, ...JSON.parse(raw) } : { 4: 0, 5: 0, 6: 0 }
    } catch {
      return { 4: 0, 5: 0, 6: 0 }
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

  return { saveState, loadState, clearState, saveBestScore, loadBestScore, saveDarkMode, loadDarkMode }
}
