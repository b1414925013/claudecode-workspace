import type { TagDef, EdgeTypeDef, VertexData, EdgeData, PropDef, ParsedGraph, TagColor } from '../types/nebula'

const PROP_TYPES = ['string', 'int', 'float', 'double', 'bool', 'date'] as const

function parsePropDefs(propsStr: string): PropDef[] {
  const props: PropDef[] = []
  const re = /(\w+)\s+(\w+)(?:\s*=\s*([^,)]+))?/g
  let m: RegExpExecArray | null
  while ((m = re.exec(propsStr)) !== null) {
    const type = m[2].toLowerCase()
    if (PROP_TYPES.includes(type as any)) {
      props.push({ name: m[1], type: type as PropDef['type'], default: m[3]?.trim() })
    }
  }
  return props
}

function hslToHex(h: number, s: number, l: number): string {
  s /= 100
  l /= 100
  const a = s * Math.min(l, 1 - l)
  const f = (n: number) => {
    const k = (n + h / 30) % 12
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
    return Math.round(255 * color).toString(16).padStart(2, '0')
  }
  return `#${f(0)}${f(8)}${f(4)}`
}

function generateHslColors(count: number): string[] {
  const colors: string[] = []
  for (let i = 0; i < count; i++) {
    const hue = (i * 360) / count
    const sat = 55 + (i % 3) * 10
    const light = 45 + (i % 2) * 10
    colors.push(hslToHex(hue, sat, light))
  }
  return colors
}

export function generateColorMap(
  tags: TagDef[],
  edgeTypes: EdgeTypeDef[]
): { tagColors: TagColor[]; edgeColors: TagColor[] } {
  const tagColors = tags.map((t, i) => {
    const colors = generateHslColors(Math.max(tags.length, 1))
    return { tag: t.name, color: colors[i], border: '#ffffff' }
  })
  const edgeColors = edgeTypes.map((e, i) => {
    const colors = generateHslColors(Math.max(edgeTypes.length, 1))
    return { tag: e.name, color: colors[i], border: '#ffffff' }
  })
  return { tagColors, edgeColors }
}

export function parseNGql(input: string): ParsedGraph {
  const result: ParsedGraph = {
    tags: [],
    edgeTypes: [],
    vertices: [],
    edges: [],
  }

  const cleanLines = input.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('--'))
  const joined = cleanLines.join('\n')

  // 1) Parse CREATE TAG
  const tagRe = /CREATE\s+TAG\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([\s\S]*?)\)\s*;/gi
  let m: RegExpExecArray | null
  while ((m = tagRe.exec(joined)) !== null) {
    result.tags.push({
      id: `tag_${result.tags.length}`,
      name: m[1],
      props: parsePropDefs(m[2]),
    })
  }

  // 2) Parse CREATE EDGE
  const edgeRe = /CREATE\s+EDGE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([\s\S]*?)\)\s*;/gi
  while ((m = edgeRe.exec(joined)) !== null) {
    result.edgeTypes.push({
      id: `edge_${result.edgeTypes.length}`,
      name: m[1],
      props: parsePropDefs(m[2]),
    })
  }

  // 3) Parse INSERT VERTEX
  // INSERT VERTEX [IF NOT EXISTS] <tag> (<prop_list>) VALUES "<vid>": (<val_list>)
  const vRe = /INSERT\s+VERTEX\s+(?:\w+\s+)?(\w+)\s*\(([^)]+)\)\s+VALUES\s+"([^"]+)"\s*:\s*\(([^)]+)\)/gi
  while ((m = vRe.exec(joined)) !== null) {
    const tagName = m[1]
    const propNames = m[2].split(',').map(s => s.trim())
    const rawValues = m[4].split(',').map(s => s.trim().replace(/^"|"$/g, ''))
    const props: Record<string, string> = {}
    propNames.forEach((name, i) => {
      props[name] = rawValues[i] || ''
    })
    result.vertices.push({
      id: `v_${result.vertices.length}`,
      vid: m[3],
      tagName,
      props,
    })
  }

  // 4) Parse INSERT EDGE
  // INSERT EDGE [IF NOT EXISTS] <edge_type> (<prop_list>) VALUES "<from>" -> "<to>" [@<rank>]: (<val_list>)
  const eRe = /INSERT\s+EDGE\s+(?:\w+\s+)?(\w+)\s*\(([^)]*)\)\s+VALUES\s+"([^"]+)"\s*->\s*"([^"]+)"\s*(?:@(\d+))?\s*:\s*\(([^)]*)\)/gi
  while ((m = eRe.exec(joined)) !== null) {
    const edgeType = m[1]
    const propNames = m[2].split(',').map(s => s.trim()).filter(Boolean)
    const rawValues = m[6].split(',').map(s => s.trim().replace(/^"|"$/g, ''))
    const props: Record<string, string> = {}
    propNames.forEach((name, i) => {
      props[name] = rawValues[i] || ''
    })
    result.edges.push({
      id: `e_${result.edges.length}`,
      edgeType,
      fromVid: m[3],
      toVid: m[4],
      rank: m[5] ? parseInt(m[5], 10) : undefined,
      props,
    })
  }

  return result
}
