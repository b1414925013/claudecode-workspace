# Sliding Puzzle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully playable Sliding Puzzle game with Vue 3 + Vite + TypeScript, supporting number mode, image mode, IDA* solver, dark mode, and persistence.

**Architecture:** Single-page Vue 3 app using Composition API. Game logic isolated in composables (`usePuzzleLogic`, `usePuzzleState`, `useSolver`, `useStorage`). Tiles rendered with CSS Grid + absolute positioning for smooth animation.

**Tech Stack:** Vue 3.4, Vite 5, TypeScript 5.4, CSS Custom Properties, Canvas API, localStorage

## Global Constraints

- Vue 3 Composition API + `<script setup lang="ts">` throughout
- Zero external UI/framework dependencies (no Tailwind, no UI library)
- Build must pass with `vue-tsc --noEmit && vite build`
- All component styles scoped unless in global style.css
- Files use PascalCase for `.vue` components, camelCase for `.ts` composables
- Tile movement uses CSS `transition` on `transform` only (no JS animation libs)
- localStorage read/write wrapped in try/catch for privacy-mode fallback
- Input locked for 100ms after each move to prevent race conditions
- IDA* solver runs synchronously with 5-second timeout for 5×5

---

### Task 1: Scaffold Project

**Files:**
- Create: `sliding-puzzle/package.json`
- Create: `sliding-puzzle/vite.config.ts`
- Create: `sliding-puzzle/tsconfig.json`
- Create: `sliding-puzzle/tsconfig.node.json`
- Create: `sliding-puzzle/index.html`
- Create: `sliding-puzzle/src/vite-env.d.ts`
- Create: `sliding-puzzle/src/main.ts`
- Create: `sliding-puzzle/src/style.css` (stub)
- Create: `sliding-puzzle/src/App.vue` (stub)

- [ ] **Step 1: Create project directories**

```bash
mkdir -p sliding-puzzle/src/components sliding-puzzle/src/composables sliding-puzzle/src/types sliding-puzzle/src/assets/presets
```

- [ ] **Step 2: Create package.json**

```json
{
  "name": "sliding-puzzle",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "vue-tsc": "^2.0.0"
  }
}
```

- [ ] **Step 3: Create vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})
```

- [ ] **Step 4: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"]
}
```

- [ ] **Step 5: Create tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 6: Create index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
    <title>数字华容道</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧩</text></svg>" />
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 7: Create src/vite-env.d.ts**

```typescript
/// <reference types="vite/client" />
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

- [ ] **Step 8: Create src/main.ts**

```typescript
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

createApp(App).mount('#app')
```

- [ ] **Step 9: Create stub App.vue**

```vue
<template>
  <div class="app">
    <h1>Sliding Puzzle</h1>
  </div>
</template>

<script setup lang="ts">
</script>
```

- [ ] **Step 10: Create stub style.css**

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #faf8ef;
  color: #776e65;
}
#app {
  min-height: 100%;
  display: flex; justify-content: center; align-items: flex-start;
  padding: 20px 16px 40px;
}
```

- [ ] **Step 11: Install dependencies**

```bash
cd sliding-puzzle && npm install
```

- [ ] **Step 12: Verify build**

```bash
npm run build
```

Expected: `dist/` created. No errors.

- [ ] **Step 13: Commit**

```bash
git add sliding-puzzle/
git commit -m "feat: scaffold sliding puzzle project"
```

---

### Task 2: Types and Storage Layer

**Files:**
- Create: `sliding-puzzle/src/types/puzzle.ts`
- Create: `sliding-puzzle/src/composables/useStorage.ts`

**Interfaces:**
- Produces: `PuzzleSize`, `GameMode`, `GameStatus`, `BestScoreData`, `Move`, `PuzzleState` types
- Produces: `useStorage()` returning `{ saveState, loadState, clearState, saveBestScore, loadBestScore, saveDarkMode, loadDarkMode, saveImageData, loadImageData }`

- [ ] **Step 1: Create src/types/puzzle.ts**

```typescript
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
```

- [ ] **Step 2: Create src/composables/useStorage.ts**

```typescript
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
```

- [ ] **Step 3: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 4: Commit**

```bash
git add sliding-puzzle/src/types/ sliding-puzzle/src/composables/
git commit -m "feat: add puzzle types and localStorage composable"
```

---

### Task 3: Core Puzzle Logic

**Files:**
- Create: `sliding-puzzle/src/composables/usePuzzleLogic.ts`

**Interfaces:**
- Consumes: `PuzzleSize`, `Move` from types
- Produces: `usePuzzleLogic()` returning `{ createSolvedBoard, shuffle, moveTile, isWin, findEmpty, isAdjacent, isSolvable }`

- [ ] **Step 1: Create src/composables/usePuzzleLogic.ts**

```typescript
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
    if (tr === er && tc === ec + 1) return 'left'   // tile is right of empty, slides left
    if (tr === er && tc === ec - 1) return 'right'  // tile is left of empty, slides right
    if (tc === ec && tr === er + 1) return 'up'     // tile is below empty, slides up
    return 'down'                                     // tile is above empty, slides down
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

    // Ensure the puzzle is not already solved
    const solved = createSolvedBoard(size)
    if (current.every((v, i) => v === solved[i])) {
      // Swap two random non-empty tiles to break solved state
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

  /** Check if a puzzle state is solvable using inversion count */
  function isSolvable(board: number[], size: PuzzleSize): boolean {
    const flat = board.filter(v => v !== 0)
    let inversions = 0
    for (let i = 0; i < flat.length; i++) {
      for (let j = i + 1; j < flat.length; j++) {
        if (flat[i] > flat[j]) inversions++
      }
    }

    if (size % 2 === 1) {
      // Odd width: solvable if inversions is even
      return inversions % 2 === 0
    } else {
      // Even width: solvable if (inversions + row of empty from bottom) is even
      const emptyIdx = findEmpty(board)
      const emptyRowFromBottom = size - Math.floor(emptyIdx / size)
      return (inversions + emptyRowFromBottom) % 2 === 0
    }
  }

  return { createSolvedBoard, findEmpty, getRowCol, isAdjacent, moveTile, shuffle, getNeighbors, isWin, isSolvable }
}
```

- [ ] **Step 2: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/composables/usePuzzleLogic.ts
git commit -m "feat: add core puzzle logic (move, shuffle, win detection, solvability check)"
```

---

### Task 4: IDA* Solver

**Files:**
- Create: `sliding-puzzle/src/composables/useSolver.ts`

**Interfaces:**
- Consumes: `PuzzleSize`, `Move` types; `usePuzzleLogic`
- Produces: `useSolver()` returning `{ solve, getSolution, isSolving, cancel }`

- [ ] **Step 1: Create src/composables/useSolver.ts**

```typescript
import type { PuzzleSize, Move } from '../types/puzzle'
import { usePuzzleLogic } from './usePuzzleLogic'

const DIRECTIONS: number[] = [0, 1, 2, 3] // up, down, left, right
const OPPOSITE: number[] = [1, 0, 3, 2]  // opposite direction index

interface Step {
  board: number[]
  move: number  // index to move into empty
}

export function useSolver() {
  const logic = usePuzzleLogic()
  let cancelled = false

  function cancel(): void {
    cancelled = true
  }

  function resetCancel(): void {
    cancelled = false
  }

  /**
   * Precompute Manhattan distance lookup table for a given size.
   * table[value][index] = manhattan distance from index to value's goal position
   */
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

  /**
   * Get the Manhattan distance for a board state using the lookup table.
   * Value 0 (empty) contributes 0 distance.
   */
  function manhattan(board: number[], table: number[][], size: PuzzleSize): number {
    let dist = 0
    for (let i = 0; i < board.length; i++) {
      if (board[i] !== 0) {
        dist += table[board[i]][i]
      }
    }
    return dist
  }

  /**
   * Apply a move: slide the tile at `tileIdx` into the empty position.
   */
  function applyMove(board: number[], emptyIdx: number, tileIdx: number): number[] {
    const next = [...board]
    next[emptyIdx] = board[tileIdx]
    next[tileIdx] = 0
    return next
  }

  /**
   * IDA* solver. Returns array of indices to move into empty, or null if no solution found.
   * Handles up to 5×5. 3×3 is instant, 4×4 < 2s, 5×5 < 5s.
   */
  function solve(board: number[], size: PuzzleSize): number[] | null {
    cancelled = false
    const table = buildManhattanTable(size)
    const goal = logic.createSolvedBoard(size)
    const emptyIdx = logic.findEmpty(board)
    const startH = manhattan(board, table, size)

    if (startH === 0) return [] // already solved

    let bound = startH
    const maxBound = size === 3 ? 100 : size === 4 ? 120 : 80

    const path: Step[] = []

    while (bound <= maxBound) {
      if (cancelled) return null
      const result = search(board, emptyIdx, 0, bound, table, goal, size, path, -1)
      if (cancelled) return null
      if (result === 'FOUND') {
        return path.map(s => s.move)
      }
      if (result === Infinity) return null
      bound = result
    }

    return null
  }

  function search(
    board: number[],
    emptyIdx: number,
    g: number,
    bound: number,
    table: number[][],
    goal: number[],
    size: PuzzleSize,
    path: Step[],
    lastMoveDir: number,
  ): number | 'FOUND' {
    const f = g + manhattan(board, table, size)
    if (f > bound) return f
    if (board.every((v, i) => v === goal[i])) return 'FOUND'

    let min = Infinity
    const [er, ec] = [Math.floor(emptyIdx / size), emptyIdx % size]
    const neighborIndices: number[] = []
    const neighborDirs: number[] = []

    if (er > 0) { neighborIndices.push(emptyIdx - size); neighborDirs.push(0) }  // up
    if (er < size - 1) { neighborIndices.push(emptyIdx + size); neighborDirs.push(1) }  // down
    if (ec > 0) { neighborIndices.push(emptyIdx - 1); neighborDirs.push(2) }  // left
    if (ec < size - 1) { neighborIndices.push(emptyIdx + 1); neighborDirs.push(3) }  // right

    // Sort by heuristic: prefer moves that reduce Manhattan distance
    const scored = neighborIndices.map((ni, i) => ({
      ni,
      dir: neighborDirs[i],
      score: table[board[ni]][emptyIdx] - table[board[ni]][ni],
    }))
    scored.sort((a, b) => b.score - a.score)

    for (const { ni, dir } of scored) {
      if (dir === OPPOSITE[lastMoveDir]) continue // skip reverse move

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
```

- [ ] **Step 2: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/composables/useSolver.ts
git commit -m "feat: add IDA* solver for 3x3/4x4/5x5 with Manhattan heuristic"
```

---

### Task 5: Global CSS Styles

**Files:**
- Create: `sliding-puzzle/src/style.css` (replace stub)

- [ ] **Step 1: Replace src/style.css**

```css
/* ========== CSS Variables & Theme ========== */
:root {
  --board-bg: #bbada0;
  --cell-bg: rgba(238, 228, 218, 0.35);
  --page-bg: #faf8ef;
  --text-color: #776e65;
  --score-bg: #bbada0;
  --btn-bg: #8f7a66;
  --btn-hover: #9f8b78;
  --overlay-bg: rgba(238, 228, 218, 0.73);
  --radius: 6px;
  --max-width: 500px;
}

.dark {
  --board-bg: #3c3a3d;
  --cell-bg: rgba(255, 255, 255, 0.1);
  --page-bg: #1a1a2e;
  --text-color: #e0e0e0;
  --score-bg: #3c3a3d;
  --btn-bg: #5c5a5d;
  --btn-hover: #6c6a6d;
  --overlay-bg: rgba(26, 26, 46, 0.85);
}

/* ========== Reset ========== */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body { height: 100%; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--page-bg);
  color: var(--text-color);
  overflow-x: hidden;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

#app {
  min-height: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 20px 16px 40px;
}

/* ========== Tile Colors (Number Mode) ========== */
.tile-1  { background: #eee4da; color: #776e65; }
.tile-2  { background: #ede0c8; color: #776e65; }
.tile-3  { background: #f2b179; color: #f9f6f2; }
.tile-4  { background: #f59563; color: #f9f6f2; }
.tile-5  { background: #f67c5f; color: #f9f6f2; }
.tile-6  { background: #f65e3b; color: #f9f6f2; }
.tile-7  { background: #edcf72; color: #f9f6f2; }
.tile-8  { background: #edcc61; color: #f9f6f2; }
.tile-9  { background: #edc850; color: #f9f6f2; }
.tile-10 { background: #edc53f; color: #f9f6f2; }
.tile-11,
.tile-12,
.tile-13,
.tile-14,
.tile-15,
.tile-16,
.tile-17,
.tile-18,
.tile-19,
.tile-20,
.tile-21,
.tile-22,
.tile-23,
.tile-24 { background: #edc22e; color: #f9f6f2; }

.dark .tile-1  { background: #4a4a4a; color: #e0e0e0; }
.dark .tile-2  { background: #5a4a3a; color: #e0e0e0; }
.dark .tile-3  { background: #8a5a3a; color: #e0e0e0; }
.dark .tile-4  { background: #9a4a2a; color: #e0e0e0; }
.dark .tile-5  { background: #aa3a2a; color: #e0e0e0; }
.dark .tile-6  { background: #ba2a1a; color: #e0e0e0; }
.dark .tile-7  { background: #8a7a2a; color: #e0e0e0; }
.dark .tile-8  { background: #9a8a2a; color: #e0e0e0; }
.dark .tile-9  { background: #aa9a2a; color: #e0e0e0; }
.dark .tile-10 { background: #baaa2a; color: #e0e0e0; }
.dark .tile-11,
.dark .tile-12,
.dark .tile-13,
.dark .tile-14,
.dark .tile-15,
.dark .tile-16,
.dark .tile-17,
.dark .tile-18,
.dark .tile-19,
.dark .tile-20,
.dark .tile-21,
.dark .tile-22,
.dark .tile-23,
.dark .tile-24 { background: #5a5a5a; color: #e0e0e0; }
```

- [ ] **Step 2: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/style.css
git commit -m "feat: add global CSS with tile colors and dark mode theme"
```

---

### Task 6: GameTile Component

**Files:**
- Create: `sliding-puzzle/src/components/GameTile.vue`

**Interfaces:**
- Props: `value: number`, `index: number`, `cellSize: number`, `size: PuzzleSize`, `mode: GameMode`, `imageUrl: string | null`, `isEmpty: boolean`
- Pure display component — renders a tile with number or image slice

- [ ] **Step 1: Create src/components/GameTile.vue**

```vue
<template>
  <div
    class="tile-pos"
    :style="positionStyle"
  >
    <div
      v-if="!isEmpty"
      class="tile"
      :class="mode === 'number' ? tileClass : 'tile-image'"
      :style="mode === 'image' ? imageStyle : {}"
      role="button"
      :aria-label="mode === 'number' ? `方块 ${value}` : '图片方块'"
    >
      <span v-if="mode === 'number'" class="tile-text">{{ value }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PuzzleSize, GameMode } from '../types/puzzle'

const props = defineProps<{
  value: number
  index: number
  cellSize: number
  gap: number
  size: PuzzleSize
  mode: GameMode
  imageUrl: string | null
  isEmpty: boolean
}>()

const positionStyle = computed(() => {
  const col = props.index % props.size
  const row = Math.floor(props.index / props.size)
  return {
    transform: `translate(${col * (props.cellSize + props.gap) + props.gap}px, ${row * (props.cellSize + props.gap) + props.gap}px)`,
    width: `${props.cellSize}px`,
    height: `${props.cellSize}px`,
  }
})

const tileClass = computed(() => {
  const v = props.value
  if (v >= 1 && v <= 24) return `tile-${v}`
  return 'tile-1'
})

const imageStyle = computed(() => {
  if (!props.imageUrl) return {}
  const col = props.value !== 0 ? (props.value - 1) % props.size : 0
  const row = props.value !== 0 ? Math.floor((props.value - 1) / props.size) : 0
  const totalSize = props.size * props.cellSize
  return {
    backgroundImage: `url(${props.imageUrl})`,
    backgroundSize: `${totalSize}px ${totalSize}px`,
    backgroundPosition: `-${col * props.cellSize}px -${row * props.cellSize}px`,
  }
})
</script>

<style scoped>
.tile-pos {
  position: absolute;
  top: 0;
  left: 0;
  transition: transform 120ms ease;
  will-change: transform;
}

.tile {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  transition: box-shadow 0.1s;
}

.tile:active {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.tile-image {
  width: 100%;
  height: 100%;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}

.tile-text {
  font-size: 1.5rem;
  font-weight: bold;
}
</style>
```

- [ ] **Step 2: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/components/GameTile.vue
git commit -m "feat: add GameTile component with number and image modes"
```

---

### Task 7: GameBoard Component

**Files:**
- Create: `sliding-puzzle/src/components/GameBoard.vue`

**Interfaces:**
- Props: `board: number[]`, `size: PuzzleSize`, `mode: GameMode`, `imageUrl: string | null`
- Emits: `move: [index: number]`

- [ ] **Step 1: Create src/components/GameBoard.vue**

```vue
<template>
  <div
    ref="boardRef"
    class="board"
    :style="boardStyle"
    role="grid"
    :aria-label="`${size}×${size} 数字华容道`"
  >
    <GameTile
      v-for="(value, index) in board"
      :key="`${index}-${value}`"
      :value="value"
      :index="index"
      :cell-size="cellSize"
      :gap="GAP"
      :size="size"
      :mode="mode"
      :image-url="imageUrl"
      :is-empty="value === 0"
      @click="onTileClick(index)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import type { PuzzleSize, GameMode } from '../types/puzzle'
import GameTile from './GameTile.vue'

const props = defineProps<{
  board: number[]
  size: PuzzleSize
  mode: GameMode
  imageUrl: string | null
}>()

const emit = defineEmits<{
  move: [index: number]
}>()

const GAP = 4
const boardRef = ref<HTMLDivElement | null>(null)
const boardWidth = ref(500)

const cellSize = computed(() => {
  return (boardWidth.value - GAP * (props.size + 1)) / props.size
})

const boardStyle = computed(() => ({
  width: `${boardWidth.value}px`,
  height: `${boardWidth.value}px`,
}))

function updateBoardWidth() {
  if (boardRef.value?.parentElement) {
    const parentW = boardRef.value.parentElement.clientWidth
    const maxW = Math.min(parentW - 32, 500)
    boardWidth.value = Math.max(maxW, 280)
  }
}

function onTileClick(index: number) {
  emit('move', index)
}

let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  updateBoardWidth()
  resizeObserver = new ResizeObserver(updateBoardWidth)
  if (boardRef.value?.parentElement) {
    resizeObserver.observe(boardRef.value.parentElement)
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})
</script>

<style scoped>
.board {
  position: relative;
  background: var(--board-bg);
  border-radius: var(--radius);
  padding: 4px;
  touch-action: none;
}
</style>
```

- [ ] **Step 2: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/components/GameBoard.vue
git commit -m "feat: add GameBoard with tile rendering"
```

---

### Task 8: GameHeader Component

**Files:**
- Create: `sliding-puzzle/src/components/GameHeader.vue`

**Interfaces:**
- Props: `moves: number`, `timer: number`
- Emits: `newGame`

- [ ] **Step 1: Create src/components/GameHeader.vue**

```vue
<template>
  <div class="header">
    <div class="header-top">
      <h1 class="title">数字华容道</h1>
      <div class="stats">
        <div class="stat-box">
          <span class="stat-label">步数</span>
          <span class="stat-value">{{ moves }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">时间</span>
          <span class="stat-value">{{ formattedTime }}</span>
        </div>
      </div>
    </div>
    <div class="header-bottom">
      <p class="subtitle">移动方块，按顺序排列 <strong>1~{{ maxNumber }}</strong></p>
      <button class="btn" @click="$emit('newGame')">新游戏</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PuzzleSize } from '../types/puzzle'

const props = defineProps<{
  moves: number
  timer: number
  size: PuzzleSize
}>()

defineEmits<{
  newGame: []
}>()

const maxNumber = computed(() => props.size * props.size - 1)

const formattedTime = computed(() => {
  const m = Math.floor(props.timer / 60)
  const s = props.timer % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
</script>

<style scoped>
.header {
  width: 100%;
  max-width: 500px;
  margin-bottom: 12px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title {
  font-size: 2.5rem;
  font-weight: 900;
  line-height: 1;
  color: var(--text-color);
}

.stats {
  display: flex;
  gap: 8px;
}

.stat-box {
  background: var(--score-bg);
  color: #fff;
  border-radius: var(--radius);
  padding: 8px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 70px;
}

.stat-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  opacity: 0.8;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.header-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.subtitle {
  font-size: 0.85rem;
  color: var(--text-color);
  opacity: 0.8;
}

.btn {
  background: var(--btn-bg);
  color: #f9f6f2;
  border: none;
  border-radius: var(--radius);
  padding: 10px 20px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.btn:hover {
  background: var(--btn-hover);
}

@media (max-width: 500px) {
  .title { font-size: 2rem; }
  .stat-box { padding: 6px 12px; min-width: 60px; }
  .stat-value { font-size: 1.1rem; }
}
</style>
```

- [ ] **Step 2: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/components/GameHeader.vue
git commit -m "feat: add GameHeader with move counter and timer"
```

---

### Task 9: GameControls Component

**Files:**
- Create: `sliding-puzzle/src/components/GameControls.vue`

**Interfaces:**
- Props: `size: PuzzleSize`, `isDark: boolean`, `mode: GameMode`, `isSolving: boolean`, `canSolve: boolean`
- Emits: `shuffle`, `changeSize: PuzzleSize`, `toggleDark`, `toggleMode`, `solve`

- [ ] **Step 1: Create src/components/GameControls.vue**

```vue
<template>
  <div class="controls">
    <button class="btn" @click="$emit('shuffle')">🔀 打乱</button>

    <div class="control-group">
      <label class="control-label">棋盘</label>
      <select class="select" :value="size" @change="onSizeChange">
        <option :value="3">3×3</option>
        <option :value="4">4×4</option>
        <option :value="5">5×5</option>
      </select>
    </div>

    <button
      class="btn"
      :disabled="isSolving"
      @click="$emit('solve')"
    >
      💡 解算
    </button>

    <div class="control-group">
      <label class="control-label">模式</label>
      <button class="btn btn-sm" @click="$emit('toggleMode')">
        {{ mode === 'number' ? '🔢' : '🖼️' }}
      </button>
    </div>

    <button class="btn btn-icon" @click="$emit('toggleDark')" :title="isDark ? '亮色模式' : '深色模式'">
      {{ isDark ? '☀️' : '🌙' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import type { PuzzleSize, GameMode } from '../types/puzzle'

defineProps<{
  size: PuzzleSize
  isDark: boolean
  mode: GameMode
  isSolving: boolean
}>()

const emit = defineEmits<{
  shuffle: []
  changeSize: [size: PuzzleSize]
  toggleDark: []
  toggleMode: []
  solve: []
}>()

function onSizeChange(e: Event) {
  const val = parseInt((e.target as HTMLSelectElement).value) as PuzzleSize
  emit('changeSize', val)
}
</script>

<style scoped>
.controls {
  width: 100%;
  max-width: 500px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.btn {
  background: var(--btn-bg);
  color: #f9f6f2;
  border: none;
  border-radius: var(--radius);
  padding: 9px 14px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn:not(:disabled):hover {
  background: var(--btn-hover);
}

.btn-sm {
  padding: 9px 12px;
  font-size: 1rem;
  line-height: 1;
}

.btn-icon {
  padding: 9px 10px;
  font-size: 1.1rem;
  line-height: 1;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.control-label {
  font-size: 0.75rem;
  color: var(--text-color);
  opacity: 0.8;
}

.select {
  background: var(--btn-bg);
  color: #f9f6f2;
  border: none;
  border-radius: var(--radius);
  padding: 8px 10px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  outline: none;
}

.select:hover {
  background: var(--btn-hover);
}
</style>
```

- [ ] **Step 2: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/components/GameControls.vue
git commit -m "feat: add GameControls with size selector, shuffle, solve, mode toggle"
```

---

### Task 10: ImagePicker Component

**Files:**
- Create: `sliding-puzzle/src/components/ImagePicker.vue`
- Create: `sliding-puzzle/src/assets/presets/index.ts`

**Interfaces:**
- Props: `selectedImage: string | null`
- Emits: `selectImage: string | null`
- Shows preset images and upload button

- [ ] **Step 1: Create preset images (SVG patterns as base64 data URLs)**

Create `src/assets/presets/index.ts`:
```typescript
// Built-in preset images as SVG data URLs for the image puzzle mode

function svgUrl(svg: string): string {
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}

const presets = [
  {
    id: 'gradient',
    name: '渐变',
    url: svgUrl(`<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">
      <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#ff6b6b"/>
        <stop offset="50%" stop-color="#ffd93d"/>
        <stop offset="100%" stop-color="#6bcb77"/>
      </linearGradient></defs>
      <rect width="400" height="400" fill="url(#g)"/>
    </svg>`),
  },
  {
    id: 'circles',
    name: '圆点',
    url: svgUrl(`<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">
      <rect width="400" height="400" fill="#2c3e50"/>
      <circle cx="100" cy="100" r="60" fill="#e74c3c" opacity="0.8"/>
      <circle cx="300" cy="120" r="50" fill="#3498db" opacity="0.8"/>
      <circle cx="150" cy="300" r="70" fill="#f39c12" opacity="0.8"/>
      <circle cx="320" cy="320" r="45" fill="#2ecc71" opacity="0.8"/>
      <circle cx="200" cy="200" r="40" fill="#9b59b6" opacity="0.8"/>
    </svg>`),
  },
  {
    id: 'waves',
    name: '波浪',
    url: svgUrl(`<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">
      <rect width="400" height="400" fill="#1a1a2e"/>
      <path d="M0 200 Q50 150 100 200 T200 200 T300 200 T400 200" stroke="#e94560" stroke-width="8" fill="none" opacity="0.9"/>
      <path d="M0 240 Q50 190 100 240 T200 240 T300 240 T400 240" stroke="#0f3460" stroke-width="8" fill="none" opacity="0.9"/>
      <path d="M0 160 Q50 110 100 160 T200 160 T300 160 T400 160" stroke="#533483" stroke-width="8" fill="none" opacity="0.9"/>
      <path d="M0 280 Q50 230 100 280 T200 280 T300 280 T400 280" stroke="#e94560" stroke-width="4" fill="none" opacity="0.5"/>
    </svg>`),
  },
]

export default presets
```

- [ ] **Step 2: Create src/components/ImagePicker.vue**

```vue
<template>
  <div class="picker">
    <p class="picker-title">选择或上传图片</p>
    <div class="presets">
      <div
        v-for="img in presets"
        :key="img.id"
        class="preset-item"
        :class="{ active: selectedImage === img.url }"
        @click="select(img.url)"
      >
        <div class="preset-thumb" :style="{ backgroundImage: `url(${img.url})` }"></div>
        <span class="preset-name">{{ img.name }}</span>
      </div>
      <div class="preset-item upload-item" @click="triggerUpload">
        <div class="preset-thumb upload-thumb">+</div>
        <span class="preset-name">上传</span>
      </div>
    </div>
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display:none"
      @change="onFileSelected"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import presets from '../assets/presets'

const props = defineProps<{
  selectedImage: string | null
}>()

const emit = defineEmits<{
  selectImage: [url: string | null]
}>()

const fileInput = ref<HTMLInputElement | null>(null)

function select(url: string) {
  emit('selectImage', url)
}

function triggerUpload() {
  fileInput.value?.click()
}

function onFileSelected(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]

  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    const dataUrl = reader.result as string
    // Scale via canvas to ensure square
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const size = 400
      canvas.width = size
      canvas.height = size
      const ctx = canvas.getContext('2d')!
      ctx.drawImage(img, 0, 0, size, size)
      const scaled = canvas.toDataURL('image/jpeg', 0.9)
      emit('selectImage', scaled)
    }
    img.src = dataUrl
  }
  reader.readAsDataURL(file)
}
</script>

<style scoped>
.picker {
  width: 100%;
  max-width: 500px;
  margin-top: 12px;
}

.picker-title {
  font-size: 0.85rem;
  margin-bottom: 8px;
  color: var(--text-color);
  opacity: 0.8;
}

.presets {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.preset-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius);
  border: 2px solid transparent;
  transition: border-color 0.15s;
}

.preset-item.active {
  border-color: var(--btn-bg);
}

.preset-item:hover {
  border-color: var(--btn-hover);
}

.preset-thumb {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  background-size: cover;
  background-position: center;
}

.upload-thumb {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2rem;
  color: var(--text-color);
  border: 2px dashed var(--text-color);
  opacity: 0.5;
  cursor: pointer;
}

.preset-name {
  font-size: 0.7rem;
  color: var(--text-color);
  opacity: 0.7;
}
</style>
```

- [ ] **Step 3: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 4: Commit**

```bash
git add sliding-puzzle/src/components/ImagePicker.vue sliding-puzzle/src/assets/
git commit -m "feat: add ImagePicker with preset images and upload support"
```

---

### Task 11: GameOverlay Component

**Files:**
- Create: `sliding-puzzle/src/components/GameOverlay.vue`

**Interfaces:**
- Props: `status: GameStatus`, `moves: number`, `timer: number`, `solverPath: number[]`, `solverStep: number`
- Emits: `newGame`, `applySolverStep`, `closeSolver`

- [ ] **Step 1: Create src/components/GameOverlay.vue**

```vue
<template>
  <!-- Win overlay -->
  <Transition name="overlay">
    <div v-if="status === 'won'" class="overlay">
      <div class="overlay-content">
        <h2 class="overlay-title">🎉 恭喜完成！</h2>
        <p class="overlay-score">用了 <strong>{{ moves }}</strong> 步，耗时 <strong>{{ formattedTime }}</strong></p>
        <button class="btn" @click="$emit('newGame')">再来一局</button>
      </div>
    </div>
  </Transition>

  <!-- Solver overlay -->
  <Transition name="overlay">
    <div v-if="status === 'solving'" class="overlay">
      <div class="overlay-content">
        <h2 class="overlay-title">🤔 正在求解中...</h2>
        <p class="overlay-score">请稍候</p>
      </div>
    </div>
  </Transition>

  <!-- Solved (show solution) overlay -->
  <Transition name="overlay">
    <div v-if="status === 'solved'" class="overlay">
      <div class="overlay-content">
        <h2 class="overlay-title">💡 解算完成！</h2>
        <p class="overlay-score">共 {{ solverPath.length }} 步</p>
        <div class="solver-buttons">
          <button class="btn" @click="$emit('applySolverStep')">
            下一步 ({{ solverStep }} / {{ solverPath.length }})
          </button>
          <button class="btn btn-secondary" @click="$emit('closeSolver')">
            关闭
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GameStatus } from '../types/puzzle'

const props = defineProps<{
  status: GameStatus
  moves: number
  timer: number
  solverPath: number[]
  solverStep: number
}>()

defineEmits<{
  newGame: []
  applySolverStep: []
  closeSolver: []
}>()

const formattedTime = computed(() => {
  const m = Math.floor(props.timer / 60)
  const s = props.timer % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
</script>

<style scoped>
.overlay {
  position: absolute;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  border-radius: var(--radius);
  backdrop-filter: blur(2px);
}

.overlay-content {
  text-align: center;
  padding: 32px;
}

.overlay-title {
  font-size: 1.8rem;
  margin-bottom: 12px;
  color: var(--text-color);
}

.overlay-score {
  font-size: 1rem;
  margin-bottom: 24px;
  color: var(--text-color);
}

.solver-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.btn {
  background: var(--btn-bg);
  color: #f9f6f2;
  border: none;
  border-radius: var(--radius);
  padding: 12px 24px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}

.btn:hover {
  background: var(--btn-hover);
}

.btn-secondary {
  background: transparent;
  border: 2px solid var(--btn-bg);
  color: var(--text-color);
}

.btn-secondary:hover {
  background: var(--btn-bg);
  color: #f9f6f2;
}

.overlay-enter-active { transition: opacity 0.3s ease; }
.overlay-leave-active { transition: opacity 0.2s ease; }
.overlay-enter-from, .overlay-leave-to { opacity: 0; }
</style>
```

- [ ] **Step 2: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/components/GameOverlay.vue
git commit -m "feat: add GameOverlay for win, solving, and solution display"
```

---

### Task 12: Game State Composable

**Files:**
- Create: `sliding-puzzle/src/composables/usePuzzleState.ts`

**Interfaces:**
- Consumes: all types, `usePuzzleLogic`, `useSolver`, `useStorage`
- Produces: `usePuzzleState()` returning `{ state, initGame, handleClick, shuffle, startSolver, applySolverStep, closeSolver, toggleDarkMode, toggleMode, setImage }`

- [ ] **Step 1: Create src/composables/usePuzzleState.ts**

```typescript
import { reactive, onUnmounted } from 'vue'
import type { PuzzleSize, GameMode, PuzzleState } from '../types/puzzle'
import { usePuzzleLogic } from './usePuzzleLogic'
import { useSolver } from './useSolver'
import { useStorage } from './useStorage'

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
  let solverPath: number[] = []
  let solverStep = 0
  let solverTimers: ReturnType<typeof setTimeout>[] = []

  function startTimer() {
    if (timerInterval) return
    state.isRunning = true
    timerInterval = setInterval(() => { state.timer++ }, 1000)
  }

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
    state.isRunning = false
  }

  function initGame(size: PuzzleSize = state.size, mode: GameMode = state.mode): void {
    stopTimer()
    const solved = logic.createSolvedBoard(size)
    const shuffled = logic.shuffle(solved, size)
    state.board = shuffled
    state.size = size
    state.mode = mode
    state.status = 'playing'
    state.moves = 0
    state.timer = 0
    state.isRunning = false
    solverPath = []
    solverStep = 0
    inputLocked = false
    solver.cancel()
    clearSolverTimers()
    storage.saveState({ board: state.board, moves: 0, timer: 0, size, mode, selectedImage: state.selectedImage })
  }

  function handleClick(index: number): void {
    if (state.status !== 'playing') return
    if (inputLocked) return
    if (state.board[index] === 0) return

    const result = logic.moveTile(state.board, index, state.size)
    if (!result) return

    // Start timer on first move
    if (state.moves === 0) startTimer()

    state.board = result.newBoard
    state.moves++
    inputLocked = true
    setTimeout(() => { inputLocked = false }, 120)

    // Auto-save after each move
    storage.saveState({ board: state.board, moves: state.moves, timer: state.timer, size: state.size, mode: state.mode, selectedImage: state.selectedImage })

    if (logic.isWin(state.board, state.size)) {
      stopTimer()
      state.status = 'won'
      storage.saveBestScore(state.size, state.moves, state.timer)
      state.bestScores = storage.loadBestScore()
    }
  }

  function shuffle(): void {
    const solved = logic.createSolvedBoard(state.size)
    state.board = logic.shuffle(solved, state.size)
    state.moves = 0
    state.timer = 0
    state.status = 'playing'
    stopTimer()
    solverPath = []
    solverStep = 0
    storage.saveState({ board: state.board, moves: 0, timer: 0, size: state.size, mode: state.mode, selectedImage: state.selectedImage })
  }

  function startSolver(): void {
    if (state.status !== 'playing') return
    state.status = 'solving'
    solverPath = []
    solverStep = 0

    // Defer to next tick to allow overlay to render
    setTimeout(() => {
      const prevStatus = state.status
      const result = solver.solve(state.board, state.size)
      if (prevStatus !== 'solving') return // was cancelled

      if (result && result.length > 0) {
        solverPath = result
        solverStep = 0
        state.status = 'solved'
      } else {
        state.status = 'playing'
        alert('无法在合理时间内求解，请尝试打乱后重试。')
      }
    }, 50)
  }

  function applySolverStep(): void {
    if (solverStep >= solverPath.length) {
      state.status = 'won'
      return
    }
    const moveIdx = solverPath[solverStep]
    const result = logic.moveTile(state.board, moveIdx, state.size)
    if (result) {
      state.board = result.newBoard
      state.moves++
      solverStep++
    }
    if (solverStep >= solverPath.length) {
      state.status = 'won'
      stopTimer()
      storage.saveBestScore(state.size, state.moves, state.timer)
      state.bestScores = storage.loadBestScore()
    }
  }

  function closeSolver(): void {
    state.status = 'playing'
  }

  function toggleDarkMode(): void {
    state.isDarkMode = !state.isDarkMode
    document.documentElement.classList.toggle('dark', state.isDarkMode)
    storage.saveDarkMode(state.isDarkMode)
  }

  function toggleMode(): void {
    if (state.mode === 'number') {
      state.mode = 'image'
      if (!state.selectedImage) {
        // Use first preset as default
        import('../assets/presets').then(m => {
          state.selectedImage = m.default[0].url
          initGame(state.size, 'image')
        })
        return
      }
    }
    const newMode = state.mode === 'number' ? 'image' : 'number'
    initGame(state.size, newMode)
  }

  function setImage(url: string | null): void {
    state.selectedImage = url
    state.mode = 'image'
    if (url) storage.saveImageData(url)
    initGame(state.size, 'image')
  }

  function clearSolverTimers(): void {
    solverTimers.forEach(t => clearTimeout(t))
    solverTimers = []
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
      // Resume timer if game in progress
      if (state.moves > 0 && !logic.isWin(state.board, state.size)) {
        startTimer()
      }
    } else {
      initGame(4)
    }
  }

  onUnmounted(() => {
    stopTimer()
    solver.cancel()
    clearSolverTimers()
  })

  return {
    state,
    initGame,
    handleClick,
    shuffle,
    startSolver,
    applySolverStep: () => { applySolverStep(); return { solverPath, solverStep } },
    closeSolver,
    toggleDarkMode,
    toggleMode,
    setImage,
    restoreOrInit,
    solverPath: () => solverPath,
    solverStep: () => solverStep,
  }
}
```

- [ ] **Step 2: Verify build**

```bash
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/composables/usePuzzleState.ts
git commit -m "feat: add puzzle game state composable with solver integration"
```

---

### Task 13: App.vue Final Integration

**Files:**
- Modify: `sliding-puzzle/src/App.vue` (replace stub)

- [ ] **Step 1: Replace src/App.vue**

```vue
<template>
  <div class="app-container">
    <GameHeader
      :moves="state.moves"
      :timer="state.timer"
      :size="state.size"
      @new-game="handleNewGame"
    />

    <div class="board-wrapper">
      <GameBoard
        :board="state.board"
        :size="state.size"
        :mode="state.mode"
        :image-url="state.selectedImage"
        @move="handleClick"
      />
      <GameOverlay
        :status="state.status"
        :moves="state.moves"
        :timer="state.timer"
        :solver-path="solverPathRef"
        :solver-step="solverStepRef"
        @new-game="handleNewGame"
        @apply-solver-step="handleSolverStep"
        @close-solver="closeSolver"
      />
    </div>

    <GameControls
      :size="state.size"
      :is-dark="state.isDarkMode"
      :mode="state.mode"
      :is-solving="state.status === 'solving'"
      @shuffle="shuffle"
      @change-size="handleSizeChange"
      @toggle-dark="toggleDarkMode"
      @toggle-mode="toggleMode"
      @solve="startSolver"
    />

    <ImagePicker
      v-if="state.mode === 'image'"
      :selected-image="state.selectedImage"
      @select-image="setImage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import GameHeader from './components/GameHeader.vue'
import GameBoard from './components/GameBoard.vue'
import GameControls from './components/GameControls.vue'
import ImagePicker from './components/ImagePicker.vue'
import GameOverlay from './components/GameOverlay.vue'
import { usePuzzleState } from './composables/usePuzzleState'
import type { PuzzleSize } from './types/puzzle'

const {
  state, handleClick, shuffle, startSolver, closeSolver,
  toggleDarkMode, toggleMode, setImage, initGame, restoreOrInit,
  applySolverStep, solverPath, solverStep,
} = usePuzzleState()

const solverPathRef = ref<number[]>([])
const solverStepRef = ref(0)

function handleSolverStep() {
  const result = applySolverStep()
  solverPathRef.value = [...result.solverPath]
  solverStepRef.value = result.solverStep
}

function handleNewGame() {
  initGame(state.size, state.mode)
}

function handleSizeChange(size: PuzzleSize) {
  initGame(size, state.mode)
}

onMounted(() => {
  restoreOrInit()
  // Sync solver refs initially
  solverPathRef.value = []
  solverStepRef.value = 0
})
</script>

<style scoped>
.app-container {
  width: 100%;
  max-width: var(--max-width, 500px);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.board-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
}
</style>
```

- [ ] **Step 2: Final build**

```bash
npm run build
```

Expected: build succeeds with no errors.

- [ ] **Step 3: Commit**

```bash
git add sliding-puzzle/src/App.vue
git commit -m "feat: integrate all components in App.vue"
```

---

### Task 14: Verify Game Works

**Files:** None (play/test the app)

- [ ] **Step 1: Start dev server**

```bash
npm run dev
```

Expected: Vite dev server at `http://localhost:5173`.

- [ ] **Step 2: Manual test checklist**

1. **Board renders** — 4×4 grid shows shuffled tiles
2. **Click to move** — Click tile adjacent to empty → tile slides into empty
3. **Non-adjacent click ignored** — Click tile not next to empty → nothing happens
4. **Win detection** — Arrange tiles in order → "恭喜完成！" overlay appears
5. **Timer starts on first move** — Timer stays at 00:00 until first click
6. **Best score saved** — Complete puzzle, refresh, best score persists
7. **Game state restores** — Mid-game refresh restores board, moves, timer
8. **Shuffle** — Click "打乱" button → board resets, timer stops
9. **Board size** — Switch to 3×3 and 5×5, game resets
10. **Dark mode** — Toggle dark mode, colors switch
11. **Number mode** — Tiles show numbers 1-15, empty is blank
12. **Image mode** — Toggle to image mode, tiles show image slices
13. **Image presets** — Click different preset → board updates
14. **Upload image** — Upload a local image → board shows it
15. **Solver (3×3)** — Switch to 3×3, click "解算" → solution found quickly
16. **Solver step** — Click "下一步" → each step animates
17. **Close solver** — Click "关闭" → back to playing
18. **Responsive** — Resize below 500px, board scales down

- [ ] **Step 3: Fix issues and final commit**

```bash
git add -A && git commit -m "fix: resolve issues from manual testing"
```
