# 🎯 Skill Creator 使用指南

> 快速创建自定义 Claude Skills，让 AI 按你的规则工作

---

## 📦 安装

```bash
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
```

**前置条件**：确保 Skills 功能已启用

---

## 🚀 快速开始

### 步骤 1：创建你的第一个 Skill

在聊天框中直接告诉 Claude：

```
使用 skill-creator 帮我创建一个新的 Claude Skill。
目标是：[描述你的需求]
```

**示例**：

```
使用 skill-creator 帮我创建一个新的 Claude Skill。
目标是：管理简单的 ToDo List，支持增删改查任务，并根据任务状态输出结构化 JSON。
```

### 步骤 2：回答 Claude 的问题

Claude 会询问一些关键信息：

- ✅ Skill 名称
- ✅ 使用说明
- ✅ 输入/输出格式
- ✅ 特殊逻辑或边界条件

> 💡 **提示**：描述越精确，生成的 Skill 质量越高

### 步骤 3：获取生成结果

生成的 Skill 通常包含：

```
my-skill/
├── SKILL.md          # 主文件
├── examples/         # 使用示例
└── guidelines/       # 规则与约束
```

---

## 📋 Skill 文件结构

标准的 Skill 文件格式：

```markdown
---
name: todo-manager
description: 管理待办事项的 Skill，提供结构化 JSON 结果
---

# Todo Manager Skill

这里写你的具体操作逻辑和规则

## Examples

- 增加 ToDo: "添加任务 写报告 截止 2026-01-20"
- 标记完成: "完成任务 写报告"
- 列出未完成任务

## Guidelines

- 所有输出应尽量用 JSON
- 不要包含无关文本
```

---

## 💡 实用示例模板

### 📊 示例 A：数据分析 Skill

```
使用 skill-creator 创建一个 Skill：

目标：分析 CSV 销售数据。接受文件链接，输出季度报表 + 销售趋势图的结构化 JSON。

输出细则：
- 总销售额
- 按地区拆分
- 趋势图 base64
- 推荐 3 个业务提升建议
```

### 🔧 示例 B：代码重构 Skill

```
使用 skill-creator 创建一个 Skill：

目标：接受 JS 代码片段，自动重构成更清晰 & 模块化版本，并输出重构后的代码 + 改动说明。

输出格式：
{
  "before": "原始代码",
  "after": "重构后代码",
  "changes": ["改动说明列表"]
}
```

### 🎨 示例 C：品牌规范 Skill

```
使用 skill-creator 创建一个 Skill：

目标：根据公司品牌规范文本，生成符合规范的社交媒体文案模板。

规范要求：
- Logo 不变形
- 颜色代码固定
- 文案必须符合品牌指南

输出：JSON 规则 + 示例文本
```

---

## ⭐ 最佳实践

| 原则 | 说明 |
|------|------|
| **🎯 描述具体** | 写清楚输入、输出、边界条件、格式约束 |
| **📐 结构化输出** | 优先使用 JSON、CSV、表格等标准格式 |
| **🧪 准备测试样本** | 生成后立即测试，查缺补漏 |
| **🔄 迭代优化** | 不够完善时继续用 skill-creator 补充 |
| **📝 完善文档** | 写好 Examples 和 Guidelines，提高调用准确性 |

---

## 🎓 进阶技巧

### 让 Skill 更智能

1. **添加错误处理**：定义异常情况的处理方式
2. **设置默认值**：为可选参数提供合理默认值
3. **版本控制**：在 Skill 中标注版本号，便于迭代
4. **测试用例**：提供多个测试场景，覆盖边界情况

### 输出格式建议

```json
{
  "status": "success",
  "data": {},
  "metadata": {
    "timestamp": "2026-02-26",
    "version": "1.0.0"
  }
}
```

---

## 📚 相关资源

- [Anthropic Skills 官方文档](https://github.com/anthropics/skills)
- [Skill 示例库](https://github.com/anthropics/example-skills)
- [社区 Skills 分享](https://community.anthropic.com/skills)

---

**🎉 现在开始创建你的第一个 Skill 吧！**
