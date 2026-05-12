# 🧠 Claude-Mem: Claude Code 的持久长期记忆插件

> **跨越会话的“数字大脑”** —— 自动捕捉编码上下文，智能压缩记忆，彻底解决 Claude Code “阅后即焚”的痛点。

---

## 🌟 简介

**Claude-Mem** 是一款专为 Claude Code 打造的开源长期记忆插件。它通过在本地建立存储系统，自动捕捉并精炼每个编码会话中的关键信息（如架构决策、Bug 修复、功能实现等），确保在开启新会话时能够无缝衔接历史上下文。

*   **GitHub**: [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
*   **核心优势**: 显著降低重复沟通成本，节省 Token 消耗，支持处理 10 万行级别的大型项目。

---

## ✨ 核心特性

### 1. 自动化记忆捕获与压缩
*   **智能过滤**: 自动从 1k-10k tokens 的工具输出中提取精华。
*   **结构化压缩**: 利用 Claude Agent SDK 将原始数据压缩为约 500 tokens 的结构化记忆片段。

### 2. 多维度存储与检索
*   **分类体系**: 记忆按类别自动归档，包括 `Decisions`（决策）、`Bug fixes`（修复）、`Features`（功能）、`Refactoring`（重构）等。
*   **双引擎搜索**:
    *   **全文搜索**: 基于 SQLite FTS5 引擎，实现毫秒级关键词定位。
    *   **语义搜索**: 集成 ChromaDB 向量数据库，支持基于意图的相关性检索。

### 3. 可视化管理
*   **Web Viewer**: 提供内置的 Web 界面，方便开发者直观地浏览、编辑和管理存储的记忆片段。
*   **AI 交互辅助**: 为 Claude Code 增加 `mem-search` 技能，AI 可主动查找历史记录。

---

## 🛠️ 技术原理：6 大核心钩子 (Hooks)

该插件通过以下 6 个生命周期钩子深度集成于 Claude Code：

1.  **SessionStart** (`context-hook.js`): 启动时检索相关记忆并预加载至上下文。
2.  **UserMessage** (`user-message-hook.js`): 实时捕捉用户的原始操作意图。
3.  **UserPromptSubmit** (`new-hook.js`): 监控最终提交给 AI 的完整 Prompt。
4.  **PostToolUse** (`save-hook.js`): 记录工具执行后的具体结果与反馈。
5.  **Stop** (`summary-hook.js`): 在会话结束前生成本阶段的精炼总结。
6.  **SessionEnd** (`cleanup-hook.js`): 执行最后的持久化存储与运行环境清理。

---

## 🚀 安装指南

### 快捷安装 (推荐)
在 Claude Code 会话中直接执行以下命令：
```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```
安装完成后，执行 `/reload` 或重启 Claude Code 即可生效。

### 源码安装 (开发/测试)
1.  **克隆仓库**:
    ```bash
    git clone https://github.com/thedotmack/claude-mem.git
    cd claude-mem
    ```
2.  **安装依赖并构建**:
    ```bash
    npm install
    npm run build
    ```
3.  **启动 Worker**:
    ```bash
    npm run worker:start
    ```

---

## 💡 使用建议

*   **定期查看记忆**: 通过 Web Viewer 检查 AI 记录的记忆是否准确，必要时进行手动修剪。
*   **明确意图**: 在对话中使用清晰的指令，有助于插件生成更高质量的总结片段。
*   **长项目必备**: 推荐在大型、长周期的开发项目中使用，以最大化发挥其上下文保留优势。