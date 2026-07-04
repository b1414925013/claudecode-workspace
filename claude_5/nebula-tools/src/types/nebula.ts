export interface PropDef {
  name: string
  type: 'string' | 'int' | 'float' | 'double' | 'bool' | 'date'
  default?: string
}

export interface TagDef {
  id: string
  name: string
  props: PropDef[]
}

export interface EdgeTypeDef {
  id: string
  name: string
  props: PropDef[]
}

export interface VertexData {
  id: string
  vid: string
  tagName: string
  props: Record<string, string>
}

export interface EdgeData {
  id: string
  edgeType: string
  fromVid: string
  toVid: string
  rank?: number
  props: Record<string, string>
}

export interface ParsedGraph {
  tags: TagDef[]
  edgeTypes: EdgeTypeDef[]
  vertices: VertexData[]
  edges: EdgeData[]
}

export interface GraphNode extends Record<string, unknown> {
  id: string
  label: string
  tagName: string
  props: Record<string, string>
  type: 'vertex'
}

export interface GraphEdge {
  id: string
  from: string
  to: string
  edgeType: string
  label: string
  props: Record<string, string>
}

export interface TagColor {
  tag: string
  color: string
  border: string
}
