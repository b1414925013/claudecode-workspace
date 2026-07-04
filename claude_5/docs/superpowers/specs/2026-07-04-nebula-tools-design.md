# Nebula Tools — nGQL 可视化与 GUI 构建器

**日期**: 2026-07-04
**项目**: nebula-tools
**状态**: Approved

## 概述

为 Nebula Graph 开发两个相互配合的 Vue 3 工具页面：
1. **Visualizer**: 输入 nGQL 脚本 → 解析并渲染为 vis-network 图可视化，支持全屏交互与节点信息查看
2. **Builder**: GUI 表单定义点/边类型和数据 → 自动生成标准 nGQL 脚本

## 技术选型

| 维度 | 选择 | 理由 |
|------|------|------|
| 框架 | Vue 3 + Vite + TypeScript | 成熟、轻量 |
| 路由 | vue-router | `/visualize` / `/builder` / 首页 |
| 代码编辑器 | CodeMirror 6 | 轻量（~80KB），自定义 nGQL 语法高亮 |
| 图可视化 | vis-network v9 | 与现有 graphify-out 一致 |
| nGQL 解析 | 手写正则引擎 | Nebula DDL/DML 语法规整，无需 Parser Generator |
| 状态管理 | Vue 3 composables + localStorage | 两页面无复杂共享状态 |
| UI 框架 | 自实现 CSS | 保持暗色风格统一，零额外依赖 |
| 构建工具 | Vite | 与项目现有工具链一致 |

## 项目结构

```
nebula-tools/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/index.ts
│   │
│   ├── pages/
│   │   ├── Home.vue              # 首页：两个工具卡片入口
│   │   ├── Visualizer.vue        # nGQL → 图可视化
│   │   └── Builder.vue           # GUI → nGQL 生成
│   │
│   ├── components/
│   │   ├── layout/NavBar.vue     # 顶栏导航
│   │   ├── visualizer/
│   │   │   ├── NGqlEditor.vue    # CodeMirror 6 编辑器（左面板）
│   │   │   ├── GraphCanvas.vue   # vis-network 渲染区域
│   │   │   ├── FloatingInfoCard.vue  # 点击节点弹出信息卡片
│   │   │   └── GraphToolbar.vue  # 浮动工具栏（搜索/缩放/截图）
│   │   ├── builder/
│   │   │   ├── TabBar.vue        # 四个 TAB 切换栏
│   │   │   ├── TagDefEditor.vue  # TAG 定义表格表单
│   │   │   ├── EdgeDefEditor.vue # EDGE 定义表格表单
│   │   │   ├── VertexDataEditor.vue  # VERTEX 数据表（动态表单联动）
│   │   │   ├── EdgeDataEditor.vue    # EDGE 数据表（动态表单联动）
│   │   │   └── ScriptPreview.vue # nGQL 脚本实时预览
│   │   └── common/
│   │       ├── SimpleTable.vue   # 通用可编辑表格组件
│   │       └── ConfirmDialog.vue # 确认对话框
│   │
│   ├── composables/
│   │   ├── useNebulaParser.ts    # nGQL → 图数据结构
│   │   ├── useNebulaGenerator.ts # 表单 → nGQL 脚本
│   │   └── usePersistState.ts    # localStorage 持久化
│   │
│   ├── parser/
│   │   ├── nGqlParser.ts         # 正则解析引擎入口
│   │   └── nebulaRules.ts        # Nebula 语法正则规则集
│   │
│   ├── types/
│   │   └── nebula.ts             # 共享类型定义
│   │
│   └── styles/
│       ├── theme.css             # CSS 变量 + 全局暗色主题
│       └── highlight.css         # CodeMirror nGQL 语法高亮
```

## 数据模型

### 核心类型

```typescript
// 点类型定义
interface TagDef {
  id: string;           // uuid
  name: string;         // 如 person
  props: PropDef[];     // 属性列表
}

// 边类型定义
interface EdgeTypeDef {
  id: string;
  name: string;         // 如 knows
  props: PropDef[];
}

// 属性定义
interface PropDef {
  name: string;
  type: 'string' | 'int' | 'float' | 'bool' | 'date' | 'double';
  default?: string;      // 默认值（可选）
}

// 点数据
interface VertexData {
  id: string;
  vid: string;          // Vertex ID
  tagName: string;      // 关联的 Tag 名
  props: Record<string, string>;
}

// 边数据
interface EdgeData {
  id: string;
  edgeType: string;      // 边类型名
  fromVid: string;
  toVid: string;
  rank?: number;
  props: Record<string, string>;
}

// 解析结果（nGQL → graph）
interface ParsedGraph {
  tags: TagDef[];
  edgeTypes: EdgeTypeDef[];
  vertices: VertexData[];
  edges: EdgeData[];
}
```

## 页面 1: nGQL 可视化 (Visualizer)

### 布局

全屏容器，两层叠加：
- **底层**: GraphCanvas — 全屏 vis-network 渲染（占满窗口）
- **浮动层**: NGqlEditor 可折叠左面板（侧滑抽屉） + 浮动工具栏（右上角） + FloatingInfoCard

### 编辑器区 (NGqlEditor)

- CodeMirror 6 实例，自定义 nGQL 语法高亮（高亮关键字：`CREATE`, `TAG`, `EDGE`, `VERTEX`, `INSERT`, `SPACE`, `IF NOT EXISTS` 等）
- 初始位置为左侧 40% 宽度面板，可拖拽边框调整宽度
- 右上角 Pin 按钮切换固定/折叠
- 输入即解析（300ms debounce），底部显示解析状态：
  - 成功时: 「✓ 解析成功 — 3 个 TAG, 5 个 VERTEX, 2 个 EDGE」
  - 失败时: 「✗ 解析错误: 第 5 行，无法解析 ...」
- 提供「Generate Graph」手动触发按钮作为 fallback

### 全屏画布 (GraphCanvas)

- 基于 vis-network `fit()` 自适应全屏
- 物理引擎：`forceAtlas2Based`，与 graphify-out 参数一致
  - gravitationalConstant: -60, centralGravity: 0.005, springLength: 120
  - 稳定后禁用物理引擎
- 节点映射：
  - Vertex 实例 → vis node，颜色按其 Tag 类型分组
  - Edge 实例 → vis edge，不同 edgeType 不同颜色（虚线/实线区分）
  - Tag 类型没有独立节点，Vertex 聚集显示时自动按 Tag 名聚类
- 交互：滚轮缩放、拖拽平移、悬停高亮、点击选中

### 浮动工具栏 (GraphToolbar)

右上角半透明浮动条（`background: rgba(15,15,26,0.8); backdrop-filter: blur(8px)`）：

```
[🔍 搜索...] [−] [+] [⟲] [📷] [⚡]
```

- 搜索输入框 —— 实时在当前节点中检索并聚焦
- 放大/缩小/重置视角（reset `fit()`）
- 截图导出（html2canvas 或 Canvas toDataURL）
- 物理引擎开关（稳定后可手动启用/禁用）

### 信息卡片 (FloatingInfoCard)

点击节点时在点击位置附近弹出（跟随节点位置或鼠标坐标）：

- **标题**: 节点标识 + Tag 图标颜色
- **类型**: Vertex / Edge Type
- **属性**: 逐行列出的键值对
- **关联边** (仅 Vertex 被点击时)：列出相邻的边（分类显示入边/出边）
- **操作按钮**: [聚焦] [关闭]

卡片样式：半透明暗色背景，圆角，`backdrop-filter: blur(12px)`，无边框干净卡片。

### nGQL 解析引擎

**Step 1 — 结构提取**（正则匹配 `CREATE TAG` / `CREATE EDGE`）：

```
CREATE TAG person(name string, age int, city string)
→ TagDef { name: "person", props: [{name:"name",type:"string"}, ...] }
```

**Step 2 — 数据提取**（正则匹配 `INSERT VERTEX` / `INSERT EDGE`）：

```
INSERT VERTEX person(name, age) VALUES "p1": ("张三", 30)
→ VertexData { vid: "p1", tagName: "person", props: {name:"张三", age:"30"} }
```

映射规则：
- 按 Tag/Edge 类型分组分配颜色（HSL 色环分配）
- Vertex ID 作为 vis node.id
- Edge 的 fromVid → toVid 映射为 vis edge.from → edge.to
- 悬停 tooltip 显示摘要属性

## 页面 2: GUI 构建器 (Builder)

### 布局

上下分栏结构：
- **上半部**: TAB 切换的四个表单区域（TabBar + 对应表单组件）
- **下半部**: 固定高度的脚本预览区（分隔条可拖拽调整比例，默认 60/40）

### TAB 详情

```
Tab 1: TagDefEditor       — 定义点类型
Tab 2: EdgeDefEditor      — 定义边类型
Tab 3: VertexDataEditor   — 输入点数据
Tab 4: EdgeDataEditor     — 输入边数据
```

TAB 切换栏固定在顶部，使用路由 query 参数 `?tab=tag` 保持状态。

### Tag 定义表单 (TagDefEditor)

| 列名 | 控件 | 说明 |
|------|------|------|
| 标签名 | `<input>` | 必填，字母数字下划线 |
| 属性 | 子表格 | 属性名 + 类型（select: string/int/float/bool/date）+ 默认值（可选）|
| 操作 | 编辑 / 删除 | 表格行 |

- 子表格支持任意数量的属性行
- 每行末尾有删除按钮，表格底部有新增行按钮

### Vertex 数据表单 (VertexDataEditor)

| 列名 | 控件 | 说明 |
|------|------|------|
| VID | `<input>` | 顶点 ID |
| Tag | `<select>` | 从已定义的 Tag 中选择 |
| 属性值 | 动态渲染 | 根据所选 Tag 的 props 自动生成输入行 |
| 操作 | 编辑 / 删除 | |

核心交互：
1. 选择 Tag → 自动展开该 Tag 的所有属性作为输入字段
2. 属性类型映射：string→文本输入, int→数字输入, bool→切换开关, date→日期选择器
3. 如果尚未定义任何 Tag，显示提示「请先在 Tag 定义中创建点类型」

### Edge 数据表单 (EdgeDataEditor)

| 列名 | 控件 | 说明 |
|------|------|------|
| Edge 类型 | `<select>` | 从已定义的 Edge 中选择 |
| From VID | `<input>` | 起始点 |
| To VID | `<input>` | 目标点 |
| Rank | `<input type=number>` | 可选 |
| 属性值 | 动态渲染 | 根据所选 Edge 类型 |
| 操作 | 编辑 / 删除 | |

### 脚本预览 (ScriptPreview)

- CodeMirror 6（只读模式），nGQL 语法高亮
- 每次表单数据变更自动重新生成（500ms debounce）
- 操作栏：[生成脚本] [复制到剪贴板] [下载为 .ngql 文件]

### 生成规则 (useNebulaGenerator)

```nGQL
-- Space（可选）
CREATE SPACE IF NOT EXISTS my_space(partition_num=10, replica_factor=1);
USE my_space;

-- Tag 定义
CREATE TAG IF NOT EXISTS person(name string, age int, city string);
CREATE TAG IF NOT EXISTS movie(title string, year int);

-- Edge 定义
CREATE EDGE IF NOT EXISTS knows(weight int);
CREATE EDGE IF NOT EXISTS likes(rating float);

-- Vertex 数据
INSERT VERTEX person(name, age, city) VALUES "p1": ("张三", 30, "北京");
INSERT VERTEX movie(title, year) VALUES "m1": ("流浪地球", 2019);

-- Edge 数据
INSERT EDGE knows(weight) VALUES "p1" -> "p2": (5);
INSERT EDGE likes(rating) VALUES "p1" -> "m1": (4.5);
```

### 状态持久化

- 使用 `usePersistState` composable，基于 `watch` + `localStorage`
- 自动保存 key: `nebula-tools:builder-state`
- 页面加载时自动恢复
- 提供「清空全部」按钮确认后重置

## 首页 (Home.vue)

简单的入口页，两个卡片：

```
┌──────────────────────────────────┐
│          Nebula Tools             │
│                                  │
│  ┌──────────────┐ ┌────────────┐ │
│  │ 📊 Visualizer │ │ 🏗 Builder │ │
│  │               │ │            │ │
│  │ nGQL → Graph  │ │ GUI → nGQL │ │
│  │ [go]          │ │ [go]        │ │
│  └──────────────┘ └────────────┘ │
└──────────────────────────────────┘
```

## 路由设计

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | Home | 入口 |
| `/visualize` | Visualizer | nGQL 可视化 |
| `/builder` | Builder | GUI 构建器 |
| `/builder?tab=tag` | Builder | 锚定到 Tab |

使用 vue-router history 模式。

## 组件交互细节

### SimpleTable 通用表格组件

可复用的表格组件，用于 builder 中各表单：
- Props: `columns`, `rows`, `editable`
- 支持行内编辑（双击单元格或点击编辑按钮）
- 支持新增行、删除行（确认对话框）
- 变更时 emit `@update`

### ConfirmDialog

确认对话框，用于删除操作确认：
- Props: `title`, `message`, `visible`
- Emit: `@confirm`, `@cancel`

### NavBar

顶栏导航（固定在页面顶部）：
- Logo / 标题: "Nebula Tools"
- 链接: Home / Visualizer / Builder
- 当前页面高亮
- 暗色背景，半透明

## 样式系统 (theme.css)

CSS 变量统一管理：

```css
:root {
  --bg-primary: #0f0f1a;
  --bg-panel: #1a1a2e;
  --bg-float: rgba(26, 26, 46, 0.85);
  --border: #2a2a4e;
  --text-primary: #e0e0e0;
  --text-secondary: #aaa;
  --text-muted: #555;
  --accent: #4E79A7;
  --danger: #e74c3c;
  --success: #2ecc71;
  --radius: 8px;
  --shadow: 0 8px 32px rgba(0,0,0,0.4);
}
```

## 非功能性需求

- **首屏加载**: < 2s（CodeMirror 6 按需加载，vis-network CDN 缓存）
- **输出尺寸**: < 200KB gzipped（不含 vis-network CDN）
- **离线可用**: 纯前端工具，无需后端服务
- **浏览器兼容**: 现代 Chrome / Edge / Firefox

## 未来扩展（当前不实现）

- 导入已有 .ngql 文件
- 图可视化时支持直接拖拽修改布局
- 批量导入 JSON/CSV 格式的点边数据
- 连接 Nebula Graph 实例直接查询/写入
