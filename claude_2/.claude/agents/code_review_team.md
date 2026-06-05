# Code Review Team（代码审查团队）

## 基本信息

- **名称**: code_review_team
- **描述**: 代码审查团队 - 并行执行，多维度审查代码
- **模式**: parallel（并行）

## 团队成员

| Agent | 描述 |
|-------|------|
| code_reviewer | 负责审查代码质量和逻辑 |
| security_reviewer | 负责审查安全漏洞 |
| performance_reviewer | 负责审查性能问题 |

## 工作流程

- **类型**: 并行执行
- **描述**: 三个审查员同时工作，从不同维度审查代码
- **聚合**: 汇总三份审查报告，生成综合报告

## 使用示例

```python
# 并行调用三个审查员
code_review = agent(description="代码审查员", prompt="...", subagent_type="general-purpose")
security_review = agent(description="安全审查员", prompt="...", subagent_type="general-purpose")
performance_review = agent(description="性能审查员", prompt="...", subagent_type="general-purpose")
```