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
    <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileSelected" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import presets from '../assets/presets'

const props = defineProps<{ selectedImage: string | null }>()
const emit = defineEmits<{ selectImage: [url: string | null] }>()

const fileInput = ref<HTMLInputElement | null>(null)

function select(url: string) { emit('selectImage', url) }

function triggerUpload() { fileInput.value?.click() }

function onFileSelected(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]
  if (!file.type.startsWith('image/')) { alert('请选择图片文件'); return }

  const reader = new FileReader()
  reader.onload = () => {
    const dataUrl = reader.result as string
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const size = 400
      canvas.width = size; canvas.height = size
      const ctx = canvas.getContext('2d')!
      ctx.drawImage(img, 0, 0, size, size)
      emit('selectImage', canvas.toDataURL('image/jpeg', 0.9))
    }
    img.src = dataUrl
  }
  reader.readAsDataURL(file)
}
</script>

<style scoped>
.picker { width: 100%; max-width: 500px; margin-top: 12px; }
.picker-title { font-size: 0.85rem; margin-bottom: 8px; color: var(--text-color); opacity: 0.8; }
.presets { display: flex; gap: 10px; flex-wrap: wrap; }
.preset-item {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  cursor: pointer; padding: 6px; border-radius: var(--radius); border: 2px solid transparent; transition: border-color 0.15s;
}
.preset-item.active { border-color: var(--btn-bg); }
.preset-item:hover { border-color: var(--btn-hover); }
.preset-thumb { width: 60px; height: 60px; border-radius: 4px; background-size: cover; background-position: center; }
.upload-thumb {
  display: flex; justify-content: center; align-items: center;
  font-size: 2rem; color: var(--text-color); border: 2px dashed var(--text-color); opacity: 0.5;
}
.preset-name { font-size: 0.7rem; color: var(--text-color); opacity: 0.7; }
</style>
