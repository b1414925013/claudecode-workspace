#!/usr/bin/env bash
#===============================================================================
# 配置加载函数库 (Bash 版本)
# 提供统一的配置加载功能
#
# 使用方式：
#   source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
#   load_config
#   value=$(get_config "KEY")
#===============================================================================

# 获取脚本所在目录
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 配置文件的路径（向上两级到 ows_shell 根目录）
readonly CONFIG_FILE="$(cd "$SCRIPT_DIR/../.." && pwd)/config/config.conf"

# 数组存储配置
declare -A CONFIG_LOADED

#-------------------------------------------------------------------------------
# 日志函数
#-------------------------------------------------------------------------------
_config_log() { printf '[config] %s\n' "$*" >&2; }
_config_error() { printf '[config] ERROR: %s\n' "$*" >&2; }

#-------------------------------------------------------------------------------
# 检查配置文件是否存在
#-------------------------------------------------------------------------------
_check_config_file() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        _config_error "配置文件不存在: $CONFIG_FILE"
        return 1
    fi
    return 0
}

#-------------------------------------------------------------------------------
# 加载配置
# 使用 source 加载配置文件，避免重复读取
#-------------------------------------------------------------------------------
load_config() {
    _check_config_file || return 1

    # 已加载则跳过
    if [[ "${CONFIG_LOADED[loaded]}" == "true" ]]; then
        return 0
    fi

    # 逐行读取配置文件
    while IFS= read -r line || [[ -n "$line" ]]; do
        # 跳过注释和空行
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        # 移除前后空白
        line="${line#"${line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"

        # 解析 key=value 格式
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"
            # 移除引号
            value="${value#\"}"
            value="${value%\"}"
            value="${value#'}"
            value="${value%'}"

            CONFIG_LOADED["$key"]="$value"
        fi
    done < "$CONFIG_FILE"

    CONFIG_LOADED[loaded]="true"
}

#-------------------------------------------------------------------------------
# 获取配置值
# 输入：配置项名称
# 输出：配置值，失败返回空
#-------------------------------------------------------------------------------
get_config() {
    local key="${1:-}"
    if [[ -z "$key" ]]; then
        _config_error "get_config 需要配置项名称"
        return 1
    fi

    load_config || return 1

    local value="${CONFIG_LOADED[$key]:-}"
    if [[ -z "$value" ]]; then
        _config_error "未知配置项: $key"
        return 1
    fi

    printf '%s' "$value"
}

#-------------------------------------------------------------------------------
# 获取节点的所有 IP 列表
# 输入：节点名（如 "master-db"）
# 输出：IP 列表（每行一个）
#-------------------------------------------------------------------------------
get_node_ips() {
    local node_name="${1:-}"
    if [[ -z "$node_name" ]]; then
        _config_error "get_node_ips 需要节点名"
        return 1
    fi

    local ips_str
    ips_str=$(get_config "NODE_${node_name}") || return 1

    if [[ -z "$ips_str" ]]; then
        _config_error "未找到节点 ${node_name} 的配置"
        return 1
    fi

    # 用逗号分隔，输出每行一个 IP
    IFS=',' read -ra ips <<< "$ips_str"
    for ip in "${ips[@]}"; do
        ip="${ip#"${ip%%[![:space:]]*}"}"
        ip="${ip%"${ip##*[![:space:]]}"}"
        [[ -n "$ip" ]] && printf '%s\n' "$ip"
    done
}

#-------------------------------------------------------------------------------
# 获取所有节点名称列表
# 输出：节点名称列表（每行一个）
#-------------------------------------------------------------------------------
get_node_names() {
    load_config || return 1

    for key in "${!CONFIG_LOADED[@]}"; do
        if [[ "$key" =~ ^NODE_(.+)$ ]]; then
            printf '%s\n' "${BASH_REMATCH[1]}"
        fi
    done
}