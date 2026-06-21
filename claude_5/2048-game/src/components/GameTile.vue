<template>
  <div
    class="tile"
    :class="[tileClass, { 'tile--new': tile.isNew, 'tile--merged': tile.isMerged }]"
    :style="tilePosition"
  >
    {{ tile.value }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TileData } from '../types/game'

const props = defineProps<{
  tile: TileData
  cellSize: number
  gap: number
}>()

const tileClass = computed(() => {
  const v = props.tile.value
  if (v >= 8192) return 'tile-super'
  if (v <= 2048) return `tile-${v}`
  return 'tile-super'
})

const tilePosition = computed(() => ({
  transform: `translate(${props.tile.col * (props.cellSize + props.gap) + props.gap}px, ${props.tile.row * (props.cellSize + props.gap) + props.gap}px)`,
  width: `${props.cellSize}px`,
  height: `${props.cellSize}px`,
  lineHeight: `${props.cellSize}px`,
  fontSize: props.cellSize > 60
    ? (props.tile.value >= 1024 ? '1.6rem' : '2.5rem')
    : (props.tile.value >= 1024 ? '1.1rem' : '1.6rem'),
}))
</script>

<style scoped>
.tile {
  position: absolute;
  top: 0;
  left: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  border-radius: 4px;
  z-index: 10;
  transition: transform 100ms ease;
  will-change: transform;
  pointer-events: none;
}

.tile--new {
  animation: tile-pop-in 200ms ease-out;
}

.tile--merged {
  animation: tile-pulse 200ms ease-in-out;
}

@keyframes tile-pop-in {
  0%   { transform: scale(0); opacity: 0; }
  50%  { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes tile-pulse {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.15); }
  100% { transform: scale(1); }
}
</style>
