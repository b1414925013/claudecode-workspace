<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  script: string
}>()

const copyLabel = ref('复制')

watch(() => props.script, () => {
  copyLabel.value = '复制'
})

function copy() {
  navigator.clipboard.writeText(props.script).then(() => {
    copyLabel.value = '✓ 已复制'
    setTimeout(() => { copyLabel.value = '复制' }, 2000)
  })
}

function download() {
  const blob = new Blob([props.script], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'schema.ngql'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="preview">
    <div class="preview-header">
      <span class="preview-title">生成的 nGQL 脚本</span>
      <div class="preview-actions">
        <button class="btn btn-primary" @click="copy">{{ copyLabel }}</button>
        <button class="btn btn-secondary" @click="download">下载</button>
      </div>
    </div>
    <pre class="preview-code"><code>{{ script || '-- 请在上方表单中添加数据' }}</code></pre>
  </div>
</template>

<style scoped>
.preview {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-top: 1px solid var(--border);
}
.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: var(--bg-panel);
  flex-shrink: 0;
}
.preview-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}
.preview-actions {
  display: flex;
  gap: 6px;
}
.preview-code {
  flex: 1;
  margin: 0;
  padding: 16px;
  background: #0a0a14;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.6;
  overflow: auto;
  white-space: pre;
  tab-size: 2;
}
</style>
