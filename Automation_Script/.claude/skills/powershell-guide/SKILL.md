---
name: "PowerShell指南"
description: "PowerShell 脚本编写指南——避免常见错误、可靠执行、安全链接命令。包含输出行为、数组陷阱、比较操作符、错误处理、命令链接、参数安全、路径处理、编码处理、重试与恢复机制。"
---

# PowerShell 指南

全面的 PowerShell 脚本编写参考，涵盖基础语法、可靠执行模式和最佳实践。

## 输出行为

- 所有未捕获的值都会输出——即使没有 `return` 或 `Write-Output`
- `return` 不会停止输出——之前未捕获的表达式仍会输出
- `Write-Host` 绕过管道——仅用于显示，不用于数据
- 赋值给 `$null` 可抑制输出——`$null = SomeFunction`
- `[void]` 强制转换也可抑制——`[void](SomeFunction)`

## 数组陷阱

- 单项结果是标量，不是数组——`@(Get-Item .)` 强制转为数组
- 空结果是 `$null`，不是空数组——用 `if ($result)` 小心检查
- 管道中数组会展开——`@(1,2,3) | ForEach-Object` 逐个发送元素
- `+=` 会创建新数组——循环中性能差，用 `[System.Collections.ArrayList]`
- `,` 是数组运算符——`,$item` 将单项包装成数组

## 比较操作符

- 用 `-eq`, `-ne`, `-gt`, `-lt`——不是 `==`, `!=`, `>`, `<`
- `-like` 通配符，`-match` 正则——都返回布尔值
- `-contains` 检查数组成员——`$arr -contains $item`
- 默认不区分大小写——用 `-ceq`, `-cmatch` 区分大小写
- `$null` 放左边——`$null -eq $var` 防止数组比较问题

## 字符串处理

- 双引号内插值——`"Hello $name"` 展开变量
- 单引号字面量——`'$name'` 保持原样
- 子表达式处理复杂情况——`"Count: $($arr.Count)"` 获取属性/方法
- Here-string 多行文本——`@" ... "@` 或 `@' ... '@`
- 反引号转义——`` `n `` 换行，`` `t `` 制表符

## 管道

- `$_` 或 `$PSItem` 是当前对象
- `ForEach-Object` 用于管道——`foreach` 语句不接受管道
- `-PipelineVariable` 保存中间结果
- 管道逐个处理——除非函数不支持流

## 错误处理

- `$ErrorActionPreference` 设置默认行为
- `-ErrorAction Stop` 逐命令设置——使非终止错误变为终止错误
- `try/catch` 只捕获终止错误——先设置 `ErrorAction Stop`
- `$?` 表示上一个命令是否成功
- `$LASTEXITCODE` 用于原生命令

## 可靠命令链接

### 安全链接模式

**错误**:
```powershell
mkdir test && cd test && echo done
```

**正确**:
```powershell
$ErrorActionPreference = 'Stop'
try {
    New-Item -ItemType Directory -Path test -Force
    Set-Location test
    Write-Host 'done'
} catch {
    Write-Error "Failed: $_"
    exit 1
}
```

### 条件链接

```powershell
if (Test-Path $file) {
    Remove-Item $file
    Write-Host "Deleted"
} else {
    Write-Warning "File not found"
}
```

### Splatting 复杂命令

```powershell
$params = @{
    Path = $filePath
    Encoding = 'UTF8'
    Force = $true
}
Set-Content @params
```

## 参数安全

**错误**:
```powershell
git commit -m "message"
```

**正确**:
```powershell
git commit -Message "message"
# 或使用 splatting:
$params = @{ Message = "message" }
git commit @params
```

## 路径处理

**错误**:
```powershell
$path = "C:/Users/name/file.txt"
```

**正确**:
```powershell
$path = Join-Path $env:USERPROFILE "file.txt"
# 或使用字面量路径:
$path = 'C:\Users\name\file.txt'
```

## 输出编码

**错误**:
```powershell
echo "text" > file.txt
```

**正确**:
```powershell
"text" | Out-File -FilePath file.txt -Encoding UTF8
```

## 重试与恢复

### 重试模式

```powershell
function Invoke-Retry {
    param(
        [scriptblock]$Command,
        [int]$MaxAttempts = 3,
        [int]$DelaySeconds = 2
    )

    $attempt = 0
    while ($attempt -lt $MaxAttempts) {
        try {
            $attempt++
            return & $Command
        } catch {
            if ($attempt -eq $MaxAttempts) { throw }
            Start-Sleep -Seconds $DelaySeconds
        }
    }
}
```

### 检查点模式（长任务恢复）

```powershell
$checkpointFile = ".checkpoint.json"

if (Test-Path $checkpointFile) {
    $state = Get-Content $checkpointFile | ConvertFrom-Json
    Write-Host "从步骤 $($state.step) 恢复"
} else {
    $state = @{ step = 0 }
}

switch ($state.step) {
    0 {
        $state.step = 1
        $state | ConvertTo-Json | Out-File $checkpointFile
    }
    1 {
        Remove-Item $checkpointFile
    }
}
```

## 会话连续性（后台任务）

```powershell
$job = Start-Job -ScriptBlock {
    param($arg)
    # 长时间操作
} -ArgumentList $arg

Wait-Job $job -Timeout 300

if ($job.State -eq 'Completed') {
    Receive-Job $job
} else {
    Stop-Job $job
    Write-Warning "任务超时"
}
```

## 跨平台

- `pwsh` 是 PowerShell 7+——`powershell` 是 Windows PowerShell 5.1
- 路径用 `/` 或 `\`——用 `Join-Path` 保证可移植
- 环境变量用 `$env:VAR`
- 别名在不同平台可能不同——用完整的 cmdlet 名称

## 常见错误

- `if` 的 `{` 前没空格——`if ($x) {` 更好
- `=` 在条件中是赋值——比较用 `-eq`
- 函数返回数组会展开——用 `return ,@($arr)` 保持数组
- `Get-Content` 返回行数组——用 `-Raw` 获取单个字符串
- `Select-Object` 创建新对象——属性是副本，不是引用

## 快速参考

| 任务 | Bash | PowerShell |
|------|------|------------|
| 列出文件 | `ls -la` | `Get-ChildItem -Force` |
| 切换目录 | `cd /path` | `Set-Location C:\path` |
| 创建目录 | `mkdir x` | `New-Item -ItemType Directory x` |
| 复制文件 | `cp a b` | `Copy-Item a b` |
| 移动文件 | `mv a b` | `Move-Item a b` |
| 删除 | `rm x` | `Remove-Item x` |
| 查看文件 | `cat x` | `Get-Content x` |
| 编辑文件 | `vim x` | `notepad x` |
| 查找文本 | `grep x` | `Select-String x` |
| 管道 | `\|` | `\|` (相同) |
| 重定向 | `>` | `>` (用 Out-File) |

---

**编写可靠脚本，优雅恢复。**