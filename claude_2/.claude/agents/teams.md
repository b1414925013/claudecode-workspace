# Agent Teams（团队总览）

## 概览

本文档汇总了所有 Agent 和 Team 配置。

---

## Agent 列表

| 文件 | 类别 | 类型 |
|------|------|------|
| code_reviewer.md | 代码审查 | general-purpose |
| security_reviewer.md | 代码审查 | general-purpose |
| performance_reviewer.md | 代码审查 | general-purpose |
| planner.md | 架构规划 | Plan |
| researcher.md | 代码探索 | Explore |

---

## Team 列表

| 文件 | 模式 | 用途 |
|------|------|------|
| code_review_team.md | 并行 | 代码多维度审查 |
| data_pipeline_team.md | 顺序 | 数据处理流程 |
| project_development_team.md | 分层 | 复杂项目开发 |

---

## 使用方式

### 使用单个 Agent

直接读取对应 .md 文件中的 prompt 和配置。

### 使用 Team

参考 team .md 文件中的 members 列表，按模式调用多个 agent：
- **并行模式**: 同时调用所有成员
- **顺序模式**: 依次调用每个成员
- **分层模式**: 先调用 manager，由 manager 协调 worker

---

## Agent 类型说明

| 类型 | 适用场景 |
|------|----------|
| general-purpose | 通用任务，最常用 |
| Explore | 搜索探索代码库 |
| Plan | 制定实现计划和架构设计 |