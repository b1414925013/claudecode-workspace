#!/usr/bin/env expect
#===============================================================================
# SSH 连接脚本
# 功能：连接服务器并执行数据库查询
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
set ssh_host [get_config "SSH_HOST"]
set ssh_pass [get_config "SSH_PASS"]
set root_pass [get_config "ROOT_PASS"]

# 验证必需配置
if {$ssh_user eq "" || $ssh_host eq "" || $ssh_pass eq "" || $root_pass eq ""} {
    puts stderr "错误：缺少必需的配置项"
    exit 1
}

# 日志输出
proc log {msg} {
    puts stdout "\[INFO\] $msg"
    flush stdout
}

log "正在连接 ${ssh_user}@${ssh_host}..."

# 1. SSH 登录
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

# 3. 执行 zqsl 命令
log "执行 zqsl -sys q..."
send "zqsl -sys q\r"
expect -re "# "

# 4. 执行 show database
log "执行 show database..."
send "show database;\r"
expect -re "# "

# 5. 执行 select 查询
log "执行 select * from table1..."
send "select * from table1;\r"
expect -re "# "

log "脚本执行完成"

# 保持连接供用户交互
log "进入交互模式，Ctrl+C 退出"
interact