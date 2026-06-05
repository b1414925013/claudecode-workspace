#!/usr/bin/env bash
#===============================================================================
# OWS Shell 脚本启动器
# 提供交互式菜单，选择并执行 app 目录下的脚本
#===============================================================================

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly APP_DIR="${SCRIPT_DIR}/app"

# 颜色定义（使用 printf 避免 echo -e 兼容性问题）
readonly COLOR_RED='\033[0;31m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_YELLOW='\033[1;33m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_RESET='\033[0m'

# 脚本名称
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

#-------------------------------------------------------------------------------
# 日志函数
#-------------------------------------------------------------------------------
log() { printf '%s\n' "$*"; }
info() { log "[INFO] $*"; }
warn() { log "[WARN] $*" >&2; }
error() { log "[ERROR] $*" >&2; }

#-------------------------------------------------------------------------------
# 用法说明
#-------------------------------------------------------------------------------
usage() {
    cat <<EOF
用法：$SCRIPT_NAME [选项]

OWS Shell 脚本启动器

选项：
  -h, --help    显示此帮助信息
  -l, --list    仅列出可用脚本

示例：
  $SCRIPT_NAME              # 启动交互式菜单
  $SCRIPT_NAME --list       # 仅列出可用脚本
EOF
}

#-------------------------------------------------------------------------------
# 获取 app 目录下的脚本列表
#-------------------------------------------------------------------------------
get_scripts() {
    local scripts=()
    for file in "$APP_DIR"/*.sh; do
        [[ -f "$file" ]] || continue
        scripts+=("$(basename "$file")")
    done
    printf '%s\n' "${scripts[@]}"
}

#-------------------------------------------------------------------------------
# 显示菜单
#-------------------------------------------------------------------------------
show_menu() {
    local scripts
    mapfile -t scripts < <(get_scripts)

    printf '\n%s\n' "======================================="
    printf '%s\n' "         OWS Shell 脚本启动器         "
    printf '%s\n\n' "======================================="

    if [[ ${#scripts[@]} -eq 0 ]]; then
        printf '%s\n' "${COLOR_RED}没有找到可用的脚本${COLOR_RESET}"
        printf '\n'
        return 1
    fi

    for i in "${!scripts[@]}"; do
        printf '  %s%d%s. %s\n' "$COLOR_GREEN" "$((i+1))" "$COLOR_RESET" "${scripts[$i]}"
    done

    printf '\n  %s%d%s. 退出\n' "$COLOR_RED" "0" "$COLOR_RESET"
    printf '\n'
}

#-------------------------------------------------------------------------------
# 信号处理（Ctrl+C 中断）
#-------------------------------------------------------------------------------
trap 'printf "\n%s\n" "已中断"; exit 130' INT TERM

#-------------------------------------------------------------------------------
# 主菜单循环
#-------------------------------------------------------------------------------
main() {
    # 解析参数
    local list_only=false
    while [[ $# -gt 0 ]]; do
        case "${1}" in
            -h|--help) usage; exit 0 ;;
            -l|--list) list_only=true ;;
            -*) error "未知选项：${1}"; usage >&2; exit 1 ;;
            *) break ;;
        esac
        shift
    done

    local scripts
    mapfile -t scripts < <(get_scripts)

    # 仅列出模式
    if [[ "$list_only" == true ]]; then
        for i in "${!scripts[@]}"; do
            printf '%s\n' "${scripts[$i]}"
        done
        exit 0
    fi

    # 交互式菜单循环
    while true; do
        show_menu || exit 1

        read -rp "请选择要启动的脚本 [0-${#scripts[@]}]: " choice

        printf '\n'

        if [[ "$choice" == "0" ]]; then
            info "再见！"
            exit 0
        fi

        if [[ ! "$choice" =~ ^[0-9]+$ ]] || [[ $choice -lt 1 || $choice -gt ${#scripts[@]} ]]; then
            error "无效选择，请重新输入"
            printf '\n'
            read -rp "按 Enter 键继续..." -r
            continue
        fi

        local selected_script="${scripts[$((choice-1))]}"
        printf '%s%s%s\n' "$COLOR_YELLOW" "启动脚本: ${selected_script}" "$COLOR_RESET"
        printf '\n'

        # 执行选中的脚本
        "$APP_DIR/$selected_script"
        local exit_code=$?

        if [[ $exit_code -ne 0 ]]; then
            error "脚本执行失败，退出码: ${exit_code}"
        fi

        printf '\n'
        read -rp "按 Enter 键继续..." -r
    done
}

main "$@"