---
name: test-case-generator
description: 根据文档内容生成标准化测试用例。当用户需要从文档生成测试用例时触发此技能。
---

# Test Case Generator

根据文档内容生成符合规范的测试用例 JSON 数组。

## 输入

- `filename`: 文档名称
- `doc_content`: 文档内容（截断至 4000 字符）

## 输出格式

生成的测试用例必须包含以下字段：

```json
[{
  "case_id": "TC-模块名-序号",
  "module": "所属模块",
  "feature": "功能点",
  "precondition": "前置条件",
  "steps": ["步骤1", "步骤2"],
  "expected": "预期结果",
  "priority": "P0|P1|P2|P3",
  "browser_steps": ["action: param"]
}]
```

## browser_steps 规范

每个元素必须是 `action: param` 格式，有效 action：

- `navigate: {url}` — 打开 URL
- `fill: #selector, 文本值` — 填写文本
- `click: #selector` 或 `click: text=按钮文字` — 点击元素
- `press_key: Enter` — 按键
- `wait: 毫秒` — 等待
- `assert: text=验证文字` — 断言

**禁止使用**: `action: custom` 或空值

## 规则

1. 每个 browser_steps 元素必须是 `动作: 参数` 格式
2. selector 优先使用 `#id` 或 CSS 选择器，如 `#kw`（搜索框）、`#su`（搜索按钮）
3. 搜索框使用 `#kw`，搜索按钮使用 `#su`
4. 不生成纯描述性步骤（如"观察页面"），必须生成可自动化执行的步骤
5. 字符串使用标准 JSON 格式（英文双引号），内部引号用「」替代

## 返回

以 JSON 数组格式返回，不包含额外说明文字。