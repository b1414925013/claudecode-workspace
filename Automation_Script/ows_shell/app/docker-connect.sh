#!/usr/bin/env expect
#===============================================================================
# Docker 容器连接脚本
# 功能：SSH 登录后进入 Docker 容器并执行命令
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
set docker_image [get_config "DOCKER_IMAGE"]
set docker_pass [get_config "DOCKER_PASS"]

# 验证必需配置
if {$ssh_user eq "" || $ssh_host eq "" || $docker_image eq ""} {
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

# 3. 进入 Docker 容器
log "进入 Docker 容器 ${docker_image}..."
send "docker -it ${docker_image} bash\r"

# 等待容器 shell
set expect_result [expect {
    -re "root@.*:.*#" {
        log "已进入容器"
    }
    -re "password:" {
        if {$docker_pass ne ""} {
            log "发送容器密码..."
            send "${docker_pass}\r"
            expect -re "root@.*:.*#"
            log "已进入容器"
        } else {
            puts stderr "错误：容器需要密码但未配置"
            exit 1
        }
    }
    timeout {
        puts stderr "错误：进入 Docker 容器超时"
        exit 1
    }
    eof {
        puts stderr "错误：连接断开"
        exit 1
    }
}]

# 4. 切换目录
log "切换到 /aaa/bbb 目录..."
send "cd /aaa/bbb\r"
expect -re "# "

# 5. 执行 zsql 命令
log "执行 zsql -a -b..."
send "zsql -a -b\r"

expect {
    -re "password:" {
        if {$docker_pass ne ""} {
            log "发送 zsql 密码..."
            send "${docker_pass}\r"
        }
    }
    -re "# " {
        # 无需密码或已认证
    }
    timeout {
        puts stderr "警告：zsql 命令超时"
    }
}

expect -re "# "

log "脚本执行完成"
log "进入交互模式，Ctrl+C 退出"
interact