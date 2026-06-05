---
name: "Shell脚本指南"
description: "Shell 脚本编写参考——Bash 语法、错误处理、参数解析、临时文件、并行执行、进程管理。适用于编写健壮、可移植的自动化脚本。"
---

# Shell 脚本指南

编写可靠、可维护的 Bash 脚本。涵盖参数解析、错误处理、可移植性、临时文件、并行执行、进程管理和自文档化脚本。

## 何时使用

- 编写供他人（或未来的你）运行的脚本
- 自动化多步骤工作流
- 使用标志和选项解析命令行参数
- 正确处理错误和清理
- 并行运行任务
- 编写可在 Linux 和 macOS 间移植的脚本
- 用更简单的接口包装复杂命令

## 脚本模板

```bash
#!/usr/bin/env bash
set -euo pipefail

# 描述：一行说明脚本功能
# 用法：script.sh [选项] <必需参数>

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

# 默认值
VERBOSE=false
OUTPUT_DIR="./output"

usage() {
    cat <<EOF
用法：$SCRIPT_NAME [选项] <输入文件>

描述：
  处理输入文件并生成输出。

选项：
  -o, --output DIR    输出目录（默认：$OUTPUT_DIR）
  -v, --verbose       启用详细输出
  -h, --help          显示此帮助信息

示例：
  $SCRIPT_NAME data.csv
  $SCRIPT_NAME -v -o /tmp/results data.csv
EOF
}

log() { echo "[$(date '+%H:%M:%S')] $*" >&2; }
debug() { $VERBOSE && log "DEBUG: $*" || true; }
die() { log "ERROR: $*"; exit 1; }

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output) OUTPUT_DIR="$2"; shift 2 ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -h|--help) usage; exit 0 ;;
        --) shift; break ;;
        -*) die "未知选项：$1" ;;
        *) break ;;
    esac
done

INPUT_FILE="${1:?$(usage >&2; echo "错误：需要输入文件")}"
[[ -f "$INPUT_FILE" ]] || die "文件不存在：$INPUT_FILE"

# 主逻辑
main() {
    debug "输入：$INPUT_FILE"
    debug "输出：$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"

    log "正在处理 $INPUT_FILE..."
    # ... 做工作 ...
    log "完成。输出在 $OUTPUT_DIR"
}

main "$@"
```

## 错误处理

### set 标志

```bash
set -e          # 任何命令失败时退出
set -u          # 未定义变量时报错
set -o pipefail # 管道中任何命令失败则管道失败
set -x          # 调试：执行前打印每个命令（较吵）

# 组合（在每个脚本中使用）
set -euo pipefail

# 临时禁用（用于允许失败的命令）
set +e
some_command_that_might_fail
exit_code=$?
set -e
```

### Trap 清理

```bash
# 退出时清理（任何退出：成功、失败或信号）
TMPDIR=""
cleanup() {
    [[ -n "$TMPDIR" ]] && rm -rf "$TMPDIR"
}
trap cleanup EXIT

TMPDIR=$(mktemp -d)
# 自由使用 $TMPDIR——它会自动清理

# 陷阱特定信号
trap 'echo "中断"; exit 130' INT    # Ctrl+C
trap 'echo "终止"; exit 143' TERM    # kill
```

### 错误处理模式

```bash
# 使用前检查命令是否存在
command -v jq >/dev/null 2>&1 || die "需要 jq 但未安装"

# 提供默认值
NAME="${NAME:-default_value}"

# 必需变量（未设置则失败）
: "${API_KEY:?错误：需要 API_KEY 环境变量}"

# 重试命令
retry() {
    local max_attempts=$1
    shift
    local attempt=1
    while [[ $attempt -le $max_attempts ]]; do
        "$@" && return 0
        log "尝试 $attempt/$max_attempts 失败。重试中..."
        ((attempt++))
        sleep $((attempt * 2))
    done
    die "命令 $max_attempts 次尝试后失败：$*"
}

retry 3 curl -sf https://api.example.com/health
```

## 参数解析

### 简单：位置参数 + 标志

```bash
FORCE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--force) FORCE=true; shift ;;
        -n|--dry-run) DRY_RUN=true; shift ;;
        -o|--output)
            [[ -n "${2:-}" ]] || die "--output 需要值"
            OUTPUT="$2"; shift 2 ;;
        --output=*)
            OUTPUT="${1#*=}"; shift ;;
        -h|--help) usage; exit 0 ;;
        --) shift; break ;;
        -*) die "未知选项：$1" ;;
        *) break ;;
    esac
done

# 剩余参数是位置参数
FILES=("$@")
[[ ${#FILES[@]} -gt 0 ]] || die "至少需要一个文件"
```

### getopts (POSIX，仅短选项)

```bash
while getopts ":o:vhf" opt; do
    case "$opt" in
        o) OUTPUT="$OPTARG" ;;
        v) VERBOSE=true ;;
        f) FORCE=true ;;
        h) usage; exit 0 ;;
        :) die "选项 -$OPTARG 需要参数" ;;
        ?) die "未知选项：-$OPTARG" ;;
    esac
done
shift $((OPTIND - 1))
```

## 临时文件和目录

```bash
# 创建临时文件（自动唯一）
TMPFILE=$(mktemp)
echo "data" > "$TMPFILE"

# 创建临时目录
TMPDIR=$(mktemp -d)

# 带自定义前缀/后缀的临时文件
TMPFILE=$(mktemp /tmp/myapp.XXXXXX)
TMPFILE=$(mktemp --suffix=.json)  # 仅 GNU

# 始终用 trap 清理
trap 'rm -f "$TMPFILE"' EXIT

# 可移植模式（macOS 和 Linux 都可用）
TMPDIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'myapp')
trap 'rm -rf "$TMPDIR"' EXIT
```

## 并行执行

### xargs -P

```bash
# 并行运行 4 个命令
cat urls.txt | xargs -P 4 -I {} curl -sO {}

# 并行处理文件（每次 4 个）
find . -name "*.csv" | xargs -P 4 -I {} ./process.sh {}

# 带进度指示器的并行
find . -name "*.jpg" | xargs -P 8 -I {} sh -c 'convert {} -resize 800x600 resized/{} && echo "完成：{}"'
```

### 后台作业 + wait

```bash
# 在后台运行任务，等待所有完成
pids=()
for file in data/*.csv; do
    process_file "$file" &
    pids+=($!)
done

# 等待所有并检查结果
failed=0
for pid in "${pids[@]}"; do
    wait "$pid" || ((failed++))
done
[[ $failed -eq 0 ]] || die "$failed 个任务失败"
```

### GNU Parallel（如可用）

```bash
# 用 8 个并行作业处理文件
parallel -j 8 ./process.sh {} ::: data/*.csv

# 带进度条
parallel --bar -j 4 convert {} -resize 800x600 resized/{/} ::: *.jpg

# 管道输入行
cat urls.txt | parallel -j 10 curl -sO {}
```

## 进程管理

### 后台进程

```bash
# 后台启动
long_running_command &
BG_PID=$!

# 检查是否仍在运行
kill -0 $BG_PID 2>/dev/null && echo "运行中" || echo "已停止"

# 等待它
wait $BG_PID
echo "退出码：$?"

# 脚本退出时杀掉它
trap 'kill $BG_PID 2>/dev/null' EXIT
```

### 进程监督

```bash
# 运行命令，如死亡则重启
run_with_restart() {
    local cmd=("$@")
    while true; do
        "${cmd[@]}" &
        local pid=$!
        log "已启动 PID $pid"
        wait $pid
        local exit_code=$?
        log "进程退出码 $exit_code。5秒后重启..."
        sleep 5
    done
}

run_with_restart ./my-server --port 8080
```

### 超时

```bash
# 30 秒后终止命令
timeout 30 long_running_command

# 自定义信号（SIGTERM 失败后 SIGKILL）
timeout --signal=TERM --kill-after=10 30 long_running_command

# 可移植（无 timeout 命令）
( sleep 30; kill $$ 2>/dev/null ) &
TIMER_PID=$!
long_running_command
kill $TIMER_PID 2>/dev/null
```

## 可移植性（Linux vs macOS）

### 常见差异

```bash
# sed：macOS 需要 -i ''（空备份扩展名）
# Linux：
sed -i 's/old/new/g' file.txt
# macOS：
sed -i '' 's/old/new/g' file.txt
# 可移植：
sed -i.bak 's/old/new/g' file.txt && rm file.txt.bak

# date：不同标志
# GNU (Linux)：
date -d '2026-02-03' '+%s'
# BSD (macOS)：
date -j -f '%Y-%m-%d' '2026-02-03' '+%s'

# readlink -f：macOS 上不存在
# 可移植替代：
real_path() { cd "$(dirname "$1")" && echo "$(pwd)/$(basename "$1")"; }

# stat：不同语法
# GNU：stat -c '%s' file
# BSD：stat -f '%z' file

# grep -P：macOS 默认不可用
# 使用 grep -E，或安装 GNU grep
```

### POSIX 安全模式

```bash
# 使用 printf 而不是 echo -e（echo 行为不同）
printf "Line 1\nLine 2\n"

# 使用 $() 而不是反引号
result=$(command)   # 好
result=`command`    # 不好（已弃用，嵌套问题）

# 测试用 [[ ]]（bash），[ ] 用于 POSIX sh
[[ -f "$file" ]]   # Bash（更安全，无单词分割）
[ -f "$file" ]     # POSIX sh
```

## 配置文件解析

### 来源配置文件

```bash
# 简单：source key=value 文件
# config.env:
# DB_HOST=localhost
# DB_PORT=5432

# source 前验证（安全：检查命令）
if grep -qP '^[A-Z_]+=.*[;\`\$\(]' config.env; then
    die "配置文件包含不安全字符"
fi
source config.env
```

### 解析 INI 风格配置

```bash
# config.ini:
# [database]
# host = localhost
# port = 5432
# [app]
# debug = true

parse_ini() {
    local file="$1" section=""
    while IFS='= ' read -r key value; do
        [[ -z "$key" || "$key" =~ ^[#\;] ]] && continue
        if [[ "$key" =~ ^\[(.+)\]$ ]]; then
            section="${BASH_REMATCH[1]}"
            continue
        fi
        value="${value%%#*}"     # 剥离行内注释
        value="${value%"${value##*[![:space:]]}"}"  # 修剪尾部空白
        printf -v "${section}_${key}" '%s' "$value"
    done < "$file"
}

parse_ini config.ini
echo "$database_host"  # localhost
echo "$app_debug"      # true
```

## 常用模式

### 破坏性操作前确认

```bash
confirm() {
    local prompt="${1:-确定吗？}"
    read -rp "$prompt [y/N] " response
    [[ "$response" =~ ^[Yy]$ ]]
}

confirm "删除 /tmp/data 中的所有文件？" || die "已取消"
rm -rf /tmp/data/*
```

### 进度指示器

```bash
# 简单计数器
total=$(wc -l < file_list.txt)
count=0
while IFS= read -r file; do
    ((count++))
    printf "\r处理 %d/%d..." "$count" "$total" >&2
    process "$file"
done < file_list.txt
echo "" >&2
```

### 锁文件（防止并发运行）

```bash
LOCKFILE="/tmp/${SCRIPT_NAME}.lock"

acquire_lock() {
    if ! mkdir "$LOCKFILE" 2>/dev/null; then
        die "另一个实例正在运行（锁：$LOCKFILE）"
    fi
    trap 'rm -rf "$LOCKFILE"' EXIT
}

acquire_lock
# ... 安全进行，只有一个实例运行 ...
```

### stdin 或文件参数

```bash
# 从文件参数或 stdin 读取
input="${1:--}"   # 默认 "-"（stdin）
if [[ "$input" == "-" ]]; then
    cat
else
    cat "$input"
fi | while IFS= read -r line; do
    process "$line"
done
```

## 重定向和管道

### 重定向参考

| 重定向 | 说明 |
|--------|------|
| `cmd > file` | stdout 到文件（覆盖） |
| `cmd >> file` | stdout 到文件（追加） |
| `cmd 2>&1` | stderr 到 stdout |
| `cmd &> file` | 所有输出到文件 |
| `cmd < file` | 从文件读取 stdin |
| `cmd1 \| cmd2` | cmd1 stdout 到 cmd2 stdin |

### 进程替换

```bash
# 比较两个排序文件的差异
diff <(sort file1) <(sort file2)

# 读取命令输出作为文件
while IFS= read -r line; do
    process "$line"
done < <(grep pattern file)
```

## 信号和陷阱

### 信号列表

| 信号 | 说明 | 常见用途 |
|------|------|----------|
| SIGTERM | 优雅终止请求 | `kill` 默认 |
| SIGINT | 中断（Ctrl+C） | 交互中断 |
| SIGHUP | 挂起 | 终端关闭 |
| SIGKILL | 强制终止 | 无法优雅终止时 |
| SIGEXIT | 脚本退出 | 清理 |

### 陷阱命令

```bash
trap 'echo "收到信号"; cleanup; exit 130' INT TERM
trap 'rm -f "$TMPFILE"' EXIT
trap 'log "错误行：$LINENO"' ERR
```

## 调试技巧

```bash
# 语法检查（不执行）
bash -n script.sh

# 跟踪执行
bash -x script.sh

# 调试特定部分
set -x
# 要调试的代码
set +x

# 常见调试标志
set -euo pipefail  # 严格模式
set -x            # 跟踪
```

## 最佳实践

- 始终以 `set -euo pipefail` 开头。它能捕获 80% 的静默 bug。
- 对临时文件始终使用 `trap cleanup EXIT`。不要依赖到达末尾的清理代码。
- 所有变量展开都要加引号：`"$var"` 而不是 `$var`。未加引号的变量在有空 格和通配符时会出问题。
- 在 bash 中用 `[[ ]]` 而不是 `[ ]`。它处理空字符串、空格和模式匹配更好。
- `shellcheck` 是最好的 shell 脚本检查工具。运行它：`shellcheck myscript.sh`。
- 用 `readonly` 声明常量防止意外覆盖：`readonly DB_HOST="localhost"`。
- 写一个 `usage()` 函数，在 `-h`/`--help` 和缺少必需参数时调用它。
- 优先使用 `printf` 而不是 `echo`，尤其对于可能包含特殊字符或需要格式化的内容。
- 运行前用 `bash -n script.sh`（语法检查）测试脚本。

---

**编写健壮脚本，让未来感谢今天的你。**