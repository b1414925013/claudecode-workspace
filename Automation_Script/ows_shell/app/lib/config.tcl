#!/usr/bin/env tclsh
#===============================================================================
# 配置加载函数库 (Tcl 版本)
# 提供统一的配置加载功能
#
# 使用方式：
#   source [file join $SCRIPT_DIR "lib" "config.tcl"]
#   load_config
#   set value [get_config "KEY"]
#===============================================================================

# 获取脚本所在目录
set SCRIPT_DIR [file dirname [info script]]
# 配置文件的路径 (向上两级到 ows_shell 根目录)
set CONFIG_FILE [file join [file dirname [file dirname $SCRIPT_DIR]] "config" "config.conf"]

# 数组变量存储配置
array set CONFIG {}

# 标记是否已加载
variable config_loaded false

#-------------------------------------------------------------------------------
# 日志函数
#-------------------------------------------------------------------------------
proc _config_log {msg} {
    puts stderr "[config] $msg"
}
proc _config_error {msg} {
    puts stderr "[config] ERROR: $msg"
}

#-------------------------------------------------------------------------------
# 检查配置文件是否存在
#-------------------------------------------------------------------------------
proc _check_config_file {} {
    global CONFIG_FILE
    if {![file exists $CONFIG_FILE]} {
        _config_error "配置文件不存在: $CONFIG_FILE"
        return 0
    }
    return 1
}

#-------------------------------------------------------------------------------
# 加载配置
#-------------------------------------------------------------------------------
proc load_config {} {
    global CONFIG
    variable config_loaded

    if {$config_loaded} {
        return 1
    }

    if {![_check_config_file]} {
        return 0
    }

    set fp [open $CONFIG_FILE r]
    while {[gets $fp line] >= 0} {
        # 跳过注释和空行
        if {$line eq "" || [string match "#*" [string trim $line]]} {
            continue
        }

        # 解析 key=value 格式
        if {[regexp {^([^=]+)=(.*)$} $line match key value]} {
            set key [string trim $key]
            set value [string trim $value]
            # 移除引号
            regsub {^["']} $value "" value
            regsub {["']$} $value "" value
            set CONFIG($key) $value
        }
    }
    close $fp

    set config_loaded true
    return 1
}

#-------------------------------------------------------------------------------
# 获取配置值
#-------------------------------------------------------------------------------
proc get_config {key} {
    global CONFIG

    if {$key eq ""} {
        _config_error "get_config 需要配置项名称"
        return ""
    }

    if {![load_config]} {
        return ""
    }

    if {![info exists CONFIG($key)] || $CONFIG($key) eq ""} {
        _config_error "未知配置项: $key"
        return ""
    }

    return $CONFIG($key)
}

#-------------------------------------------------------------------------------
# 获取节点的所有 IP 列表
#-------------------------------------------------------------------------------
proc get_node_ips {node_name} {
    global CONFIG

    if {$node_name eq ""} {
        _config_error "get_node_ips 需要节点名"
        return ""
    }

    if {![load_config]} {
        return ""
    }

    set key "NODE_${node_name}"
    if {![info exists CONFIG($key)] || $CONFIG($key) eq ""} {
        _config_error "未找到节点 ${node_name} 的配置"
        return ""
    }

    set ips [split $CONFIG($key) ","]
    set result {}
    foreach ip $ips {
        set ip [string trim $ip]
        if {$ip ne ""} {
            lappend result $ip
        }
    }

    return $result
}

#-------------------------------------------------------------------------------
# 获取所有节点名称列表
#-------------------------------------------------------------------------------
proc get_node_names {} {
    global CONFIG

    if {![load_config]} {
        return {}
    }

    set names {}
    foreach key [array names CONFIG] {
        if {[regexp {^NODE_(.+)$} $key match name]} {
            lappend names $name
        }
    }

    return $names
}