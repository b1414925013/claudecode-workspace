# 本地 CI 工具（CI Runner）设计文档

- 日期：2026-09-19
- 状态：待评审
- 目标目录：`D:\develop\claudecode-workspace\claude_5\CI\`

## 1. 背景与目标

公司电脑不允许安装 Jenkins（禁止注册系统服务、禁止需要管理员的安装），但日常开发需要
"改完代码点一下 → 自动跑构建和测试 → 看结果"的闭环，以及定时跑一些周期性任务。

因此需要一个**用户态的、本机运行的轻量 CI 工具**，提供 Jenkins 的核心子集：
多任务管理、流水线步骤、手动/定时触发、实时构建日志、构建历史、完成通知。

### 明确的非目标（YAGNI）

以下功能经确认**不做**，不要为它们预留复杂度：

- 不做 Git 源码管理：任务只绑定一个已存在的本地目录，工具不 clone / fetch / checkout
- 不做构建产物归档
- 不做自动部署 / 发布
- 不做文件变化监听触发
- 不做新提交轮询触发
- 不做多用户、权限、登录、审计（本地单人使用，只监听 `127.0.0.1`）
- 不做分布式 Agent / 主从节点
- 不做插件体系

### 成功标准

1. 双击 `start.bat` 后无需任何其他操作，浏览器自动打开界面
2. 新建一个任务（指定目录 + 若干命令步骤），点击"立即构建"，能在网页上实时看到完整输出
3. 配置 cron 表达式后，到点自动构建
4. 构建结束（成功或失败）能收到 Windows 桌面通知
5. 上述全过程不需要联网、不需要管理员权限、不需要新增 pip 安装

## 2. 运行环境约束

已实测本机（2026-09-19）可用：

| 组件 | 版本 | 用途 |
|---|---|---|
| Python | 3.11.4 | 运行时 |
| FastAPI | 0.109.0 | Web 框架 |
| uvicorn | 0.52.4 | ASGI 服务器 |
| SQLAlchemy | 2.0.25 | ORM |
| APScheduler | 3.10.4 | cron 调度 |
| pytest | 9.1.1 | 测试 |
| Node / npm | 24.15.0 / 11.12.1 | 被 CI 调用的目标工具链 |
| JDK / Maven | 21.0.11 / 3.8.8 | 同上 |

**核心约束：本方案不引入任何新的 pip 依赖**，全部使用上述已安装的包。前端不使用构建工具
（无 npm install），只用浏览器原生能力，因此也**不需要模板引擎**——页面以静态文件形式由
FastAPI 直接托管，Jinja2 虽然已安装但不使用。

## 3. 总体架构

单 Python 进程，内部分为三个协作部分：

```
uvicorn (FastAPI)
├── HTTP / SSE 接口 + 静态页面          处理请求，不阻塞
├── APScheduler 后台线程                到点把构建请求投进队列
└── BuildExecutor（调度循环 + 工作线程）  真正执行构建
        └── 每个构建占 1 个线程
              └── 每个步骤 = 1 个 subprocess
```

三个部分的边界：

- **API 层**只做校验和读写数据库，绝不执行构建，避免请求被长任务卡住
- **调度层**只负责"什么时候投递"，不关心构建怎么跑；触发后立即返回
- **执行层**是唯一会写 `builds.status` 和执行子进程的地方

它们之间通过数据库 + 一个内存队列解耦，不共享可变状态。

## 4. 并发模型

用户明确要求"不同任务可以并行"。

### 规则

| 场景 | 行为 |
|---|---|
| 同一任务正在跑，再次触发 | 进入该任务的 `pending` 队列，返回 202 + 提示"已排队" |
| 同一任务已有 1 个 pending，再次触发 | 拒绝，返回 409，"该任务已有构建在排队" |
| 不同任务同时触发 | 并行执行，受线程池 `max_workers` 限制 |
| 并发额度已满 | 构建状态置为 `queued`，等有构建结束释放额度 |

### 参数

- `max_workers` 默认 **4**，在设置页可改

执行器不预先创建固定大小的线程池，而是用一个**调度循环**：只要
`正在运行数 < max_workers` 且队列非空，就派发下一个构建到新线程。
`max_workers` 每次派发时从设置表读取，所以**改完并发数，下一个被派发的构建就按新额度走，
不需要重启**。已经在跑的构建不受影响，不会被中断。
- 每个任务最多 1 个排队中的构建（防止误点十下堆出十个）

### 为什么不做"全局串行"

本地机器跑 `npm run build` 和 `mvn package` 确实会抢 CPU，但这是用户明确接受的取舍；
每个任务可设置超时来兜底。

## 5. 数据模型

SQLite，库文件 `CI/data/ci.db`，SQLAlchemy 2.0 声明式模型。
SQLite 需开启 WAL 模式，因为调度线程和执行线程会并发写。

### jobs

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int PK | |
| name | str(100) | 唯一，非空 |
| description | str(500) | 可空 |
| workdir | str(500) | 步骤执行的基准目录，必须存在且为目录 |
| cron_expr | str(100) | 可空；为空表示不启用定时 |
| timeout_seconds | int | 单步骤超时，默认 1800 |
| fail_fast | bool | 默认 True；为 False 时步骤失败也继续跑后续步骤 |
| enabled | bool | 默认 True；False 时定时不触发，手动仍可触发 |
| created_at / updated_at | datetime | |

### steps

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int PK | |
| job_id | int FK → jobs.id | 级联删除 |
| order_index | int | 从 0 开始 |
| name | str(100) | 显示名，如"运行 pytest" |
| command | str(4000) | 要执行的命令 |
| shell | str(20) | `cmd` 或 `powershell`，默认 `cmd` |
| continue_on_failure | bool | 默认 False。单步骤级别的"失败继续"，优先于 job.fail_fast |
| env | JSON | 追加的环境变量，可空 |

唯一约束 `(job_id, order_index)`。

### builds

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int PK | 全局唯一 |
| job_id | int FK | |
| build_number | int | **每个任务独立自增**，从 1 开始，符合 Jenkins 习惯。分配时机为事务内 `SELECT MAX(build_number) + 1`，并对该任务行加写锁，避免并发触发时重号 |
| status | str(20) | `queued` / `running` / `success` / `failed` / `aborted` / `timeout` |
| trigger | str(20) | `manual` / `cron` |
| started_at / finished_at | datetime | `started_at` 在真正拿到槽位开跑时填 |
| exit_code | int | 整体退出码；失败时取第一个失败步骤的 code |
| error_message | str(500) | 如"工作目录不存在"这类工具级错误 |

### build_steps

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int PK | |
| build_id | int FK → builds.id | 级联删除 |
| step_id | int FK → steps.id | |
| name | str(100) | **冗余存储**：步骤改名后历史记录仍显示当时的名字 |
| order_index | int | |
| status | str(20) | `pending` / `running` / `success` / `failed` / `skipped` / `timeout` / `aborted` |
| exit_code | int | |
| started_at / finished_at | datetime | 用于算每步耗时 |

`build_steps` 独立成表的原因：控制台要按步骤折叠、要一眼看出挂在第几步、要显示每步耗时。
只存 builds 一张表做不到这些。

### settings

键值表：`max_workers`、`notify_on_success_manual`、`notify_on_success_cron`、`notify_on_failure`。

## 6. 执行引擎

### 一次构建的完整流程

```
POST /api/jobs/{id}/build
  → 校验：任务存在 / 工作目录存在 / 该任务无 pending
  → 建 builds 记录，status=queued，分配 build_number
  → 建 build_steps 记录（全部 pending）
  → 投递到线程池
  → 立即返回 202 + build_id        ← 请求在这里就结束了

工作线程：
  → status=running, started_at=now
  → 逐步骤执行（见下）
  → 汇总 status，finished_at=now
  → 触发桌面通知
  → 广播"构建结束"，关闭该构建的所有 SSE 连接
```

### 单个步骤的执行

1. 在日志流写入分隔头：`────── [3/7] 运行 pytest ──────`
2. 启动子进程（细节见下）
3. 读取子进程输出，同时做两件事：写日志文件 + 广播给 SSE 订阅者
4. 等待退出，记录 `exit_code` 和耗时，更新 `build_steps.status`
5. 判定是否继续：
   - `exit_code == 0` → `success`，继续下一步
   - `exit_code != 0` 且（`continue_on_failure` 或 `job.fail_fast == False`）→ `failed`，**继续跑下一步**
   - `exit_code != 0` 且需要停止 → `failed`，**剩余步骤全部标记 `skipped`**，整个构建 `failed`
   - 超时 → 该步骤 `timeout`，杀进程树，剩余步骤 `skipped`，整个构建 `timeout`
   - 用户点中止 → 当前步 `aborted`，剩余 `skipped`，整个构建 `aborted`

### Windows 特有的三个坑（必须按此实现）

**坑 1：杀进程树必须用 taskkill**

`npm run build` 会派生 node 子进程，只掉 `proc.kill()` 杀不掉孙子进程，会留一堆僵尸占着
CPU 和文件锁。超时和中止必须走：

```
taskkill /F /T /PID <pid>
```

`/T` 是连子孙一起杀，缺了它等于没杀。

**坑 2：中文输出乱码**

中文 Windows 的控制台默认代码页是 GBK (936)，Python 读到的是 GBK 字节，按 utf-8 解码会得到
乱码或抛 `UnicodeDecodeError`。

处理方式：
- 启动子进程时前置 `chcp 65001 > nul &&` 切到 UTF-8 代码页
- 同时设置环境变量 `PYTHONIOENCODING=utf-8`，避免 Python 子进程回退到 GBK
- 解码时统一用 `errors='replace'`，宁可个别字符变问号，也绝不能因为解码异常导致构建流程崩掉

**坑 3：Ctrl+C 传染**

工具在控制台被 Ctrl+C 关闭时，信号会传到同一进程组的子进程，导致正在跑的任务半死不活。
子进程必须以独立进程组启动（`CREATE_NEW_PROCESS_GROUP`），并保证工具退出时统一清理。

### 命令构造

- `shell == "cmd"` → `cmd.exe /c "chcp 65001 > nul && <command>"`
- `shell == "powershell"` → `powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "<command>"`

统一 `cwd = job.workdir`，环境变量 = 当前进程环境 + `step.env`。

### 日志落盘

路径 `CI/logs/<job_id>/<build_number>.log`，UTF-8 编码。
文件首行写入构建元信息（任务名、构建号、触发方式、开始时间、工作目录）。
日志文件是**唯一权威来源**，内存缓冲只是加速；即使工具崩溃重启，历史日志仍可读。

## 7. 实时日志通道

`LogHub` 组件（`ci_runner/loghub.py`），每个正在运行的构建对应一个实例：

- **环形缓冲**：最近 2000 行（防止长构建把内存吃光）
- **订阅者集合**：每个打开的 SSE 连接是一个订阅者，用线程安全的方式增删
- **落盘**：同步追加到日志文件

### 前端取日志的两条路径

1. **增量拉取**：`GET /api/builds/{id}/log?offset=N` → 返回 `{lines: [...], next_offset: M, status: "..."}`
   用于页面加载时补齐历史，以及 SSE 断线后的兜底轮询
2. **实时推送**：`GET /api/builds/{id}/stream` → SSE，事件 `log`（一行）/ `status`（状态变化）/ `end`（结束）

页面打开流程：先拉一次全量 `offset=0` → 记住 `next_offset` → 建立 SSE。
这样即使 SSE 建立慢了，也不会丢日志。

构建结束后 SSE 连接主动发 `end` 事件并关闭，前端切到轮询模式（用于查看历史构建）。

## 8. API 设计

统一前缀 `/api`，全部返回 JSON。错误格式统一 `{"detail": "人类可读的错误信息"}`。

### 任务

```
GET    /api/jobs                    列表，含每个任务最近一次构建的状态摘要
POST   /api/jobs                    新建
GET    /api/jobs/{id}               详情，含步骤列表
PUT    /api/jobs/{id}               整体更新（步骤列表整体替换）
DELETE /api/jobs/{id}               删除（级联删步骤和构建历史）
POST   /api/jobs/{id}/build         手动触发构建 → 202
GET    /api/jobs/{id}/builds        该任务的构建历史（分页）
POST   /api/jobs/{id}/validate-cron  校验 cron 表达式，返回下次 5 次触发时间
```

`PUT` 采用**步骤整体替换**语义而不是逐个步骤增删改：前端提交完整步骤数组，后端删旧插新。
这样一个事务就能完成，也不会出现"步骤顺序错乱"这类并发问题。

`validate-cron` 单独做一个接口，是为了让编辑页能即时提示"这个表达式下次会在什么时候触发"，
不用等保存后才发现写错。

`DELETE` 时若该任务有构建处于 `running` 或 `queued` 状态，返回 409 并提示先中止。
否则删掉任务后，正在跑的子进程会变成没人管的孤儿进程，还会继续占着工作目录。

### 构建

```
GET    /api/builds/{id}             单次构建详情，含每个步骤的状态和耗时
GET    /api/builds/{id}/log         增量取日志（?offset=N）
GET    /api/builds/{id}/stream      实时日志 SSE
POST   /api/builds/{id}/abort       中止
GET    /api/builds/{id}/download    下载完整日志文件
```

`abort` 对两种状态都有效：
- `queued` 的构建 → 直接标记 `aborted` 并移出队列，从头到尾不会启动任何子进程
- `running` 的构建 → 杀进程树，当前步标记 `aborted`，剩余步骤 `skipped`

对已经结束的构建调用 `abort` 返回 409 并说明当前状态。

### 其他

```
GET    /api/queue                   当前正在跑 + 排队的构建
GET    /api/settings                读取设置
PUT    /api/settings                更新设置
GET    /api/health                  健康检查，返回版本号、调度器状态、运行中数量
```

`/api/health` 主要给 `start.bat` 用：启动脚本轮询它来判断服务是否已经就绪，就绪后再打开浏览器。

### 校验规则（后端强制，前端只是提示）

- `name`：非空，≤100 字符，全局唯一
- `workdir`：非空，必须存在且是目录
- `cron_expr`：可空；非空时必须能被 APScheduler 的 `CronTrigger.from_crontab()` 解析
- 步骤：至少 1 个；每个 `command` 非空
- `timeout_seconds`：60 ~ 86400
- `max_workers`：1 ~ 16

## 9. 前端设计

单页应用，三个文件：`web/index.html`、`web/app.js`、`web/style.css`。
**不使用任何前端框架和构建工具**，用原生 JS + `fetch` + `EventSource`。

用原生 JS 而不是 Vue/React 的理由：整个界面就是 5 个视图和十几张表，引入框架意味着要
配 npm 和打包流程，而这个项目的卖点恰恰是"零安装、双击就能跑"。得不偿失。

### 视图

**① 任务列表（首页）**

表格列：名称 / 状态圆点 / 最近构建号 / 结果 / 持续时间 / cron / 操作按钮。
状态圆点颜色：绿=成功、红=失败、黄=运行中（带脉冲动画）、灰=从未构建。
操作列：`[构建] [编辑] [历史] [删除]`。删除需二次确认（输入任务名确认，避免误删）。

**② 任务编辑**

上半部分：名称、描述、工作目录、cron 表达式（带"下次触发时间"即时预览）、超时秒数、失败即停开关、启用开关。
下半部分：**步骤列表**，每行 = 序号 + 名称 + shell 下拉 + 命令输入框 + "失败继续"勾选 + 上移/下移/删除按钮，底部"添加步骤"。

**③ 构建历史**

该任务的所有构建：构建号 / 状态 / 触发方式 / 开始时间 / 时长 / 操作。
点击进入控制台。运行中的构建条目高亮并可点击查看实时输出。

**④ 控制台**

黑底终端风。顶部：构建号 + 任务名 + 状态徽章 + 已运行时长 + `[中止]` 按钮 + `[自动滚动]` 开关 + `[下载日志]`。
中部：日志区域，等宽字体。每个步骤渲染为一个可折叠区块，头部显示 `[3/7] 运行 pytest  ✓ 2.4s`，
标题行颜色按成功/失败区分，默认展开当前正在跑的，折叠已完成的。

**⑤ 顶栏**

常驻显示 `运行中 2 · 排队 1`，点击跳到队列总览。数据靠 3 秒轮询 `/api/queue`。

### 交互细节

- 所有耗时超过 300ms 的请求显示 loading 状态
- 表单校验错误内联显示在对应字段下方
- 构建触发成功后立即跳转到控制台页
- 页面卸载时主动关闭 SSE 连接，防止连接泄漏

## 10. 桌面通知

`ci_runner/notify.py`，本身不引入 Python 依赖。

- **主方案**：调 PowerShell 走 WinRT `Windows.UI.Notifications` API 弹 Toast
- **降级**：Toast 失败时（如系统禁用了通知）退到 `winsound` 播放系统提示音 + 任务栏闪烁
- **绝不能因为通知失败而影响构建结果**：整个通知调用包在 try/except 里，失败只记日志

### 通知策略（可在设置页改）

| 场景 | 默认 |
|---|---|
| 构建失败 | 通知 |
| 手动触发的构建成功 | 通知 |
| 定时触发的构建成功 | **不通知**（否则每天早上必弹一次） |
| 构建超时 / 被中止 | 通知 |

通知内容：任务名 + 构建号 + 结果 + 耗时，如：
`❌ nebula-tools #12 构建失败（3分24秒）`

## 11. 调度

`ci_runner/scheduler.py` 封装 APScheduler 的 `BackgroundScheduler`。

- 工具启动时，读所有 `enabled=True` 且 `cron_expr` 非空的 job，各注册一个 cron 任务
- 新增/修改/删除/启用/禁用 job 时，同步增删改对应的调度任务
- 调度任务 ID 用 `job_{id}`，便于同步管理
- 触发时走**和执行引擎完全相同的入口**，`trigger="cron"`
- 若触发时该任务已有构建在跑或排队，**跳过这次触发**（不排队，避免定时任务堆积）。
  跳过时**不产生任何构建记录**，只在应用日志（进程 stdout）里写一行
  `[scheduler] skip job=nebula-tools #12 already running`

最后一条很重要：如果一个任务设定每 5 分钟跑一次但每次要跑 10 分钟，排队会让积压越来越严重。
跳过并记录是唯一合理的行为。

## 12. 目录结构

```
CI/
├── ci_runner/
│   ├── __init__.py
│   ├── main.py          FastAPI 应用装配 + 启动入口（uvicorn.run）
│   ├── config.py        端口 / 数据目录 / 默认值常量
│   ├── db.py            引擎、Session、WAL 设置、建表
│   ├── models.py        SQLAlchemy 模型
│   ├── schemas.py       Pydantic 请求/响应模型
│   ├── executor.py      构建执行引擎（并发控制 + 步骤执行 + 进程树清理）
│   ├── scheduler.py     APScheduler 封装
│   ├── loghub.py        日志环形缓冲 + 落盘 + SSE 广播
│   ├── notify.py        Windows Toast 通知
│   └── api/
│       ├── __init__.py
│       ├── jobs.py      任务相关路由
│       ├── builds.py    构建相关路由
│       └── misc.py      队列 / 设置 / 健康检查
├── web/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── tests/
│   ├── conftest.py
│   ├── test_executor.py
│   ├── test_api_jobs.py
│   ├── test_api_builds.py     含 SSE / abort / 日志增量拉取
│   ├── test_loghub.py
│   └── test_scheduler.py
├── start.bat            双击启动：起服务 + 等端口就绪 + 自动开浏览器
├── data/                运行时生成，ci.db
├── logs/                运行时生成，<job_id>/<build_number>.log
├── .gitignore           忽略 data/ logs/ __pycache__/
└── README.md
```

## 13. 配置默认值

| 配置项 | 默认值 | 位置 |
|---|---|---|
| 监听地址 | `127.0.0.1` | `config.py` |
| 端口 | `8899` | `config.py` |
| 并发线程数 | `4` | 设置表，可在界面改 |
| 单步骤超时 | `1800` 秒 | 每个任务可单独设 |
| 日志环形缓冲行数 | `2000` | `config.py` |
| 构建历史保留 | 全部保留 | 不做自动清理 |

端口选 8899 的理由：避开 8000 / 8080 / 3000 / 5173 这些被开发服务器大量占用的常用端口。

## 14. 测试策略

用 pytest + FastAPI `TestClient`（两者都已安装）。重点测那些**不看代码就不知道对不对**的地方：

### test_executor.py（最重要）

- 同一任务连续触发两次 → 第二次被拒绝（409），不是并行跑
- 两个不同任务同时触发 → 都进入 running，验证并发确实生效
- 步骤返回非 0 且 `fail_fast=True` → 后续步骤状态为 `skipped`，构建为 `failed`
- 步骤返回非 0 但 `continue_on_failure=True` → 后续步骤仍执行，构建最终仍为 `failed`
- 超时 → 构建状态为 `timeout`，且子进程树真的被杀死（用一个会派生子进程的测试脚本验证）
- 中止 → 状态为 `aborted`，子进程树被杀死
- 中文输出不丢失、不乱码（步骤输出含中文，断言日志文件里能读到正确中文）

### test_loghub.py

- 环形缓冲超过上限后，最老的行被丢弃、最新行仍在
- 多个订阅者都能收到同一行（广播不丢）
- 日志文件内容与缓冲内容一致

### test_api_jobs.py

- 创建任务时 `workdir` 不存在 → 400
- cron 表达式非法 → 400，合法 → 200
- 名称重复 → 409
- `PUT` 更新步骤列表为 3 个 → 数据库里确实只有 3 个，且 `order_index` 为 0/1/2
- 删除任务 → 步骤和构建历史一并级联删除
- 删除**有构建正在运行**的任务 → 409，且任务、步骤、构建历史都还在

### test_api_builds.py

- `abort` 一个 `queued` 的构建 → 状态变 `aborted`，且该构建从未启动过子进程
- `abort` 一个已结束的构建 → 409
- 增量取日志：`offset=0` 拿到全部；带着上次的 `next_offset` 再取 → 只拿到新增行，无重复
- SSE：连上后触发构建，能依次收到 `log` 事件和最后的 `end` 事件

### test_scheduler.py

- 注册/修改/禁用任务时，APScheduler 的 job 数量正确同步
- `enabled=False` 的任务不会被调度
- 已有构建在跑时，定时触发被跳过而不是排队，且**不产生构建记录**
- 把 `max_workers` 从 4 改成 1 后，再投递多个构建 → 只有 1 个进入 `running`，其余 `queued`；改回 4 后剩余的陆续被派发

### 端到端冒烟

一个真实跑通的测试：建任务（含一条 `echo` 和一个故意失败的命令）→ 触发 → 等结束 →
断言状态、日志内容、每步状态。

## 15. 启动方式

`start.bat` 做的事：

1. `cd` 到脚本所在目录（这样双击也能找到相对路径）
2. 检查 `data/` 和 `logs/` 目录，不存在则创建
3. 启动 `python -m uvicorn ci_runner.main:app --host 127.0.0.1 --port 8899`
4. 轮询 `GET /api/health` 直到返回 200（最多 15 秒）；超时则报错并提示看启动日志
5. `start http://127.0.0.1:8899` 打开浏览器
6. 保持窗口打开，Ctrl+C 停止

不注册任何系统服务、不写注册表、不开机自启。要它常驻就自己开个终端窗口挂着。

## 16. 风险与对策

| 风险 | 对策 |
|---|---|
| 子进程清理不干净，累积僵尸进程 | 超时/中止一律 `taskkill /F /T`；工具退出时清理所有活跃子进程 |
| 中文日志乱码 | 强制 UTF-8 代码页 + `errors='replace'` 兜底 + 专门的测试用例 |
| 长时间运行内存增长（日志堆积） | 环形缓冲上限 2000 行；日志主体在磁盘上 |
| SQLite 并发写锁 | 开启 WAL 模式；执行层与 API 层用独立 Session |
| 端口 8899 被占用 | 启动时检测并明确报错，提示改 `config.py` 或关掉占用进程 |
| 定时任务堆积 | 已有构建在跑时跳过本次触发并记日志 |
| 桌面通知被系统禁用 | 降级到提示音；通知失败绝不影响构建结果 |

## 17. 实施顺序建议

按依赖关系，每一步都能独立验证：

1. **骨架**：`config.py` / `db.py` / `models.py` / `main.py` + 健康检查接口，能起来
2. **日志通道**：`loghub.py` + 单元测试（不含 HTTP）
3. **执行引擎**：`executor.py` + 单元测试（这是最难的部分，优先做透）
4. **任务 API**：`schemas.py` + `api/jobs.py` + 测试
5. **构建 API**：`api/builds.py`（含 SSE）+ 测试
6. **调度**：`scheduler.py` + 测试
7. **通知**：`notify.py`
8. **前端**：`web/` 三个文件，基于已稳定的 API 开发
9. **启动脚本 + README**
10. **端到端冒烟测试**
