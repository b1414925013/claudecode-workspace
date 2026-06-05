# Ralph-Loop 新手指南：Claude Code 自动化迭代利器

`Ralph-Loop` 是 Claude Code 中一个强大的插件/技术，它允许 AI 进入一个“自我迭代”的循环，通过不断的“执行 -> 验证 -> 修复”过程，直到完成你设定的目标。

---

## 一、 什么是 Ralph-Loop？

**Ralph-Loop** 是一种 AI Agent 的“循环编程”技术。简单来说，就是你告诉 AI 一个任务和完成标准，AI 会自动重复执行：**写代码 -> 自检 -> 修复 Bug -> 再次测试**，直到满足条件或达到最大迭代次数。

> [!NOTE]
> **命名背景**：取自《辛普森一家》中的 Ralph Wiggum。象征着虽然可能会像小孩子一样犯错，但始终保持认真执行、不断尝试、直到成功。

---

## 二、 核心机制：Stop Hook

Ralph-Loop 在 Claude Code 环境中引入了 **Stop Hook** 机制：
1. **完成承诺 (Completion Promise)**：用户预设一个结束标记（例如 `✅DONE`）。
2. **自我闭环**：如果不输出该标记，循环会自动重启，并带上之前的迭代历史，让 AI 继续改进，直到 AI 原样输出预设的暗号为止。

---

## 三、 安装与基础命令

### 1. 安装插件
在 Claude Code 终端中输入：
```bash
/plugin install ralph-loop@claude-plugins-official
```

### 2. 启动循环任务
```bash
/ralph-loop "你的任务描述" --completion-promise "✅DONE" --max-iterations 15
```

### 3. 其他管理命令
- `/ralph-loop:cancel-ralph`：取消当前正在进行的循环。
- `/ralph-loop:help`：显示帮助信息。

---

## 四、 核心参数详解

| 参数 | 说明 | 示例 |
| :--- | :--- | :--- |
| `prompt` | 具体的任务描述及完成标准 | `"修复所有 Lint 错误，完成后输出 ✅DONE"` |
| `--completion-promise` | **暗号/承诺标记**。AI 在完成任务后必须原样输出该字符串来停止循环。 | `"✅DONE"` 或 `"🎉OK"` |
| `--max-iterations` | **最大迭代次数**。防止死循环和过度消耗 Token，建议设为 10-30 次。 | `15` |

---

## 五、 最佳实践：5 分钟上手建议

1. **任务要“小而精”**：不要试图一次完成整个项目。例如：“让登录页测试通过”比“重构整个前端”更高效。
2. **完成标准要“可机器验证”**：
   - ✅ 正确示例：`npm test 退出码为 0`、`Lighthouse 性能分 > 90`。
   - ❌ 错误示例：`让界面更好看`（AI 无法客观判断）。
3. **先小步试水**：首次执行建议将 `max-iterations` 设为 5，观察 AI 的思路，觉得方向正确后再加大。
4. **使用状态文件**：在 Prompt 中要求 AI 将进度记录在 `progress.md` 中，这样即使中途停止，进度也不会丢失。
5. **暗号建议使用 Emoji+英文**：防止 AI 在日常对话中误触停机。推荐：`✅DONE`、`🚀COMPLETE`。

---

## 六、 实战提示词 (Prompts)

### 1. 提升测试覆盖率
```bash
/ralph-loop "将 src/ 下业务代码的测试覆盖率提升至 ≥90%
步骤：
- 运行 npm run test:cov
- 为未覆盖的部分编写测试
- 重复直到覆盖率达标
完成后输出：✅DONE" \
--max-iterations 20 \
--completion-promise "✅DONE"
```

### 2. 消灭 ESLint 错误
```bash
/ralph-loop "修复项目中所有的 ESLint 错误
- 运行 npm run lint
- 每次修复 1-3 个错误点并验证
完成后输出：✅DONE" \
--max-iterations 15 \
--completion-promise "✅DONE"
```

### 3. 框架迁移（如 Redux 迁至 Zustand）
```bash
/ralph-loop "将项目从 Redux 迁移到 Zustand
验证标准：
- 移除 @reduxjs 相关依赖
- 所有 store 逻辑改为 Zustand 实现
- npm run build 无错误
- 所有现有测试通过
完成后输出：✅DONE" \
--max-iterations 25 \
--completion-promise "✅DONE"
```

---

## 七、 常见坑位 (Troubleshooting)

- **暗号未触发**：如果 AI 没能原样输出字符串（例如多了空格或引号），循环会继续。
- **Token 消耗**：大循环会携带大量的 Context 历史，请注意监控 Token 消耗。
- **死循环**：如果任务标准定得太高（如：性能必须达到 100 分），且 AI 目前无法完全达到，可能会陷入死循环。务必设置合理的 `max-iterations`。

---

## 八、 总结：成功三件套

> **小任务 + 可验证标准 + 停机暗号 = 完美的 Ralph-Loop 体验。**

现在就去试试吧：
`/ralph-loop "将当前目录所有文件格式化成 Prettier 风格，完成后输出：🎉OK" --max-iterations 5 --completion-promise "🎉OK"`
