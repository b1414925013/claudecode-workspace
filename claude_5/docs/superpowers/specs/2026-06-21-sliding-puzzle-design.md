# 数字华容道 (Sliding Puzzle) — 设计文档

## 概述

基于 Vue 3 + Vite + TypeScript 的数字华容道网页游戏，支持数字模式和图片拼图模式。内置 IDA* 自动解算器，多尺寸棋盘、深色模式、游戏状态持久化。

## 技术栈

| 层级 | 技术 |
|------|------|
| 构建工具 | Vite 5 |
| 框架 | Vue 3 (Composition API, `<script setup lang="ts">`) |
| 语言 | TypeScript |
| 样式 | Scoped CSS + CSS 变量 |
| 图片处理 | Canvas API (缩放/切割) |
| 解算算法 | IDA* (Iterative Deepening A*) |
| 存储 | localStorage |
| 包管理 | npm |

## 文件结构

```
sliding-puzzle/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── style.css                      # 全局样式、CSS 变量、深色模式
│   ├── components/
│   │   ├── GameHeader.vue             # 标题、步数、计时器、新游戏
│   │   ├── GameBoard.vue              # n×n 棋盘
│   │   ├── GameTile.vue               # 方块（数字或图片切片）
│   │   ├── GameControls.vue           # 尺寸选择、打乱、模式切换、深色切换
│   │   ├── ImagePicker.vue            # 预设图片选择 + 上传按钮
│   │   └── GameOverlay.vue            # 胜利弹层 + 解算提示
│   ├── composables/
│   │   ├── usePuzzleState.ts          # 响应式游戏状态管理
│   │   ├── usePuzzleLogic.ts          # 核心算法（打乱、移动、胜利判定）
│   │   ├── useSolver.ts              # IDA* 解算器
│   │   └── useStorage.ts             # localStorage 读写 + 降级处理
│   ├── assets/
│   │   └── presets/                   # 预设图片（SVG/Data URL）
│   └── types/
│       └── puzzle.ts                  # 类型定义
```

## 组件设计

### App.vue

根组件，组合所有子组件，调用 `usePuzzleState` 管理全局状态。通过 props 向下传递数据。

### GameHeader.vue

- 游戏标题 "数字华容道" / "Sliding Puzzle"
- 步数计数器（显示 "步数：N"）
- 计时器（格式 `MM:SS`，第一步移动时启动，胜利时停止）
- "新游戏" 按钮（重置当前尺寸和模式）

### GameBoard.vue

- 渲染 n×n 网格（Grid 或绝对定位）
- 每个方块的点击事件 → 触发移动
- 动画期间屏蔽输入（100ms 锁定）
- 监听键盘方向键（可替代点击操作）

### GameTile.vue

数字模式：
- 显示方块数字（如果值 > 0）
- 空格（值 === 0）显示空白背景
- 随数字大小渐变色

图片模式：
- 每个方块用 `background-image` + `background-position` + `background-size` 显示对应图片切片
- 空格透明
- 不使用数字，纯图片

### GameControls.vue

- 棋盘尺寸下拉选择器（3×3 / 4×4 / 5×5）
- "打乱" 按钮（重新随机排列）
- "解算提示" 按钮（触发 IDA* 解算）
- 数字/图片模式切换开关
- 深色模式切换按钮（🌙/☀️）

### ImagePicker.vue

- 预设图片列表（3-5 张，缩略图展示）
- "上传图片" 按钮（`<input type="file">`）
- 上传后显示预览
- 点击预设或上传的图片 → 切换到图片模式并重置游戏

### GameOverlay.vue

- 胜利弹窗（显示步数、用时 + "再来一局" 按钮）
- 解算提示弹窗（"正在求解中..." / "下一步" / 自动播放）
- 半透明遮罩层

## 核心逻辑

### 类型定义 (`types/puzzle.ts`)

```typescript
export type PuzzleSize = 3 | 4 | 5
export type GameMode = 'number' | 'image'
export type GameStatus = 'playing' | 'won' | 'solving' | 'solved'

export interface PuzzleState {
  board: number[]               // 一维数组，0 = 空格，1~n²-1 = 方块
  size: PuzzleSize
  mode: GameMode
  status: GameStatus
  moves: number
  timer: number                 // 秒
  isRunning: boolean            // 计时器是否在运行
  bestScores: Record<string, BestScoreData>  // key = "3x3", "4x4", "5x5"
  selectedImage: string | null  // 当前图片的 data URL / key
  isDarkMode: boolean
}

export interface BestScoreData {
  moves: number
  time: number
}

export interface Move {
  index: number      // 空格移动到的目标索引
  direction: 'up' | 'down' | 'left' | 'right'  // 方块滑入的方向
}
```

### 游戏逻辑 `usePuzzleLogic.ts`

**打乱算法：**
1. 从完成态开始，执行 n² × 50 次随机合法移动
2. 保证有解（因为始终从完成态反向移动）

**移动逻辑：**
- 点击索引 `i` → 找到空格索引 `empty`
- 检查 `i` 是否与 `empty` 相邻（行差 + 列差 = 1）
- 交换 `board[i]` 与 `board[empty]`
- 返回交换后的新数组

**胜利判定：**
- `board.every((v, i) => v === (i + 1) % (size * size))`

**逆序数验证（备用打乱方法）：**
- 对 3×3 和 4×4：逆序数为偶数时有解
- 对 5×5：需要考虑行数和逆序数的组合

### 解算器 `useSolver.ts`

```
函数 idaStar(board, size):
  预处理: 预计算每个目标位置的曼哈顿距离表
  bound = manhattan(board)
  path = []
  while true:
    result = search(board, 0, bound, path, -1)
    if result == FOUND: return path
    if result == INF: return null
    bound = result

函数 search(board, g, bound, path, lastMove):
  f = g + manhattan(board)
  if f > bound: return f
  if board == goal: return FOUND
  min = INF
  for each direction (跳过 lastMove 的反向):
    newBoard = applyMove(board, dir)
    path.push(direction)
    t = search(newBoard, g+1, bound, path, dir)
    if t == FOUND: return FOUND
    if t < min: min = t
    path.pop()
  return min
```

性能优化：
- 曼哈顿距离查表（预计算）
- 跳过反向移动（避免来回振荡）
- 在 Web Worker 中运行（可选，视复杂度）
- 5×5 设置最大 80 步搜索深度限制

### 游戏状态 `usePuzzleState.ts`

- 响应式 `PuzzleState`
- `initGame(size, mode)` — 初始化
- `handleClick(index)` — 处理点击移动
- `shuffle()` — 重新打乱
- `startSolver()` — 启动解算
- `applySolverStep()` — 应用解算的下一步
- `saveToStorage()` / `loadFromStorage()`

### 存储 `useStorage.ts`

与 2048 同样的模式：try/catch 包裹所有操作，隐私模式静默降级。

键名：
- `'puzzle-game-state'` — 当前游戏进度
- `'puzzle-best-scores'` — 最高分记录
- `'puzzle-dark-mode'` — 深色模式
- `'puzzle-image-data'` — 用户上传的图片数据（base64）

## 视觉设计

### 布局

- 居中卡片式布局，最大宽度 500px
- 标题 + 步数/计时器在顶部并列
- 控制栏在棋盘下方
- 棋盘内方块间距 4px

### 方块样式（数字模式）

| 数字范围 | 背景色 |
|---------|--------|
| 1-5 | #eee4da, #ede0c8, #f2b179, #f59563, #f67c5f |
| 6-10 | #f65e3b, #edcf72, #edcc61, #edc850, #edc53f |
| 11+ | #edc22e |
| 空格 | 透明/灰色背景 |

### 方块样式（图片模式）

- 每个方块：`background-image` 相同，`background-size: (n × cellSize)px (n × cellSize)px`
- `background-position: (-col × cellSize)px (-row × cellSize)px`
- 空格：透明 / 隐藏

### 动画

| 动画 | 时长 | 缓动函数 |
|------|------|---------|
| 方块滑动 | 120ms | ease |
| 新游戏淡入 | 200ms | ease-out |
| 胜利弹层 | 300ms | ease |

### 深色模式

与 2048 同一体系，CSS 变量互换，`.dark` class 控制。

## 响应式

| 屏幕宽度 | 棋盘行为 |
|---------|---------|
| ≥500px | 固定尺寸，居中显示 |
| <500px | 宽度自适应（100% - 2×16px） |

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| localStorage 不可用 | try/catch 捕获，游戏正常运行不保存 |
| 上传非图片文件 | 检查 `file.type`，弹窗提示 |
| 图片过小 | Canvas 缩放后检查尺寸，提示用户 |
| IDA* 超时（5×5） | 5秒超时，返回 null，提示 "无法求解" |
| 解算中切换尺寸 | 终止当前解算（标志位 + 清空路径） |

## 非功能需求

- **性能**：每次移动操作 < 1ms，IDA* 3×3 瞬时，4×4 < 2s，5×5 < 5s
- **兼容性**：Chrome / Firefox / Safari / Edge 最新版本
- **无外部依赖**：不引入第三方 UI 库或游戏库
- **可访问性**：方块使用 `role="button"`，支持 `aria-label`
