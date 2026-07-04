<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { EditorView, basicSetup } from 'codemirror'
import { EditorState } from '@codemirror/state'
import { oneDark } from '@codemirror/theme-one-dark'
import { StreamLanguage } from '@codemirror/language'

// Simple nGQL keyword highlighting
const nGqlLang = StreamLanguage.define({
  token(stream: any) {
    if (stream.eatSpace()) return null
    if (stream.match(/^(CREATE|TAG|EDGE|VERTEX|INSERT|VALUES|SPACE|USE|IF|NOT|EXISTS|ALTER|DROP|INDEX|SHOW|DESCRIBE|DELETE|UPDATE|YIELD|GO|FETCH|LOOKUP|SET|FROM|WHERE|ORDER\s+BY|LIMIT|GROUP\s+BY|UNION|INTERSECT|MINUS)\b/i)) return 'keyword'
    if (stream.match(/^(string|int|float|double|bool|date|timestamp)\b/i)) return 'typeName'
    if (stream.match(/^"([^"]*)"/)) return 'string'
    if (stream.match(/^'([^']*)'/)) return 'string'
    if (stream.match(/^\d+(\.\d+)?/)) return 'number'
    if (stream.match(/^--.*/)) return 'comment'
    if (stream.match(/^->/)) return 'arrow'
    stream.next()
    return null
  },
})

const props = defineProps<{
  modelValue: string
  summary?: string
  error?: string | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const editorRef = ref<HTMLDivElement>()
let view: EditorView | null = null

onMounted(() => {
  if (!editorRef.value) return

  const startState = EditorState.create({
    doc: props.modelValue,
    extensions: [
      basicSetup,
      oneDark,
      nGqlLang,
      EditorView.updateListener.of(update => {
        if (update.docChanged) {
          emit('update:modelValue', update.state.doc.toString())
        }
      }),
    ],
  })

  view = new EditorView({
    state: startState,
    parent: editorRef.value,
  })
})

watch(() => props.modelValue, (val) => {
  if (view && val !== view.state.doc.toString()) {
    view.dispatch({
      changes: { from: 0, to: view.state.doc.length, insert: val },
    })
  }
})
</script>

<template>
  <div class="ngql-editor">
    <div class="editor-head">
      <span class="editor-label">nGQL 脚本</span>
      <span v-if="summary" class="status success">{{ summary }}</span>
      <span v-else-if="error" class="status error">{{ error }}</span>
    </div>
    <div ref="editorRef" class="editor-body" />
  </div>
</template>

<style scoped>
.ngql-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-panel);
  border-right: 1px solid var(--border);
}
.editor-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  gap: 8px;
}
.editor-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  flex-shrink: 0;
}
.status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.status.success { color: var(--success); background: rgba(46, 204, 113, 0.1); }
.status.error { color: var(--danger); background: rgba(231, 76, 60, 0.1); }
.editor-body {
  flex: 1;
  overflow: auto;
}
.editor-body :deep(.cm-editor) {
  height: 100%;
}
.editor-body :deep(.cm-scroller) {
  font-family: var(--font-mono);
  font-size: 13px;
}
.editor-body :deep(.cm-content) {
  padding: 8px 0;
}
.editor-body :deep(.ͼ1 .cm-keyword) { color: #c678dd; font-weight: 600; }
.editor-body :deep(.ͼ1 .cm-typeName) { color: #61afef; }
.editor-body :deep(.ͼ1 .cm-string) { color: #98c379; }
.editor-body :deep(.ͼ1 .cm-number) { color: #d19a66; }
.editor-body :deep(.ͼ1 .cm-comment) { color: #5c6370; font-style: italic; }
</style>
