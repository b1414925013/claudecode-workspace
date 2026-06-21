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
      @shuffle="shuffleBoard"
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
  state, handleClick, shuffleBoard, startSolver, closeSolver, mSolverPath, mSolverStep,
  toggleDarkMode, toggleMode, setImage, initGame, restoreOrInit, applySolverStep,
} = usePuzzleState()

const solverPathRef = ref<number[]>([])
const solverStepRef = ref(0)

function handleSolverStep() {
  const result = applySolverStep()
  solverPathRef.value = [...result.solverPath]
  solverStepRef.value = result.solverStep
}

function handleNewGame() { initGame(state.size, state.mode) }

function handleSizeChange(size: PuzzleSize) { initGame(size, state.mode) }

onMounted(() => {
  restoreOrInit()
  solverPathRef.value = []
  solverStepRef.value = 0
})
</script>

<style scoped>
.app-container { width: 100%; max-width: var(--max-width, 500px); display: flex; flex-direction: column; align-items: center; }
.board-wrapper { position: relative; width: 100%; display: flex; justify-content: center; }
</style>
