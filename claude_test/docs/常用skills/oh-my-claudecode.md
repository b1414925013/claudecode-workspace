# oh-my-claudecode 快速入门

仓库地址：[https://github.com/Yeachan-Heo/oh-my-claudecode/](https://github.com/Yeachan-Heo/oh-my-claudecode/)
官方手册：[https://yeachan-heo.github.io/oh-my-claudecode-website/docs.html](https://yeachan-heo.github.io/oh-my-claudecode-website/docs.html)

## 为什么选择 OMC
- **零配置**：开箱即用，智能默认设置。
- **团队优先编排**：Team 模式是规范的多智能体交互方式。
- **自然语言界面**：无需记忆命令，直接描述需求即可。
- **自动并行化**：将复杂任务分布在专业代理之间执行。
- **持久执行**：直到任务经验证完成才会停止（Ralph模式）。
- **成本优化**：智能模型路由可节省约 30-50% 的 Tokens 成本。
- **从经验中学习**：自动提取并重复使用解决问题的模式。
- **实时可视化**：提供 HUD 状态显示动态。

## 安装、设置与更新

**步骤1：安装插件**
```bash
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode 
/plugin install oh-my-claudecode
```

**步骤2：初始化设置**
配置一次大约需要10-15分钟。必须在设置完成后再使用，如果刚更新过也需要重新设置对齐版本。
```bash
/omc-setup
```

**步骤3：更新**
```bash
/plugin marketplace update omc
/omc-setup
```
> **注意**：更新插件后、在不同机器上使用或在新项目中，都必须重新运行 `/omc-setup`（新项目使用 `/oh-my-claudecode:omc-setup --local`）。

**卸载方法**
```bash
curl -fsSL https://raw.githubusercontent.com/Yeachan-Heo/oh-my-claudecode/main/scripts/uninstall.sh | bash
```

## 魔法关键词（高级用户快捷方式）

OMC 包含了智能行为，并在提示中自然包含关键词即可激活对应模式：
- **`ralph`**: 持久模式（自动包含最大并行执行）。例如："ralph: 修复认证 bug"
- **`ralplan`**: 迭代规划。例如："ralplan 这个功能"
- **`ulw`**: 最大并行度。例如："ulw 重构 API"
- **`plan`**: 规划访谈。例如："plan 新的端点"
- **`team`**: 协调代理。例如：`/team 4:executor 修复错误`

## Team Mode（推荐模式）

从 v4.1.7 开始，Team 成为 OMC 中的规范编排表面（原生团队调度）。
```bash
/team 3:executor "fix all TypeScript errors"
```
其按阶段化流水线运行逻辑：`team-plan` → `team-prd` → `team-exec` → `team-verify` → `team-fix` (循环)

> 运行过 `/omc-setup` 之后 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 会自动配置无需手动修改。

## 常见问题

**Ralph 循环停不下来**
由 OMC 发起的 Ralph 循环有时候可能停不下来，可以使用以下命令取消：
```bash
/oh-my-claudecode:cancel
```
如果取消失败，可以使用强制退出和清理：
```bash
/oh-my-claudecode:cancel --force
```
*(注：该问题已通过社区 PR 1306 修复，请升级至最新版本)*
