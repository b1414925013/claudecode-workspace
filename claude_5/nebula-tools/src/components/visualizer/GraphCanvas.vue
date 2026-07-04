<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, shallowRef } from 'vue'
import type { ParsedGraph, TagColor } from '../../types/nebula'

const props = defineProps<{
  parsed: ParsedGraph
  tagColors: TagColor[]
  edgeColors: TagColor[]
}>()

const emit = defineEmits<{
  nodeClick: [data: { id: string; vid: string; tagName: string; props: Record<string, string>; neighbors: string[] }]
  backgroundClick: []
}>()

const containerRef = ref<HTMLDivElement>()
let network: any = null
const networkRef = shallowRef<any>(null)

function colorForTag(tagName: string): string {
  const found = props.tagColors.find(t => t.tag === tagName)
  return found?.color || '#666'
}

function colorForEdge(edgeType: string): string {
  const found = props.edgeColors.find(e => e.tag === edgeType)
  return found?.color || '#888'
}

function buildVisData() {
  const g = (window as any).vis
  if (!g || !props.parsed) return null

  const { vertices, edges } = props.parsed

  const nodes = vertices.map(v => ({
    id: v.vid,
    label: `${v.vid} (${v.tagName})`,
    title: `${v.vid} | Tag: ${v.tagName} | ${Object.entries(v.props).map(([k, val]) => `${k}: ${val}`).join(' | ')}`,
    color: { background: colorForTag(v.tagName), border: '#ffffff' },
    size: 20,
    shape: 'dot',
    borderWidth: 1.5,
    tagName: v.tagName,
    props: v.props,
  }))

  const visEdges = edges.map((e, i) => ({
    id: `e_${i}`,
    from: e.fromVid,
    to: e.toVid,
    label: e.edgeType,
    title: `${e.edgeType} | From: ${e.fromVid} → ${e.toVid}${e.rank !== undefined ? ` | Rank: ${e.rank}` : ''}`,
    color: { color: colorForEdge(e.edgeType), highlight: colorForEdge(e.edgeType) },
    dashes: false,
    width: 1.5,
    arrows: { to: { enabled: true, scaleFactor: 0.5 } },
    smooth: { type: 'continuous', roundness: 0.2 },
    edgeType: e.edgeType,
  }))

  if (visEdges.length === 0 && nodes.length === 0) return null

  return { nodes, edges: visEdges }
}

function renderGraph() {
  const g = (window as any).vis
  if (!containerRef.value || !g) return

  const data = buildVisData()
  if (!data) {
    if (network) { network.destroy(); network = null }
    return
  }

  const { nodes, edges } = data

  const options = {
    physics: {
      enabled: true,
      solver: 'forceAtlas2Based',
      forceAtlas2Based: {
        gravitationalConstant: -60,
        centralGravity: 0.005,
        springLength: 120,
        springConstant: 0.08,
        damping: 0.4,
        avoidOverlap: 0.8,
      },
      stabilization: { iterations: 200, fit: true },
    },
    interaction: {
      hover: true,
      tooltipDelay: 100,
      hideEdgesOnDrag: true,
    },
    nodes: { shape: 'dot', borderWidth: 1.5 },
    edges: { smooth: { type: 'continuous', roundness: 0.2 }, selectionWidth: 2 },
  }

  if (network) {
    network.setData({ nodes: new g.DataSet(nodes), edges: new g.DataSet(edges) })
    network.setOptions(options)
    network.fit({ animation: true })
  } else {
    network = new g.Network(
      containerRef.value,
      { nodes: new g.DataSet(nodes), edges: new g.DataSet(edges) },
      options
    )

    network.once('stabilizationIterationsDone', () => {
      network.setOptions({ physics: { enabled: false } })
      network.fit()
    })

    network.on('click', (params: any) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0]
        const nodeData = props.parsed.vertices.find(v => v.vid === nodeId)
        if (nodeData) {
          const neighbors = network.getConnectedNodes(nodeId) as string[]
          emit('nodeClick', {
            id: nodeId,
            vid: nodeData.vid,
            tagName: nodeData.tagName,
            props: nodeData.props,
            neighbors,
          })
        }
      } else {
        emit('backgroundClick')
      }
    })

    network.on('hoverNode', () => {
      if (containerRef.value) containerRef.value.style.cursor = 'pointer'
    })
    network.on('blurNode', () => {
      if (containerRef.value) containerRef.value.style.cursor = 'default'
    })
  }

  networkRef.value = network
}

watch(() => [props.parsed, props.tagColors, props.edgeColors], renderGraph, { deep: false })

onMounted(renderGraph)
onUnmounted(() => {
  if (network) network.destroy()
})

function focusNode(id: string) {
  if (network) {
    network.focus(id, { scale: 1.4, animation: true })
    network.selectNodes([id])
  }
}
function fit() {
  if (network) network.fit({ animation: true })
}
function togglePhysics(on: boolean) {
  if (network) network.setOptions({ physics: { enabled: on } })
}

defineExpose({ focusNode, fit, togglePhysics })
</script>

<template>
  <div ref="containerRef" class="graph-canvas" />
</template>

<style scoped>
.graph-canvas {
  width: 100%;
  height: 100%;
  background: var(--bg-primary);
}
</style>
