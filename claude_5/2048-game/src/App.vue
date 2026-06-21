<template>
  <div class="app-container">
    <GameHeader
      :score="state.score"
      :best-score="state.bestScore[state.boardSize] || 0"
      @new-game="handleNewGame"
    />

    <div class="board-wrapper">
      <GameBoard
        :tiles="state.tiles"
        :board-size="state.boardSize"
        @move="handleMove"
      />
      <GameOverlay
        :status="state.status"
        :score="state.score"
        @new-game="handleNewGame"
      />
    </div>

    <GameControls
      :can-undo="state.history.length > 0"
      :board-size="state.boardSize"
      :is-dark="state.isDarkMode"
      @undo="handleUndo"
      @change-size="handleSizeChange"
      @toggle-dark="handleToggleDark"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import GameHeader from './components/GameHeader.vue'
import GameBoard from './components/GameBoard.vue'
import GameControls from './components/GameControls.vue'
import GameOverlay from './components/GameOverlay.vue'
import { useGameState } from './composables/useGameState'
import type { BoardSize, Direction } from './types/game'

const { state, handleMove, restoreOrInit, newGame, undo, toggleDarkMode } = useGameState()

function handleNewGame(): void {
  newGame(state.boardSize)
}

function handleSizeChange(size: BoardSize): void {
  newGame(size)
}

function handleUndo(): void {
  undo()
}

function handleToggleDark(): void {
  toggleDarkMode()
}

onMounted(() => {
  restoreOrInit()
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
