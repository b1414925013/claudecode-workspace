#!/usr/bin/env expect
#===============================================================================
# 多节点日志查看脚本
# 功能：支持选择节点和 IP，SSH 登录后实时查看远程日志
#===============================================================================

# 加载配置库
set SCRIPT_DIR [file dirname [info script]]
source [file join $SCRIPT_DIR "lib" "config.tcl"]

# 加载配置
if {![load_config]} {
    puts stderr "错误：加载配置失败"
    exit 1
}

# 获取配置值
set timeout [get_config "TIMEOUT"]
set ssh_user [get_config "SSH_USER"]
set ssh_pass [get_config "SSH_PASS"]
set root_pass [get_config "ROOT_PASS"]

# 日志输出
proc log {msg} {
    puts stdout "\[INFO\] $msg"
    flush stdout
}

# 获取节点列表
set node_names [get_node_names]

if {[llength $node_names] == 0} {
    puts stderr "错误：没有配置任何节点"
    exit 1
}

# 显示节点选择菜单（第一层）
log "选择要连接的节点"
puts ""
puts "======================================="
puts "         选择要连接的节点             "
puts "======================================="
puts ""

for {set i 0} {$i < [llength $node_names]} {incr i} {
    set node_name [lindex $node_names $i]
    set ips [get_node_ips $node_name]
    set ip_count [llength $ips]
    puts "  [expr {$i + 1}]. $node_name ($ip_count 个 IP)"
}

puts ""
puts "  0. 取消"
puts ""

# 获取用户选择的节点
puts -nonewline "请选择节点 \[0-[llength $node_names]\]: "
flush stdout

set choice [gets stdin]
puts ""

if {$choice eq "0" || $choice eq ""} {
    log "已取消"
    exit 0
}

if {![regexp {^[0-9]+$} $choice] || $choice < 1 || $choice > [llength $node_names]} {
    puts stderr "错误：无效选择"
    exit 1
}

# 获取选择的节点名称
set idx [expr {$choice - 1}]
set node_name [lindex $node_names $idx]
set ips [get_node_ips $node_name]
set ip_count [llength $ips]

# 显示该节点的所有 IP 选择菜单（第二层）
log "选择 $node_name 的 IP 地址"
puts ""
puts "======================================="
puts "    选择 $node_name 的 IP 地址        "
puts "======================================="
puts ""

for {set i 0} {$i < $ip_count} {incr i} {
    set ip [lindex $ips $i]
    puts "  [expr {$i + 1}]. $ip"
}

puts ""
puts "  0. 取消"
puts ""

# 获取用户选择的 IP
puts -nonewline "请选择 IP \[0-$ip_count\]: "
flush stdout

set ip_choice [gets stdin]
puts ""

if {$ip_choice eq "0" || $ip_choice eq ""} {
    log "已取消"
    exit 0
}

if {![regexp {^[0-9]+$} $ip_choice] || $ip_choice < 1 || $ip_choice > $ip_count} {
    puts stderr "错误：无效选择"
    exit 1
}

# 获取选择的 IP
set ip_idx [expr {$ip_choice - 1}]
set ssh_host [lindex $ips $ip_idx]

log "连接服务器: $ssh_host"
puts ""

# 日志文件路径
set log_file "/dd/ee/ff.log"

# 1. SSH 登录
log "正在连接 ${ssh_user}@${ssh_host}..."
spawn ssh "${ssh_user}@${ssh_host}"
expect {
    -re "password:" {
        log "发送 SSH 密码..."
        send "${ssh_pass}\r"
    }
    -re "yes/no" {
        log "接受主机密钥..."
        send "yes\r"
        expect -re "password:"
        send "${ssh_pass}\r"
    }
    timeout {
        puts stderr "错误：SSH 连接超时"
        exit 1
    }
    eof {
        puts stderr "错误：SSH 连接失败"
        exit 1
    }
}

log "已连接，等待 shell 提示符..."
expect -re {\$ |> }

log "切换到 root 用户..."
send "su - root\r"

# 2. 切换到 root
expect {
    -re "Password:" {
        log "发送 root 密码..."
        send "${root_pass}\r"
    }
    timeout {
        puts stderr "错误：su 命令超时"
        exit 1
    }
}

expect {
    -re "# |root@" {
        log "已切换到 root"
    }
    timeout {
        puts stderr "错误：切换 root 用户失败"
        exit 1
    }
}

# 3. 实时查看日志
log "实时查看日志：tail -f ${log_file}"
log "Ctrl+C 退出"
send "tail -f ${log_file}\r"

# 保持交互模式
expect {
    "# " {
        # 继续等待日志输出
    }
    eof {
        # 连接断开
    }
}

interact