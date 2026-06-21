<template>
  <div
    ref="boardRef"
    class="board"
    :style="gridStyle"
    tabindex="0"
    role="grid"
    aria-label="2048 游戏棋盘"
    @keydown.prevent="onKeyDown"
    @touchstart.prevent="onTouchStart"
    @touchmove.prevent="onTouchMove"
    @touchend.prevent="onTouchEnd"
  >
    <div
      v-for="i in boardSize * boardSize"
      :key="'cell-' + i"
      class="cell"
    ></div>

    <GameTile
      v-for="tile in tiles"
      :key="tile.id"
      :tile="tile"
      :cell-size="cellSize"
      :gap="gap"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import type { BoardSize, Direction, TileData } from '../types/game'
import GameTile from './GameTile.vue'

const props = defineProps<{
  tiles: TileData[]
  boardSize: BoardSize
}>()

const emit = defineEmits<{
  move: [direction: Direction]
}>()

const gap = 8
const boardRef = ref<HTMLDivElement | null>(null)
const boardWidth = ref(500)

const cellSize = computed(() => {
  return (boardWidth.value - gap * (props.boardSize + 1)) / props.boardSize
})

const gridStyle = computed(() => ({
  width: `${boardWidth.value}px`,
  height: `${boardWidth.value}px`,
  gridTemplateColumns: `repeat(${props.boardSize}, ${cellSize.value}px)`,
  gridTemplateRows: `repeat(${props.boardSize}, ${cellSize.value}px)`,
  gap: `${gap}px`,
  padding: `${gap}px`,
}))

function updateBoardWidth() {
  if (boardRef.value?.parentElement) {
    const parentW = boardRef.value.parentElement.clientWidth
    const maxW = Math.min(parentW - 32, 500)
    boardWidth.value = Math.max(maxW, 280)
  }
}

const keyMap: Record<string, Direction> = {
  ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right',
}

function onKeyDown(e: KeyboardEvent) {
  const dir = keyMap[e.key]
  if (dir) {
    e.preventDefault()
    emit('move', dir)
  }
}

let touchStartX = 0
let touchStartY = 0
const MIN_SWIPE = 20

function onTouchStart(e: TouchEvent) {
  const t = e.touches[0]
  touchStartX = t.clientX
  touchStartY = t.clientY
}

function onTouchMove(_e: TouchEvent) {
  /* prevent scroll while swiping */
}

function onTouchEnd(e: TouchEvent) {
  const t = e.changedTouches[0]
  const dx = t.clientX - touchStartX
  const dy = t.clientY - touchStartY
  const absDx = Math.abs(dx)
  const absDy = Math.abs(dy)

  if (Math.max(absDx, absDy) < MIN_SWIPE) return

  if (absDx > absDy) {
    emit('move', dx > 0 ? 'right' : 'left')
  } else {
    emit('move', dy > 0 ? 'down' : 'up')
  }
}

let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  updateBoardWidth()
  boardRef.value?.focus()
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
  display: grid;
  outline: none;
  touch-action: none;
}

.cell {
  background: var(--cell-bg);
  border-radius: 4px;
}
</style>
