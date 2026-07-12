# Graph Report - D:/develop/claudecode-workspace/claude_5  (2026-07-03)

## Corpus Check
- Corpus is ~25,732 words - fits in a single context window. You may not need a graph.

## Summary
- 210 nodes · 276 edges · 17 communities (16 shown, 1 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 16 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Sliding Puzzle Core Logic|Sliding Puzzle Core Logic]]
- [[_COMMUNITY_2048 Game Core Logic|2048 Game Core Logic]]
- [[_COMMUNITY_Sliding Puzzle Board UI|Sliding Puzzle Board UI]]
- [[_COMMUNITY_2048 TypeScript Config|2048 TypeScript Config]]
- [[_COMMUNITY_Sliding Puzzle TypeScript Config|Sliding Puzzle TypeScript Config]]
- [[_COMMUNITY_Game Design Documents|Game Design Documents]]
- [[_COMMUNITY_2048 Package Configuration|2048 Package Configuration]]
- [[_COMMUNITY_Sliding Puzzle Package Configuration|Sliding Puzzle Package Configuration]]
- [[_COMMUNITY_Image Presets & Picker|Image Presets & Picker]]
- [[_COMMUNITY_2048 Board UI|2048 Board UI]]
- [[_COMMUNITY_2048 Vite & Build Config|2048 Vite & Build Config]]
- [[_COMMUNITY_Sliding Puzzle Vite & Build Config|Sliding Puzzle Vite & Build Config]]
- [[_COMMUNITY_Project Root Config|Project Root Config]]

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 16 edges
2. `compilerOptions` - 16 edges
3. `PuzzleSize` - 10 edges
4. `Sliding Puzzle Game` - 10 edges
5. `2048 Number Merging Game` - 9 edges
6. `BoardSize` - 6 edges
7. `compilerOptions` - 6 edges
8. `compilerOptions` - 6 edges
9. `TileData` - 5 edges
10. `Direction` - 5 edges

## Surprising Connections (you probably didn't know these)
- `2048 Game Vue App Entry` --references--> `2048 Number Merging Game`  [INFERRED]
  2048-game/index.html → docs/superpowers/specs/2026-06-21-2048-game-design.md
- `Sliding Puzzle Vue App Entry` --references--> `Sliding Puzzle Game`  [INFERRED]
  sliding-puzzle/index.html → docs/superpowers/specs/2026-06-21-sliding-puzzle-design.md
- `Superpowers-Driven Development (SDD)` --references--> `2048 Game Implementation Plan`  [INFERRED]
  .superpowers/sdd/progress.md → docs/superpowers/plans/2026-06-21-2048-game-plan.md
- `Superpowers-Driven Development (SDD)` --references--> `Sliding Puzzle Implementation Plan`  [INFERRED]
  .superpowers/sdd/progress.md → docs/superpowers/plans/2026-06-21-sliding-puzzle-plan.md
- `Sliding Puzzle Game` --conceptually_related_to--> `Vue 3 Composable Architecture`  [INFERRED]
  docs/superpowers/specs/2026-06-21-sliding-puzzle-design.md → docs/superpowers/specs/2026-06-21-2048-game-design.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Shared Tech Stack and Architecture Decisions** — docs_superpowers_specs_2026_06_21_2048_game_design_2048_game, docs_superpowers_specs_2026_06_21_sliding_puzzle_design_sliding_puzzle, docs_superpowers_specs_2026_06_21_2048_game_design_composable_pattern, docs_superpowers_specs_2026_06_21_2048_game_design_localstorage_fallback, docs_superpowers_specs_2026_06_21_2048_game_design_dark_mode, docs_superpowers_specs_2026_06_21_2048_game_design_zero_deps, docs_superpowers_specs_2026_06_21_2048_game_design_animation_css [INFERRED 0.85]
- **Sliding Puzzle Distinguishing Features** — docs_superpowers_specs_2026_06_21_sliding_puzzle_design_sliding_puzzle, docs_superpowers_specs_2026_06_21_sliding_puzzle_design_idastar_solver, docs_superpowers_specs_2026_06_21_sliding_puzzle_design_image_mode, docs_superpowers_specs_2026_06_21_sliding_puzzle_design_solvability_check [INFERRED 0.85]

## Communities (17 total, 1 thin omitted)

### Community 0 - "Sliding Puzzle Core Logic"
Cohesion: 0.09
Nodes (27): solverPathRef, solverStepRef, {
  state, handleClick, shuffleBoard, startSolver, closeSolver, mSolverPath, mSolverStep,
  toggleDarkMode, toggleMode, setImage, initGame, restoreOrInit, applySolverStep,
}, emit, onSizeChange(), formattedTime, maxNumber, props (+19 more)

### Community 1 - "2048 Game Core Logic"
Cohesion: 0.14
Nodes (14): { state, handleMove, restoreOrInit, newGame, undo, toggleDarkMode }, emit, onSizeChange(), SlideRowResult, useGameLogic(), useGameState(), useStorage(), BoardSize (+6 more)

### Community 2 - "Sliding Puzzle Board UI"
Cohesion: 0.12
Nodes (13): boardRef, boardWidth, cellSize, emit, gridStyle, keyMap, onKeyDown(), onTouchEnd() (+5 more)

### Community 3 - "2048 TypeScript Config"
Cohesion: 0.11
Nodes (17): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+9 more)

### Community 4 - "Sliding Puzzle TypeScript Config"
Cohesion: 0.11
Nodes (17): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+9 more)

### Community 5 - "Game Design Documents"
Cohesion: 0.17
Nodes (16): 2048 Game Vue App Entry, Superpowers-Driven Development (SDD), 2048 Game Implementation Plan, Sliding Puzzle Implementation Plan, 2048 Number Merging Game, CSS Transform-Based Animations, Vue 3 Composable Architecture, Dark Mode via CSS Variable Swap (+8 more)

### Community 6 - "2048 Package Configuration"
Cohesion: 0.12
Nodes (15): dependencies, vue, devDependencies, typescript, vite, @vitejs/plugin-vue, vue-tsc, name (+7 more)

### Community 7 - "Sliding Puzzle Package Configuration"
Cohesion: 0.12
Nodes (15): dependencies, vue, devDependencies, typescript, vite, @vitejs/plugin-vue, vue-tsc, name (+7 more)

### Community 8 - "Image Presets & Picker"
Cohesion: 0.24
Nodes (5): presets, emit, fileInput, props, select()

### Community 9 - "2048 Board UI"
Cohesion: 0.25
Nodes (7): boardRef, boardStyle, boardWidth, cellSize, emit, onTileClick(), props

### Community 10 - "2048 Vite & Build Config"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 11 - "Sliding Puzzle Vite & Build Config"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

## Knowledge Gaps
- **106 isolated node(s):** `name`, `version`, `private`, `type`, `dev` (+101 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PuzzleSize` connect `Sliding Puzzle Core Logic` to `2048 Board UI`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Sliding Puzzle Game` (e.g. with `2048 Number Merging Game` and `Vue 3 Composable Architecture`) actually correct?**
  _`Sliding Puzzle Game` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `2048 Number Merging Game` (e.g. with `2048 Game Vue App Entry` and `CSS Transform-Based Animations`) actually correct?**
  _`2048 Number Merging Game` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `private` to the rest of the system?**
  _111 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Sliding Puzzle Core Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.09024390243902439 - nodes in this community are weakly interconnected._
- **Should `2048 Game Core Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.14245014245014245 - nodes in this community are weakly interconnected._
- **Should `Sliding Puzzle Board UI` be split into smaller, more focused modules?**
  _Cohesion score 0.12418300653594772 - nodes in this community are weakly interconnected._