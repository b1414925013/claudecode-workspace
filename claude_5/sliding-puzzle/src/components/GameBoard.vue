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

const emit = defineEmits<{ move: [index: number] }>()

const GAP = 4
const boardRef = ref<HTMLDivElement | null>(null)
const boardWidth = ref(500)

const cellSize = computed(() => (boardWidth.value - GAP * (props.size + 1)) / props.size)

const boardStyle = computed(() => ({
  width: `${boardWidth.value}px`,
  height: `${boardWidth.value}px`,
}))

function updateBoardWidth() {
  if (boardRef.value?.parentElement) {
    const parentW = boardRef.value.parentElement.clientWidth
    boardWidth.value = Math.max(Math.min(parentW - 32, 500), 280)
  }
}

function onTileClick(index: number) { emit('move', index) }

let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  updateBoardWidth()
  resizeObserver = new ResizeObserver(updateBoardWidth)
  if (boardRef.value?.parentElement) resizeObserver.observe(boardRef.value.parentElement)
})

onBeforeUnmount(() => resizeObserver?.disconnect())
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
