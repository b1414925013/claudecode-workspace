# Nebula Tools Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build two Vue 3 tools — parse nGQL into interactive graph visualizations, and provide a GUI form to define graph schemas/data then auto-generate nGQL scripts.

**Architecture:** Standalone Vite + Vue 3 + TypeScript project (`nebula-tools/`). Two pages via vue-router: `/visualize` uses CodeMirror 6 for nGQL input + vis-network for graph rendering; `/builder` uses form components (backed by SimpleTable) that drive a composable to emit nGQL. All styling is hand-written CSS with dark theme. No backend — 100% browser-side.

**Tech Stack:** Vue 3.5+, Vite 6+, TypeScript 5+, vue-router 4, vis-network 9, CodeMirror 6

## Global Constraints

- Node.js >= 18 required
- No UI framework dependency — all CSS hand-written
- All tooling is browser-only, zero server dependencies
- vis-network loaded from unpkg CDN in index.html (no npm package)
- CodeMirror 6 loaded via npm (`codemirror`, `@codemirror/view`, `@codemirror/state`, `@codemirror/lang-javascript`, `@codemirror/theme-one-dark`)
- Dark theme colors: `--bg-primary: #0f0f1a; --bg-panel: #1a1a2e; --border: #2a2a4e; --text-primary: #e0e0e0; --accent: #4E79A7;`
- No unit test framework — verification is manual in browser via `npm run dev`

---

### Task 1: Project Scaffolding

**Files:**
- Create: `nebula-tools/package.json`
- Create: `nebula-tools/vite.config.ts`
- Create: `nebula-tools/tsconfig.json`
- Create: `nebula-tools/tsconfig.node.json`
- Create: `nebula-tools/index.html`
- Create: `nebula-tools/env.d.ts`
- Create: `nebula-tools/src/main.ts`
- Create: `nebula-tools/src/App.vue`

**Interfaces:**
- Produces: A runnable `npm run dev` Vite project skeleton

- [ ] **Step 1: Create package.json**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\package.json`:

```json
{
  "name": "nebula-tools",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.5.0",
    "codemirror": "^6.0.1",
    "@codemirror/view": "^6.36.0",
    "@codemirror/state": "^6.5.0",
    "@codemirror/lang-javascript": "^6.2.0",
    "@codemirror/theme-one-dark": "^6.1.0",
    "@codemirror/language": "^6.10.0",
    "@codemirror/commands": "^6.8.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.0",
    "typescript": "~5.7.0",
    "vite": "^6.3.0",
    "vue-tsc": "^2.2.0"
  }
}
```

- [ ] **Step 2: Create vite.config.ts**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': '/src' }
  }
})
```

- [ ] **Step 3: Create tsconfig files**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue", "env.d.ts"]
}
```

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\tsconfig.node.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 4: Create index.html**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Nebula Tools</title>
</head>
<body>
  <div id="app"></div>
  <script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"
    integrity="sha384-Ux6phic9PEHJ38YtrijhkzyJ8yQlH8i/+buBR8s3mAZOJrP1gwyvAcIYl3GWtpX1"
    crossorigin="anonymous"></script>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [ ] **Step 5: Create env.d.ts**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\env.d.ts`:

```typescript
/// <reference types="vite/client" />
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

- [ ] **Step 6: Create src/main.ts**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\main.ts`:

```typescript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/theme.css'

const app = createApp(App)
app.use(router)
app.mount('#app')
```

- [ ] **Step 7: Create App.vue (skeleton — router-view only)**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\App.vue`:

```vue
<script setup lang="ts">
import NavBar from './components/layout/NavBar.vue'
</script>

<template>
  <div class="app-shell">
    <NavBar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}
.main-content {
  flex: 1;
  overflow: hidden;
}
</style>
```

- [ ] **Step 8: Install dependencies and verify dev server starts**

Run:
```bash
cd "D:/develop/claudecode-workspace/claude_5/nebula-tools" && npm install
```
Expected: All packages install without errors.

- [ ] **Step 9: Commit**

```bash
git add nebula-tools/
git commit -m "feat(nebula-tools): scaffold Vite + Vue 3 project"
```

---

### Task 2: Types + Theme CSS

**Files:**
- Create: `nebula-tools/src/types/nebula.ts`
- Create: `nebula-tools/src/styles/theme.css`

**Interfaces:**
- Produces: Shared TypeScript type definitions (`TagDef`, `EdgeTypeDef`, `VertexData`, `EdgeData`, `PropDef`, `ParsedGraph`) and CSS variables consumed by all components

- [ ] **Step 1: Create types/nebula.ts**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\types\nebula.ts`:

```typescript
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

// For vis-network node/edge color configuration
export interface TagColor {
  tag: string
  color: string
  border: string
}
```

- [ ] **Step 2: Create styles/theme.css**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\styles\theme.css`:

```css
:root {
  --bg-primary: #0f0f1a;
  --bg-panel: #1a1a2e;
  --bg-float: rgba(26, 26, 46, 0.88);
  --bg-hover: #2a2a4e;
  --border: #2a2a4e;
  --border-focus: #4E79A7;
  --text-primary: #e0e0e0;
  --text-secondary: #aaa;
  --text-muted: #555;
  --accent: #4E79A7;
  --accent-hover: #5a8fc7;
  --danger: #e74c3c;
  --success: #2ecc71;
  --warning: #f39c12;
  --radius: 8px;
  --radius-sm: 4px;
  --shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  --font-mono: 'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  overflow: hidden;
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-sans);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  color: var(--accent-hover);
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

input, select, textarea, button {
  font-family: inherit;
  font-size: inherit;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--border-focus);
}
```

- [ ] **Step 3: Commit**

```bash
git add nebula-tools/
git commit -m "feat(nebula-tools): add type definitions and dark theme CSS"
```

---

### Task 3: Router + NavBar + Home Page

**Files:**
- Create: `nebula-tools/src/router/index.ts`
- Create: `nebula-tools/src/components/layout/NavBar.vue`
- Create: `nebula-tools/src/pages/Home.vue`

**Interfaces:**
- Consumes: CSS variables from theme.css
- Produces: `router` instance imported by main.ts; NavBar component used by App.vue; Home component as default route

- [ ] **Step 1: Create router/index.ts**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\router\index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/nebula-tools/'),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../pages/Home.vue'),
    },
    {
      path: '/visualize',
      name: 'visualize',
      component: () => import('../pages/Visualizer.vue'),
    },
    {
      path: '/builder',
      name: 'builder',
      component: () => import('../pages/Builder.vue'),
    },
  ],
})

export default router
```

- [ ] **Step 2: Create NavBar.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\layout\NavBar.vue`:

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const links = [
  { path: '/', label: 'Home', icon: '⌂' },
  { path: '/visualize', label: 'Visualizer', icon: '◉' },
  { path: '/builder', label: 'Builder', icon: '⚙' },
]
</script>

<template>
  <nav class="navbar">
    <span class="navbar-brand">Nebula Tools</span>
    <div class="navbar-links">
      <router-link
        v-for="link in links"
        :key="link.path"
        :to="link.path"
        class="nav-link"
        :class="{ active: router.currentRoute.value.path === link.path }"
      >
        <span class="nav-icon">{{ link.icon }}</span>
        {{ link.label }}
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  gap: 24px;
  height: 44px;
  padding: 0 20px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  user-select: none;
}
.navbar-brand {
  font-weight: 600;
  font-size: 14px;
  color: var(--accent);
  letter-spacing: 0.03em;
}
.navbar-links {
  display: flex;
  gap: 4px;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-secondary);
  transition: background 0.15s, color 0.15s;
}
.nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.nav-link.active {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.nav-icon {
  font-size: 14px;
}
</style>
```

- [ ] **Step 3: Create Home.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\pages\Home.vue`:

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const tools = [
  {
    title: 'Visualizer',
    icon: '◉',
    description: '输入 nGQL 脚本，自动解析并渲染为交互式图可视化。支持点、边、属性展示，适合数据探索与调试。',
    path: '/visualize',
    color: '#4E79A7',
  },
  {
    title: 'Builder',
    icon: '⚙',
    description: '通过 GUI 表单定义点类型、边类型及数据，自动生成完整的 nGQL 脚本。支持一键复制与下载。',
    path: '/builder',
    color: '#59A14F',
  },
]
</script>

<template>
  <div class="home">
    <div class="hero">
      <h1 class="hero-title">Nebula Tools</h1>
      <p class="hero-subtitle">Nebula Graph 可视化工具集 — 解析 nGQL 脚本与 GUI 构建</p>
    </div>
    <div class="cards">
      <div
        v-for="tool in tools"
        :key="tool.title"
        class="card"
        :style="{ '--card-color': tool.color }"
        @click="router.push(tool.path)"
      >
        <div class="card-icon">{{ tool.icon }}</div>
        <div class="card-body">
          <h2 class="card-title">{{ tool.title }}</h2>
          <p class="card-desc">{{ tool.description }}</p>
        </div>
        <div class="card-action">打开 →</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
  gap: 48px;
}
.hero {
  text-align: center;
}
.hero-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}
.hero-subtitle {
  margin-top: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}
.cards {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  justify-content: center;
}
.card {
  width: 320px;
  padding: 28px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.card:hover {
  transform: translateY(-3px);
  border-color: var(--card-color, var(--accent));
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}
.card-icon {
  font-size: 36px;
  line-height: 1;
}
.card-body {
  flex: 1;
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}
.card-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}
.card-action {
  font-size: 13px;
  color: var(--card-color, var(--accent));
  font-weight: 500;
}
</style>
```

- [ ] **Step 4: Verify in browser**

Run:
```bash
cd "D:/develop/claudecode-workspace/claude_5/nebula-tools" && npm run dev
```
Expected: Dev server starts. Visit http://localhost:5173/nebula-tools/ — see the Home page with two cards. Click them — they navigate to /visualize and /builder (blank pages for now). Verify navbar shows all three links and active state works.

- [ ] **Step 5: Commit**

```bash
git add nebula-tools/
git commit -m "feat(nebula-tools): add router, NavBar, and Home page"
```

---

### Task 4: nGQL Parser Engine

**Files:**
- Create: `nebula-tools/src/parser/nGqlParser.ts`

**Interfaces:**
- Consumes: Types from `types/nebula.ts` (`TagDef`, `EdgeTypeDef`, `VertexData`, `EdgeData`, `PropDef`, `ParsedGraph`)
- Produces: `function parseNGql(input: string): ParsedGraph` — the core parsing function; `function generateColorMap(tags: TagDef[], edgeTypes: EdgeTypeDef[]): { tagColors: TagColor[], edgeColors: TagColor[] }` — stable color assignment per tag/edge type

- [ ] **Step 1: Create nGqlParser.ts with regex rules and parseNGql export**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\parser\nGqlParser.ts`:

```typescript
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

const HEX_CHARS = '0123456789abcdef'

function hslToHex(h: number, s: number, l: number): string {
  s /= 100
  l /= 100
  const a = s * Math.min(l, 1 - l)
  const f = (n: number) => {
    const k = (n + h / 30) % 12
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
    return Math.round(255 * color)
      .toString(16)
      .padStart(2, '0')
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

  const lines = input.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('--'))

  // 1) Parse CREATE TAG
  const tagRe = /CREATE\s+TAG\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([\s\S]*?)\)\s*;/gi
  let m: RegExpExecArray | null
  while ((m = tagRe.exec(lines.join('\n'))) !== null) {
    result.tags.push({
      id: `tag_${result.tags.length}`,
      name: m[1],
      props: parsePropDefs(m[2]),
    })
  }

  // 2) Parse CREATE EDGE
  const edgeRe = /CREATE\s+EDGE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([\s\S]*?)\)\s*;/gi
  while ((m = edgeRe.exec(lines.join('\n'))) !== null) {
    result.edgeTypes.push({
      id: `edge_${result.edgeTypes.length}`,
      name: m[1],
      props: parsePropDefs(m[2]),
    })
  }

  // Rejoin for data parsing (per-line patterns)
  const text = lines.join('\n')

  // 3) Parse INSERT VERTEX
  // INSERT VERTEX [IF NOT EXISTS] <tag> (<prop_list>) VALUES "<vid>": (<val_list>)
  const vRe = /INSERT\s+VERTEX\s+(?:\w+\s+)?(\w+)\s*\(([^)]+)\)\s+VALUES\s+"([^"]+)"\s*:\s*\(([^)]+)\)/gi
  while ((m = vRe.exec(text)) !== null) {
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
  while ((m = eRe.exec(text)) !== null) {
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
```

- [ ] **Step 2: Commit**

```bash
git add nebula-tools/
git commit -m "feat(nebula-tools): add nGQL parser engine"
```

---

### Task 5: useNebulaGenerator Composable + usePersistState

**Files:**
- Create: `nebula-tools/src/composables/useNebulaGenerator.ts`
- Create: `nebula-tools/src/composables/usePersistState.ts`

**Interfaces:**
- Consumes: `TagDef`, `EdgeTypeDef`, `VertexData`, `EdgeData` from types
- `useNebulaGenerator` returns: `{ generate(tags, edgeTypes, vertices, edges, spaceName?): string }`
- `usePersistState(key, defaultVal)` returns: `Ref<T>` auto-synced to localStorage

- [ ] **Step 1: Create usePersistState.ts**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\composables\usePersistState.ts`:

```typescript
import { ref, watch } from 'vue'
import type { Ref } from 'vue'

export function usePersistState<T>(key: string, defaultValue: T): Ref<T> {
  const stored = localStorage.getItem(key)
  const data = ref<T>(stored ? JSON.parse(stored) : defaultValue) as Ref<T>

  watch(data, (val) => {
    localStorage.setItem(key, JSON.stringify(val))
  }, { deep: true })

  return data
}
```

- [ ] **Step 2: Create useNebulaGenerator.ts**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\composables\useNebulaGenerator.ts`:

```typescript
import type { TagDef, EdgeTypeDef, VertexData, EdgeData } from '../types/nebula'

function quote(val: string): string {
  return `"${val.replace(/"/g, '\\"')}"`
}

function propList(props: Record<string, string>): string {
  return Object.keys(props).join(', ')
}

function valList(props: Record<string, string>): string {
  return Object.values(props).map(v => {
    const num = Number(v)
    return String(num) === v && v !== '' ? v : quote(v)
  }).join(', ')
}

export function useNebulaGenerator() {
  function generate(
    tags: TagDef[],
    edgeTypes: EdgeTypeDef[],
    vertices: VertexData[],
    edges: EdgeData[],
    spaceName?: string
  ): string {
    const lines: string[] = []
    lines.push('-- Generated by Nebula Tools', '')

    if (spaceName) {
      lines.push(`CREATE SPACE IF NOT EXISTS ${spaceName}(partition_num=10, replica_factor=1);`)
      lines.push(`USE ${spaceName};`, '')
    }

    // Tag definitions
    if (tags.length > 0) {
      for (const tag of tags) {
        const props = tag.props.map(p => `${p.name} ${p.type}${p.default ? ` = ${p.default}` : ''}`).join(', ')
        lines.push(`CREATE TAG IF NOT EXISTS ${tag.name}(${props});`)
      }
      lines.push('')
    }

    // Edge definitions
    if (edgeTypes.length > 0) {
      for (const et of edgeTypes) {
        const props = et.props.map(p => `${p.name} ${p.type}${p.default ? ` = ${p.default}` : ''}`).join(', ')
        lines.push(`CREATE EDGE IF NOT EXISTS ${et.name}(${props});`)
      }
      lines.push('')
    }

    // Vertex data
    if (vertices.length > 0) {
      for (const v of vertices) {
        const pNames = propList(v.props)
        const vVals = valList(v.props)
        lines.push(`INSERT VERTEX ${v.tagName}(${pNames}) VALUES ${quote(v.vid)}: (${vVals});`)
      }
      lines.push('')
    }

    // Edge data
    if (edges.length > 0) {
      for (const e of edges) {
        const pNames = propList(e.props)
        const eVals = valList(e.props)
        const rank = e.rank !== undefined ? ` @${e.rank}` : ''
        lines.push(`INSERT EDGE ${e.edgeType}(${pNames}) VALUES ${quote(e.fromVid)} -> ${quote(e.toVid)}${rank}: (${eVals});`)
      }
      lines.push('')
    }

    return lines.join('\n')
  }

  return { generate }
}
```

- [ ] **Step 3: Commit**

```bash
git add nebula-tools/
git commit -m "feat(nebula-tools): add useNebulaGenerator and usePersistState composables"
```

---

### Task 6: Common Components (SimpleTable + ConfirmDialog)

**Files:**
- Create: `nebula-tools/src/components/common/SimpleTable.vue`
- Create: `nebula-tools/src/components/common/ConfirmDialog.vue`

**Interfaces:**
- Produces: Reusable table component and modal dialog consumed by Builder tab editors

- [ ] **Step 1: Create ConfirmDialog.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\common\ConfirmDialog.vue`:

```vue
<script setup lang="ts">
defineProps<{
  title: string
  message: string
  visible: boolean
}>()
const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="dialog-overlay" @click.self="emit('cancel')">
      <div class="dialog-box">
        <h3 class="dialog-title">{{ title }}</h3>
        <p class="dialog-message">{{ message }}</p>
        <div class="dialog-actions">
          <button class="btn btn-secondary" @click="emit('cancel')">取消</button>
          <button class="btn btn-danger" @click="emit('confirm')">确认</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.dialog-box {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  min-width: 320px;
  box-shadow: var(--shadow);
}
.dialog-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}
.dialog-message {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 20px;
  line-height: 1.5;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
```

- [ ] **Step 2: Create SimpleTable.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\common\SimpleTable.vue`:

```vue
<script setup lang="ts">
defineProps<{
  columns: { key: string; label: string; width?: string }[]
  rows: Record<string, any>[]
}>()
const emit = defineEmits<{
  edit: [row: Record<string, any>]
  delete: [row: Record<string, any>]
}>()
</script>

<template>
  <table class="simple-table">
    <thead>
      <tr>
        <th v-for="col in columns" :key="col.key" :style="col.width ? { width: col.width } : {}">
          {{ col.label }}
        </th>
        <th class="th-actions">操作</th>
      </tr>
    </thead>
    <tbody>
      <tr v-if="rows.length === 0">
        <td :colspan="columns.length + 1" class="empty-row">暂无数据</td>
      </tr>
      <tr v-for="(row, idx) in rows" :key="idx">
        <td v-for="col in columns" :key="col.key" class="cell">
          {{ typeof row[col.key] === 'object' ? JSON.stringify(row[col.key]) : row[col.key] ?? '-' }}
        </td>
        <td class="cell-actions">
          <button class="btn-sm btn-edit" @click="emit('edit', row)">编辑</button>
          <button class="btn-sm btn-delete" @click="emit('delete', row)">删除</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.simple-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.simple-table th {
  text-align: left;
  padding: 8px 10px;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
.th-actions {
  width: 100px;
  text-align: center;
}
.simple-table td {
  padding: 8px 10px;
  border-bottom: 1px solid rgba(42, 42, 78, 0.5);
  color: var(--text-primary);
}
.cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.empty-row {
  text-align: center;
  color: var(--text-muted);
  padding: 20px !important;
}
.cell-actions {
  display: flex;
  gap: 4px;
  justify-content: center;
}
.btn-sm {
  padding: 3px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.15s;
}
.btn-edit {
  background: transparent;
  color: var(--accent);
  border-color: var(--accent);
}
.btn-edit:hover {
  background: var(--accent);
  color: #fff;
}
.btn-delete {
  background: transparent;
  color: var(--danger);
  border-color: var(--danger);
}
.btn-delete:hover {
  background: var(--danger);
  color: #fff;
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add nebula-tools/
git commit -m "feat(nebula-tools): add SimpleTable and ConfirmDialog components"
```

---

### Task 7: Builder Components (4 Tab Editors + ScriptPreview)

**Files:**
- Create: `nebula-tools/src/components/builder/TagDefEditor.vue`
- Create: `nebula-tools/src/components/builder/EdgeDefEditor.vue`
- Create: `nebula-tools/src/components/builder/VertexDataEditor.vue`
- Create: `nebula-tools/src/components/builder/EdgeDataEditor.vue`
- Create: `nebula-tools/src/components/builder/ScriptPreview.vue`

**Interfaces:**
- Consumes: `usePersistState`, `useNebulaGenerator`, types from `types/nebula.ts`
- Each editor emits: `@update` with its data array
- Produces: Self-contained Vue components wired into Builder.vue

- [ ] **Step 1: Create TagDefEditor.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\builder\TagDefEditor.vue`:

```vue
<script setup lang="ts">
import { ref } from 'vue'
import type { TagDef, PropDef } from '../../types/nebula'
import SimpleTable from '../common/SimpleTable.vue'
import ConfirmDialog from '../common/ConfirmDialog.vue'

const props = defineProps<{ items: TagDef[] }>()
const emit = defineEmits<{ update: [items: TagDef[]] }>()

const showDialog = ref(false)
const editingIdx = ref(-1)
const form = ref<TagDef>({ id: '', name: '', props: [] })

const columns = [
  { key: 'name', label: '标签名' },
  { key: 'props', label: '属性' },
]

function addNew() {
  editingIdx.value = -1
  form.value = { id: crypto.randomUUID(), name: '', props: [] }
  showDialog.value = true
}

function editRow(row: TagDef) {
  editingIdx.value = props.items.indexOf(row)
  form.value = JSON.parse(JSON.stringify(row))
  showDialog.value = true
}

function confirmDelete(row: TagDef) {
  const idx = props.items.indexOf(row)
  const next = [...props.items]
  next.splice(idx, 1)
  emit('update', next)
}

function save() {
  if (!form.value.name.trim()) return
  const next = [...props.items]
  if (editingIdx.value >= 0) {
    next[editingIdx.value] = { ...form.value }
  } else {
    next.push({ ...form.value })
  }
  emit('update', next)
  showDialog.value = false
}

function addProp() {
  form.value.props.push({ name: '', type: 'string' })
}

function removeProp(idx: number) {
  form.value.props.splice(idx, 1)
}
</script>

<template>
  <div class="editor-section">
    <div class="editor-header">
      <span class="editor-title">点类型 (Tag) 定义</span>
      <button class="btn btn-primary" @click="addNew">+ 添加 Tag</button>
    </div>
    <SimpleTable :columns="columns" :rows="items" @edit="editRow" @delete="confirmDelete" />

    <Teleport to="body">
      <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
        <div class="modal-box">
          <h3 class="modal-title">{{ editingIdx >= 0 ? '编辑' : '新增' }} Tag</h3>
          <div class="form-field">
            <label>标签名</label>
            <input v-model="form.name" class="input" placeholder="例如: person" />
          </div>
          <div class="form-field">
            <label>属性</label>
            <div v-for="(p, pi) in form.props" :key="pi" class="prop-row">
              <input v-model="p.name" class="input prop-name" placeholder="属性名" />
              <select v-model="p.type" class="input prop-type">
                <option v-for="t in ['string','int','float','double','bool','date']" :key="t" :value="t">{{ t }}</option>
              </select>
              <input v-model="p.default" class="input prop-default" placeholder="默认值(可选)" />
              <button class="btn-sm btn-delete" @click="removeProp(pi)">✕</button>
            </div>
            <button class="btn btn-text" @click="addProp">+ 添加属性</button>
          </div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDialog = false">取消</button>
            <button class="btn btn-primary" @click="save">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
```

- [ ] **Step 2: Create EdgeDefEditor.vue** (same pattern as TagDefEditor, for edge types)

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\builder\EdgeDefEditor.vue` — identical structure to TagDefEditor but title says "边类型 (Edge) 定义" and emits items typed as `EdgeTypeDef[]`.

```vue
<script setup lang="ts">
import { ref } from 'vue'
import type { EdgeTypeDef } from '../../types/nebula'
import SimpleTable from '../common/SimpleTable.vue'

const props = defineProps<{ items: EdgeTypeDef[] }>()
const emit = defineEmits<{ update: [items: EdgeTypeDef[]] }>()

const showDialog = ref(false)
const editingIdx = ref(-1)
const form = ref<EdgeTypeDef & { props: { name: string; type: string; default?: string }[] }>({
  id: '', name: '', props: [],
})

const columns = [{ key: 'name', label: '边类型名' }, { key: 'props', label: '属性' }]

function addNew() {
  editingIdx.value = -1
  form.value = { id: crypto.randomUUID(), name: '', props: [] }
  showDialog.value = true
}
function editRow(row: EdgeTypeDef) {
  editingIdx.value = props.items.indexOf(row)
  form.value = JSON.parse(JSON.stringify(row))
  showDialog.value = true
}
function confirmDelete(row: EdgeTypeDef) {
  const next = props.items.filter(r => r !== row)
  emit('update', next)
}
function save() {
  if (!form.value.name.trim()) return
  const next = [...props.items]
  if (editingIdx.value >= 0) next[editingIdx.value] = { ...form.value }
  else next.push({ ...form.value })
  emit('update', next)
  showDialog.value = false
}
function addProp() { form.value.props.push({ name: '', type: 'string' }) }
function removeProp(idx: number) { form.value.props.splice(idx, 1) }
</script>

<template>
  <div class="editor-section">
    <div class="editor-header">
      <span class="editor-title">边类型 (Edge) 定义</span>
      <button class="btn btn-primary" @click="addNew">+ 添加 Edge</button>
    </div>
    <SimpleTable :columns="columns" :rows="items" @edit="editRow" @delete="confirmDelete" />

    <Teleport to="body">
      <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
        <div class="modal-box">
          <h3 class="modal-title">{{ editingIdx >= 0 ? '编辑' : '新增' }} Edge</h3>
          <div class="form-field">
            <label>边类型名</label>
            <input v-model="form.name" class="input" placeholder="例如: knows" />
          </div>
          <div class="form-field">
            <label>属性</label>
            <div v-for="(p, pi) in form.props" :key="pi" class="prop-row">
              <input v-model="p.name" class="input prop-name" placeholder="属性名" />
              <select v-model="p.type" class="input prop-type">
                <option v-for="t in ['string','int','float','double','bool','date']" :key="t" :value="t">{{ t }}</option>
              </select>
              <input v-model="p.default" class="input prop-default" placeholder="默认值(可选)" />
              <button class="btn-sm btn-delete" @click="removeProp(pi)">✕</button>
            </div>
            <button class="btn btn-text" @click="addProp">+ 添加属性</button>
          </div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDialog = false">取消</button>
            <button class="btn btn-primary" @click="save">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.editor-section {
  padding: 16px;
}
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.editor-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}
</style>
```

- [ ] **Step 3: Create VertexDataEditor.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\builder\VertexDataEditor.vue`:

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { VertexData, TagDef } from '../../types/nebula'
import SimpleTable from '../common/SimpleTable.vue'

const props = defineProps<{ items: VertexData[]; tags: TagDef[] }>()
const emit = defineEmits<{ update: [items: VertexData[]] }>()

const showDialog = ref(false)
const editingIdx = ref(-1)
const form = ref<VertexData>({ id: '', vid: '', tagName: '', props: {} })

const columns = [
  { key: 'vid', label: 'VID', width: '120px' },
  { key: 'tagName', label: 'Tag', width: '100px' },
  { key: 'props', label: '属性值' },
]

const selectedTag = computed(() => props.tags.find(t => t.name === form.value.tagName))

function addNew() {
  editingIdx.value = -1
  form.value = { id: crypto.randomUUID(), vid: '', tagName: '', props: {} }
  showDialog.value = true
}
function editRow(row: VertexData) {
  editingIdx.value = props.items.indexOf(row)
  form.value = JSON.parse(JSON.stringify(row))
  showDialog.value = true
}
function confirmDelete(row: VertexData) {
  emit('update', props.items.filter(r => r !== row))
}
function save() {
  if (!form.value.vid.trim() || !form.value.tagName) return
  const next = [...props.items]
  if (editingIdx.value >= 0) next[editingIdx.value] = { ...form.value }
  else next.push({ ...form.value })
  emit('update', next)
  showDialog.value = false
}
</script>

<template>
  <div class="editor-section">
    <div class="editor-header">
      <span class="editor-title">顶点数据 (Vertex)</span>
      <button class="btn btn-primary" @click="addNew">+ 添加 Vertex</button>
    </div>
    <SimpleTable :columns="columns" :rows="items" @edit="editRow" @delete="confirmDelete" />

    <Teleport to="body">
      <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
        <div class="modal-box">
          <h3 class="modal-title">{{ editingIdx >= 0 ? '编辑' : '新增' }} Vertex</h3>
          <div class="form-field">
            <label>VID</label>
            <input v-model="form.vid" class="input" placeholder="顶点 ID" />
          </div>
          <div class="form-field">
            <label>Tag</label>
            <select v-model="form.tagName" class="input">
              <option value="" disabled>选择 Tag</option>
              <option v-for="t in tags" :key="t.name" :value="t.name">{{ t.name }}</option>
            </select>
            <p v-if="tags.length === 0" class="form-hint">请先在 Tag 定义页面创建点类型</p>
          </div>
          <div v-if="selectedTag" class="form-field">
            <label>属性值</label>
            <div v-for="p in selectedTag.props" :key="p.name" class="prop-row">
              <span class="prop-label">{{ p.name }} ({{ p.type }})</span>
              <input
                v-model="form.props[p.name]"
                class="input"
                :type="p.type === 'int' || p.type === 'float' || p.type === 'double' ? 'number' : p.type === 'bool' ? 'checkbox' : 'text'"
                :placeholder="p.default ?? p.type"
              />
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDialog = false">取消</button>
            <button class="btn btn-primary" @click="save">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.editor-section {
  padding: 16px;
}
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.editor-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}
.prop-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.prop-label {
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 100px;
}
.form-hint {
  font-size: 12px;
  color: var(--warning);
  margin-top: 4px;
}
</style>
```

- [ ] **Step 4: Create EdgeDataEditor.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\builder\EdgeDataEditor.vue` — similar to VertexDataEditor but for edges:

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { EdgeData, EdgeTypeDef } from '../../types/nebula'
import SimpleTable from '../common/SimpleTable.vue'

const props = defineProps<{ items: EdgeData[]; edgeTypes: EdgeTypeDef[] }>()
const emit = defineEmits<{ update: [items: EdgeData[]] }>()

const showDialog = ref(false)
const editingIdx = ref(-1)
const form = ref<EdgeData>({ id: '', edgeType: '', fromVid: '', toVid: '', props: {} })

const columns = [
  { key: 'edgeType', label: '类型', width: '80px' },
  { key: 'fromVid', label: 'From', width: '100px' },
  { key: 'toVid', label: 'To', width: '100px' },
  { key: 'rank', label: 'Rank', width: '60px' },
  { key: 'props', label: '属性值' },
]

const selectedEdgeType = computed(() => props.edgeTypes.find(e => e.name === form.value.edgeType))

function addNew() {
  editingIdx.value = -1
  form.value = { id: crypto.randomUUID(), edgeType: '', fromVid: '', toVid: '', props: {} }
  showDialog.value = true
}
function editRow(row: EdgeData) {
  editingIdx.value = props.items.indexOf(row)
  form.value = JSON.parse(JSON.stringify(row))
  showDialog.value = true
}
function confirmDelete(row: EdgeData) {
  emit('update', props.items.filter(r => r !== row))
}
function save() {
  if (!form.value.edgeType || !form.value.fromVid || !form.value.toVid) return
  const next = [...props.items]
  if (editingIdx.value >= 0) next[editingIdx.value] = { ...form.value }
  else next.push({ ...form.value })
  emit('update', next)
  showDialog.value = false
}
</script>

<template>
  <div class="editor-section">
    <div class="editor-header">
      <span class="editor-title">边数据 (Edge)</span>
      <button class="btn btn-primary" @click="addNew">+ 添加 Edge</button>
    </div>
    <SimpleTable :columns="columns" :rows="items" @edit="editRow" @delete="confirmDelete" />

    <Teleport to="body">
      <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
        <div class="modal-box">
          <h3 class="modal-title">{{ editingIdx >= 0 ? '编辑' : '新增' }} Edge</h3>
          <div class="form-row">
            <div class="form-field flex-1">
              <label>Edge 类型</label>
              <select v-model="form.edgeType" class="input">
                <option value="" disabled>选择类型</option>
                <option v-for="e in edgeTypes" :key="e.name" :value="e.name">{{ e.name }}</option>
              </select>
            </div>
            <div class="form-field flex-1">
              <label>Rank (可选)</label>
              <input v-model="form.rank" class="input" type="number" placeholder="0" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-field flex-1">
              <label>From VID</label>
              <input v-model="form.fromVid" class="input" placeholder="起始点 ID" />
            </div>
            <div class="form-field flex-1">
              <label>To VID</label>
              <input v-model="form.toVid" class="input" placeholder="目标点 ID" />
            </div>
          </div>
          <div v-if="selectedEdgeType" class="form-field">
            <label>属性值</label>
            <div v-for="p in selectedEdgeType.props" :key="p.name" class="prop-row">
              <span class="prop-label">{{ p.name }} ({{ p.type }})</span>
              <input
                v-model="form.props[p.name]"
                class="input"
                :type="p.type === 'int' || p.type === 'float' || p.type === 'double' ? 'number' : p.type === 'bool' ? 'checkbox' : 'text'"
                :placeholder="p.default ?? p.type"
              />
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDialog = false">取消</button>
            <button class="btn btn-primary" @click="save">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.editor-section {
  padding: 16px;
}
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.editor-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}
.form-row {
  display: flex;
  gap: 12px;
}
.flex-1 { flex: 1; }
.prop-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.prop-label {
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 100px;
}
</style>
```

- [ ] **Step 5: Create ScriptPreview.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\builder\ScriptPreview.vue`:

```vue
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
```

- [ ] **Step 6: Add global button styles to theme.css**

Add to the end of `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\styles\theme.css`:

```css
/* === Shared Button Styles === */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.15s, border-color 0.15s, opacity 0.15s;
  background: transparent;
  color: var(--text-primary);
}
.btn:hover { opacity: 0.85; }
.btn-primary {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.btn-primary:hover { background: var(--accent-hover); }
.btn-secondary { border-color: var(--border); color: var(--text-secondary); }
.btn-secondary:hover { background: var(--bg-hover); color: var(--text-primary); }
.btn-danger {
  background: var(--danger);
  border-color: var(--danger);
  color: #fff;
}
.btn-text {
  border: none;
  color: var(--accent);
  padding: 4px 0;
  font-size: 12px;
}

/* === Shared Form Styles === */
.input {
  width: 100%;
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}
.input:focus { border-color: var(--accent); }
select.input { cursor: pointer; }
input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
}

/* === Modal === */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  min-width: 480px;
  max-width: 640px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow);
}
.modal-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}
.form-field {
  margin-bottom: 14px;
}
.form-field label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.prop-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.prop-name { flex: 2; }
.prop-type { flex: 1.5; }
.prop-default { flex: 1.5; }
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 20px;
}
```

- [ ] **Step 7: Commit**

```bash
git add nebula-tools/
git commit -m "feat(nebula-tools): add Builder tab editor components and ScriptPreview"
```

---

### Task 8: Builder.vue Main Page

**Files:**
- Create: `nebula-tools/src/pages/Builder.vue`

**Interfaces:**
- Consumes: all 4 editor components, ScriptPreview, `useNebulaGenerator`, `usePersistState`
- Produces: The full Builder page wired together

- [ ] **Step 1: Create Builder.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\pages\Builder.vue`:

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { TagDef, EdgeTypeDef, VertexData, EdgeData } from '../types/nebula'
import { usePersistState } from '../composables/usePersistState'
import { useNebulaGenerator } from '../composables/useNebulaGenerator'
import TagDefEditor from '../components/builder/TagDefEditor.vue'
import EdgeDefEditor from '../components/builder/EdgeDefEditor.vue'
import VertexDataEditor from '../components/builder/VertexDataEditor.vue'
import EdgeDataEditor from '../components/builder/EdgeDataEditor.vue'
import ScriptPreview from '../components/builder/ScriptPreview.vue'

const route = useRoute()
const router = useRouter()
const { generate } = useNebulaGenerator()

const activeTab = computed(() => (route.query.tab as string) || 'tag')

function setTab(tab: string) {
  router.replace({ query: { ...route.query, tab } })
}

const spaceName = usePersistState('nebula-tools:space', '')
const tags = usePersistState<TagDef[]>('nebula-tools:tags', [])
const edgeTypes = usePersistState<EdgeTypeDef[]>('nebula-tools:edgeTypes', [])
const vertices = usePersistState<VertexData[]>('nebula-tools:vertices', [])
const edges = usePersistState<EdgeData[]>('nebula-tools:edges', [])

const script = computed(() => generate(tags.value, edgeTypes.value, vertices.value, edges.value, spaceName.value || undefined))

const tabs = [
  { key: 'tag', label: '🏷️ Tag 定义' },
  { key: 'edge', label: '🔗 Edge 定义' },
  { key: 'vertex', label: '📦 Vertex 数据' },
  { key: 'edgeData', label: '🔀 Edge 数据' },
]

function clearAll() {
  if (!confirm('确认清空所有数据？此操作不可恢复。')) return
  tags.value = []
  edgeTypes.value = []
  vertices.value = []
  edges.value = []
  spaceName.value = ''
}
</script>

<template>
  <div class="builder-layout">
    <div class="builder-top">
      <div class="tab-bar">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="setTab(tab.key)"
        >
          {{ tab.label }}
        </button>
        <div class="tab-spacer" />
        <div class="tab-extra">
          <input v-model="spaceName" class="input space-input" placeholder="Space 名称(可选)" />
          <button class="btn btn-danger btn-sm" @click="clearAll">清空</button>
        </div>
      </div>

      <div class="tab-content">
        <TagDefEditor v-if="activeTab === 'tag'" :items="tags" @update="tags = $event" />
        <EdgeDefEditor v-if="activeTab === 'edge'" :items="edgeTypes" @update="edgeTypes = $event" />
        <VertexDataEditor v-if="activeTab === 'vertex'" :items="vertices" :tags="tags" @update="vertices = $event" />
        <EdgeDataEditor v-if="activeTab === 'edgeData'" :items="edges" :edgeTypes="edgeTypes" @update="edges = $event" />
      </div>
    </div>

    <div class="builder-bottom">
      <ScriptPreview :script="script" />
    </div>
  </div>
</template>

<style scoped>
.builder-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.builder-top {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.tab-bar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 0 8px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.tab-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.tab-btn:hover { color: var(--text-primary); }
.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
.tab-spacer { flex: 1; }
.tab-extra {
  display: flex;
  align-items: center;
  gap: 8px;
}
.space-input {
  width: 160px;
  font-size: 12px;
  padding: 4px 8px;
}
.tab-content {
  flex: 1;
  overflow-y: auto;
}
.builder-bottom {
  height: 40%;
  min-height: 180px;
  flex-shrink: 0;
}
</style>
```

- [ ] **Step 2: Verify in browser**

Navigate to `/nebula-tools/builder` — verify:
- TAB switching works between Tag/Edge/Vertex/Edge Data sections
- Adding/editing/deleting Tag definitions works
- Adding/editing/deleting Edge definitions works
- Vertex Data tab detects available Tags and renders dynamic property fields
- Edge Data tab detects available Edge types and renders dynamic property fields
- Script preview auto-updates with valid nGQL output
- Space name input appears in generated script
- Copy and Download buttons work
- Page refresh restores data from localStorage

- [ ] **Step 3: Commit**

```bash
git add nebula-tools/
git commit -m "feat(nebula-tools): add Builder page with full form-to-nGQL flow"
```

---

### Task 9: Visualizer Page — NGqlEditor + useNebulaParser Composable

**Files:**
- Create: `nebula-tools/src/composables/useNebulaParser.ts`
- Create: `nebula-tools/src/components/visualizer/NGqlEditor.vue`
- Create: `nebula-tools/src/components/visualizer/GraphCanvas.vue`
- Create: `nebula-tools/src/components/visualizer/FloatingInfoCard.vue`
- Create: `nebula-tools/src/components/visualizer/GraphToolbar.vue`
- Create: `nebula-tools/src/pages/Visualizer.vue`

**Interfaces:**
- Consumes: `parseNGql`, `generateColorMap` from parser; types from `types/nebula.ts`
- Produces: The full Visualizer page

- [ ] **Step 1: Create useNebulaParser.ts**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\composables\useNebulaParser.ts`:

```typescript
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
```

- [ ] **Step 2: Create NGqlEditor.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\visualizer\NGqlEditor.vue`:

```vue
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

    // Keywords
    if (stream.match(/^(CREATE|TAG|EDGE|VERTEX|INSERT|VALUES|SPACE|USE|IF|NOT|EXISTS|ALTER|DROP|INDEX|SHOW|DESCRIBE|DELETE|UPDATE|YIELD|GO|FETCH|LOOKUP|SET|FROM|WHERE|ORDER\s+BY|LIMIT|GROUP\s+BY|UNION|INTERSECT|MINUS)\b/i)) {
      return 'keyword'
    }

    // Types
    if (stream.match(/^(string|int|float|double|bool|date|timestamp)\b/i)) {
      return 'typeName'
    }

    // Strings
    if (stream.match(/^"([^"]*)"/)) return 'string'
    if (stream.match(/^'([^']*)'/)) return 'string'

    // Numbers
    if (stream.match(/^\d+(\.\d+)?/)) return 'number'

    // Comments
    if (stream.match(/^--.*/)) return 'comment'

    // Arrow
    if (stream.match(/^->/)) return 'arrow'

    // Skip one character
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
  /* CodeMirror takes full height */
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
/* Custom nGQL syntax colors */
.editor-body :deep(.ͼ1 .cm-keyword) { color: #c678dd; font-weight: 600; }
.editor-body :deep(.ͼ1 .cm-typeName) { color: #61afef; }
.editor-body :deep(.ͼ1 .cm-string) { color: #98c379; }
.editor-body :deep(.ͼ1 .cm-number) { color: #d19a66; }
.editor-body :deep(.ͼ1 .cm-comment) { color: #5c6370; font-style: italic; }
</style>
```

- [ ] **Step 3: Create GraphCanvas.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\visualizer\GraphCanvas.vue`:

```vue
<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, shallowRef } from 'vue'
import type { ParsedGraph, TagColor, VertexData, EdgeData } from '../../types/nebula'
import type { TagDef, EdgeTypeDef } from '../../types/nebula'

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
  if (!window.vis || !props.parsed) return null

  const { tags, edgeTypes, vertices, edges } = props.parsed

  // Build nodes for each vertex
  const nodes = vertices.map(v => {
    const color = colorForTag(v.tagName)
    const propStr = Object.entries(v.props).map(([k, val]) => `${k}=${val}`).join(', ')
    return {
      id: v.vid,
      label: `${v.vid} (${v.tagName})`,
      title: `${v.vid}<br/>Tag: ${v.tagName}<br/>${Object.entries(v.props).map(([k, val]) => `${k}: ${val}`).join('<br/>')}`,
      color: { background: color, border: '#ffffff' },
      size: 20,
      shape: 'dot',
      borderWidth: 1.5,
      tagName: v.tagName,
      props: v.props,
    }
  })

  // Build edges
  const visEdges = edges.map((e, i) => ({
    id: `e_${i}`,
    from: e.fromVid,
    to: e.toVid,
    label: e.edgeType,
    title: `${e.edgeType}<br/>From: ${e.fromVid} → ${e.toVid}${e.rank !== undefined ? `<br/>Rank: ${e.rank}` : ''}`,
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
  if (!containerRef.value || !window.vis) return

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
    network.setData({ nodes: new window.vis.DataSet(nodes), edges: new window.vis.DataSet(edges) })
    network.setOptions(options)
    network.fit({ animation: true })
  } else {
    network = new window.vis.Network(
      containerRef.value,
      { nodes: new window.vis.DataSet(nodes), edges: new window.vis.DataSet(edges) },
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

    // Track hover for cursor
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

defineExpose({
  focusNode(id: string) {
    if (network) {
      network.focus(id, { scale: 1.4, animation: true })
      network.selectNodes([id])
    }
  },
  fit() {
    if (network) network.fit({ animation: true })
  },
  togglePhysics(on: boolean) {
    if (network) network.setOptions({ physics: { enabled: on } })
  },
})
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
```

- [ ] **Step 4: Create FloatingInfoCard.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\visualizer\FloatingInfoCard.vue`:

```vue
<script setup lang="ts">
defineProps<{
  visible: boolean
  x: number
  y: number
  vid: string
  tagName: string
  props: Record<string, string>
  neighbors: string[]
}>()

const emit = defineEmits<{
  close: []
  focusNeighbor: [vid: string]
}>()
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="info-card"
      :style="{ left: x + 'px', top: y + 'px' }"
    >
      <div class="card-head">
        <span class="card-tag" :style="{ background: 'var(--accent)' }">{{ tagName }}</span>
        <span class="card-vid">{{ vid }}</span>
        <button class="card-close" @click="emit('close')">✕</button>
      </div>

      <div class="card-body">
        <div class="section-title">属性</div>
        <div v-for="(val, key) in props" :key="key" class="prop-line">
          <span class="prop-key">{{ key }}</span>
          <span class="prop-val">{{ val }}</span>
        </div>
        <div v-if="Object.keys(props).length === 0" class="empty">无属性</div>

        <div v-if="neighbors.length > 0" class="neighbors-section">
          <div class="section-title">关联 ({{ neighbors.length }})</div>
          <div
            v-for="nid in neighbors.slice(0, 20)"
            :key="nid"
            class="neighbor-link"
            @click="emit('focusNeighbor', nid)"
          >
            {{ nid }}
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.info-card {
  position: fixed;
  z-index: 100;
  min-width: 240px;
  max-width: 340px;
  background: var(--bg-float);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  font-size: 13px;
  transform: translate(10px, -50%);
  overflow: hidden;
}
.card-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
}
.card-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  color: #fff;
  font-weight: 500;
}
.card-vid {
  flex: 1;
  font-weight: 600;
  font-family: var(--font-mono);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  padding: 2px;
  line-height: 1;
}
.card-close:hover { color: var(--text-primary); }
.card-body {
  padding: 10px 12px;
  max-height: 300px;
  overflow-y: auto;
}
.section-title {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 8px 0 4px;
}
.section-title:first-child { margin-top: 0; }
.prop-line {
  display: flex;
  gap: 6px;
  padding: 2px 0;
  font-size: 12px;
}
.prop-key { color: var(--text-secondary); min-width: 60px; }
.prop-val { color: var(--text-primary); font-family: var(--font-mono); font-size: 11px; }
.empty { color: var(--text-muted); font-style: italic; font-size: 12px; }
.neighbors-section { margin-top: 4px; }
.neighbor-link {
  padding: 3px 6px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--accent);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.neighbor-link:hover { background: var(--bg-hover); }
</style>
```

- [ ] **Step 5: Create GraphToolbar.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\components\visualizer\GraphToolbar.vue`:

```vue
<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  search: [query: string]
  zoomIn: []
  zoomOut: []
  resetView: []
  screenshot: []
  togglePhysics: [on: boolean]
}>()

const physicsOn = ref(false)
const searchQuery = ref('')

function onSearch() {
  emit('search', searchQuery.value)
}
</script>

<template>
  <div class="toolbar">
    <div class="toolbar-group">
      <input
        v-model="searchQuery"
        class="search-input"
        placeholder="搜索节点..."
        @input="onSearch"
      />
    </div>
    <div class="toolbar-group">
      <button class="tb-btn" title="放大" @click="emit('zoomIn')">＋</button>
      <button class="tb-btn" title="缩小" @click="emit('zoomOut')">−</button>
      <button class="tb-btn" title="重置视角" @click="emit('resetView')">⟲</button>
    </div>
    <div class="toolbar-group">
      <button class="tb-btn" title="截图" @click="emit('screenshot')">📷</button>
      <button
        class="tb-btn"
        :class="{ active: physicsOn }"
        title="物理引擎"
        @click="physicsOn = !physicsOn; emit('togglePhysics', physicsOn)"
      >⚡</button>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}
.toolbar-group {
  display: flex;
  align-items: center;
  gap: 4px;
}
.toolbar-group + .toolbar-group {
  padding-left: 8px;
  border-left: 1px solid var(--border);
}
.search-input {
  width: 140px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
}
.search-input:focus {
  border-color: var(--accent);
}
.tb-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 15px;
  transition: background 0.15s, color 0.15s;
}
.tb-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.tb-btn.active {
  background: var(--accent);
  color: #fff;
}
</style>
```

- [ ] **Step 6: Create Visualizer.vue**

Create `D:\develop\claudecode-workspace\claude_5\nebula-tools\src\pages\Visualizer.vue`:

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useNebulaParser } from '../composables/useNebulaParser'
import NGqlEditor from '../components/visualizer/NGqlEditor.vue'
import GraphCanvas from '../components/visualizer/GraphCanvas.vue'
import FloatingInfoCard from '../components/visualizer/FloatingInfoCard.vue'
import GraphToolbar from '../components/visualizer/GraphToolbar.vue'
import type { TagDef, EdgeTypeDef, VertexData, EdgeData } from '../types/nebula'

const nGqlInput = ref(`-- Nebula Graph 示例
CREATE TAG IF NOT EXISTS person(name string, age int, city string);
CREATE TAG IF NOT EXISTS movie(title string, year int);

CREATE EDGE IF NOT EXISTS knows(weight int);
CREATE EDGE IF NOT EXISTS likes(rating float);

INSERT VERTEX person(name, age, city) VALUES "p1": ("张三", 30, "北京");
INSERT VERTEX person(name, age, city) VALUES "p2": ("李四", 25, "上海");
INSERT VERTEX person(name, age, city) VALUES "p3": ("王五", 35, "深圳");
INSERT VERTEX movie(title, year) VALUES "m1": ("流浪地球", 2019);
INSERT VERTEX movie(title, year) VALUES "m2": ("哪吒", 2020);

INSERT EDGE knows(weight) VALUES "p1" -> "p2": (5);
INSERT EDGE knows(weight) VALUES "p2" -> "p3": (3);
INSERT EDGE likes(rating) VALUES "p1" -> "m1": (4.5);
INSERT EDGE likes(rating) VALUES "p2" -> "m2": (4.0);
INSERT EDGE likes(rating) VALUES "p3" -> "m1": (3.8);
`)

const { parsed, tagColors, edgeColors, error, summary } = useNebulaParser({ value: nGqlInput })

// Editor panel width (default 40%)
const editorWidth = ref(40)
const editorVisible = ref(true)
let dragStart = 0
let dragBase = 0

function onResizeStart(e: MouseEvent) {
  dragStart = e.clientX
  dragBase = editorWidth.value
  document.addEventListener('mousemove', onResizeMove)
  document.addEventListener('mouseup', onResizeEnd)
}
function onResizeMove(e: MouseEvent) {
  const total = window.innerWidth
  const delta = ((e.clientX - dragStart) / total) * 100
  editorWidth.value = Math.max(15, Math.min(70, dragBase + delta))
}
function onResizeEnd() {
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeEnd)
}

// Floating info card
const cardVisible = ref(false)
const cardPos = ref({ x: 0, y: 0 })
const selectedNode = ref({ vid: '', tagName: '', props: {} as Record<string, string>, neighbors: [] as string[] })

function onNodeClick(data: { id: string; vid: string; tagName: string; props: Record<string, string>; neighbors: string[] }) {
  selectedNode.value = data
  cardPos.value = { x: window.innerWidth - 360, y: Math.min(data.neighbors.length * 24 + 80, window.innerHeight - 100) }
  cardVisible.value = true
}

function onBackgroundClick() {
  cardVisible.value = false
}

// Graph canvas ref
const graphRef = ref<InstanceType<typeof GraphCanvas>>()

function handleSearch(query: string) {
  if (!query.trim() || !graphRef.value) return
  graphRef.value.focusNode(query.trim())
}
</script>

<template>
  <div class="visualizer-layout">
    <!-- Left: nGQL Editor -->
    <div v-if="editorVisible" class="editor-panel" :style="{ width: editorWidth + '%' }">
      <NGqlEditor
        v-model="nGqlInput"
        :summary="summary"
        :error="error"
      />
    </div>

    <!-- Resize handle -->
    <div v-if="editorVisible" class="resize-handle" @mousedown="onResizeStart" />

    <!-- Right: Graph + Toolbar -->
    <div class="graph-area">
      <GraphCanvas
        ref="graphRef"
        :parsed="parsed"
        :tag-colors="tagColors"
        :edge-colors="edgeColors"
        @node-click="onNodeClick"
        @background-click="onBackgroundClick"
      />

      <!-- Floating Toolbar -->
      <div class="toolbar-float">
        <GraphToolbar
          @search="handleSearch"
          @zoom-in="graphRef?.focusNode"
          @zoom-out=""
          @reset-view="graphRef?.fit()"
          @toggle-physics="(on: boolean) => graphRef?.togglePhysics(on)"
        />
      </div>

      <!-- Editor toggle pill -->
      <button class="toggle-editor" @click="editorVisible = !editorVisible" :title="editorVisible ? '收起编辑器' : '展开编辑器'">
        {{ editorVisible ? '◀' : '▶' }}
      </button>
    </div>

    <!-- Floating Info Card -->
    <FloatingInfoCard
      :visible="cardVisible"
      :x="cardPos.x"
      :y="cardPos.y"
      :vid="selectedNode.vid"
      :tag-name="selectedNode.tagName"
      :props="selectedNode.props"
      :neighbors="selectedNode.neighbors"
      @close="cardVisible = false"
      @focus-neighbor="(vid) => graphRef?.focusNode(vid); cardVisible = false"
    />
  </div>
</template>

<style scoped>
.visualizer-layout {
  display: flex;
  height: 100%;
  position: relative;
}
.editor-panel {
  flex-shrink: 0;
  overflow: hidden;
}
.resize-handle {
  width: 4px;
  cursor: col-resize;
  background: transparent;
  flex-shrink: 0;
  z-index: 5;
  transition: background 0.15s;
}
.resize-handle:hover {
  background: var(--accent);
}
.graph-area {
  flex: 1;
  position: relative;
  overflow: hidden;
}
.toolbar-float {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
}
.toggle-editor {
  position: absolute;
  top: 12px;
  left: 8px;
  z-index: 10;
  width: 24px;
  height: 24px;
  background: rgba(26, 26, 46, 0.8);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.toggle-editor:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>
```

- [ ] **Step 2: Verify in browser**

Navigate to `/nebula-tools/visualize` — verify:
- Editor panel shows default nGQL script with syntax highlighting
- Graph renders: 5 vertices (p1, p2, p3, m1, m2) and 5 edges, color-coded by tag/edge type
- Clicking a node shows FloatingInfoCard with properties and neighbors
- Clicking a neighbor in the card focuses that node
- Search input filters/highlights nodes
- Zoom + / − / Reset View work
- Dragging the resize handle adjusts editor/graph split
- Toggling editor panel hides/shows it
- Physics toggle stops/starts animation
- Clicking background dismisses the card

- [ ] **Step 3: Commit**

```bash
git add nebula-tools/
git commit -m "feat(nebula-tools): add Visualizer page with nGQL editor and graph canvas"
```

---

### Self-Review Checklist

1. **Spec coverage** — Skim spec section by section:
   - ✅ Project structure — Task 1 scaffold matches spec exactly
   - ✅ Router with `/visualize` `/builder` `/` — Task 3
   - ✅ CodeMirror 6 with nGQL highlighting — Task 9 (NGqlEditor.vue)
   - ✅ vis-network with forceAtlas2Based — Task 9 (GraphCanvas.vue)
   - ✅ FloatingInfoCard with backdrop blur — Task 9
   - ✅ GraphToolbar with search/zoom/screenshot/physics — Task 9
   - ✅ nGQL Parser with regex — Task 4 (nGqlParser.ts)
   - ✅ Four Builder Tab editors — Task 7
   - ✅ Dynamic form for Vertex/Edge properties — Task 7 (VertexDataEditor, EdgeDataEditor)
   - ✅ useNebulaGenerator — Task 5
   - ✅ usePersistState — Task 5
   - ✅ Dark theme CSS — Task 2
   - ✅ SimpleTable/ConfirmDialog — Task 6

2. **Placeholder scan** — No "TBD", "TODO", or "implement later" in this plan

3. **Type consistency** — Cross-checked type names (`TagDef`, `EdgeTypeDef`, `VertexData`, `EdgeData`, `ParsedGraph`, `TagColor`) across all tasks — consistent

4. **Scope check** — This is a single well-scoped project (nebula-tools), no decomposition needed
