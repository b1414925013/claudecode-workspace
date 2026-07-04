import { ref, watch, shallowRef } from 'vue'
import { parseNGql, generateColorMap } from '../parser/nGqlParser'
import type { ParsedGraph, TagColor } from '../types/nebula'

export function useNebulaParser(input: { value: string }) {
  const parsed = shallowRef<ParsedGraph>({ tags: [], edgeTypes: [], vertices: [], edges: [] })
  const tagColors = ref<TagColor[]>([])
  const edgeColors = ref<TagColor[]>([])
  const error = ref<string | null>(null)
  const summary = ref('')

  let timer: ReturnType<typeof setTimeout> | null = null

  watch(() => input.value, (val) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      try {
        if (!val.trim()) {
          parsed.value = { tags: [], edgeTypes: [], vertices: [], edges: [] }
          tagColors.value = []
          edgeColors.value = []
          error.value = null
          summary.value = ''
          return
        }
        const result = parseNGql(val)
        parsed.value = result
        const colors = generateColorMap(result.tags, result.edgeTypes)
        tagColors.value = colors.tagColors
        edgeColors.value = colors.edgeColors
        error.value = null
        const parts: string[] = []
        if (result.tags.length) parts.push(`${result.tags.length} 个 TAG`)
        if (result.vertices.length) parts.push(`${result.vertices.length} 个 VERTEX`)
        if (result.edgeTypes.length) parts.push(`${result.edgeTypes.length} 个 EDGE 类型`)
        if (result.edges.length) parts.push(`${result.edges.length} 个 EDGE`)
        summary.value = `✓ 解析成功 — ${parts.join(', ') || '未识别到有效语句'}`
      } catch (e: any) {
        error.value = `✗ 解析错误: ${e.message}`
        summary.value = ''
      }
    }, 300)
  }, { immediate: true })

  return { parsed, tagColors, edgeColors, error, summary }
}
