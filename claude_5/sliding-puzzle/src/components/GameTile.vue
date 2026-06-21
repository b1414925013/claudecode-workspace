<template>
  <div class="tile-pos" :style="positionStyle">
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
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
  transition: box-shadow 0.1s;
}
.tile:active { box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
.tile-image {
  width: 100%;
  height: 100%;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}
.tile-text { font-size: 1.5rem; font-weight: bold; }
</style>
