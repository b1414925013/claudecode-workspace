---
name: "WindowsGUI自动化"
description: "使用 PowerShell 自动化 Windows GUI 交互（鼠标、键盘、窗口）。当用户需要在桌面上模拟用户输入时使用，例如移动光标、点击按钮、在非 Web 应用中输入文本或管理窗口状态。"
---

# Windows UI Automation

Control the Windows desktop environment programmatically.

## Core Capabilities

- **Mouse**: Move, click (left/right/double), drag.
- **Keyboard**: Send text, press special keys (Enter, Tab, Alt, etc.).
- **Windows**: Find, focus, minimize/maximize, and screenshot windows.

## Usage Guide

### Mouse Control

Use the provided PowerShell script `mouse_control.ps1.txt`:

```powershell
# Move to X, Y
powershell -File .agents/skills/windows-ui-automation/mouse_control.ps1 -Action move -X 500 -Y 500

# Click at current position
powershell -File .agents/skills/windows-ui-automation/mouse_control.ps1 -Action click

# Right click
powershell -File .agents/skills/windows-ui-automation/mouse_control.ps1 -Action rightclick
```

### Keyboard Control

Use `keyboard_control.ps1.txt`:

```powershell
# Type text
powershell -File .agents/skills/windows-ui-automation/keyboard_control.ps1 -Text "Hello World"

# Press Enter
powershell -File .agents/skills/windows-ui-automation/keyboard_control.ps1 -Key "{ENTER}"
```

### Window Management

To focus a window by title:
```powershell
$wshell = New-Object -ComObject WScript.Shell; $wshell.AppActivate("Notepad")
```

## Best Practices

1. **Safety**: Always move the mouse slowly or include delays between actions.
2. **Verification**: Take a screenshot before and after complex UI actions to verify state.
3. **Coordinates**: Remember that coordinates (0,0) are at the top-left of the primary monitor.
