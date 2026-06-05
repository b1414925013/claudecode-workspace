---
name: xiangyu-content-article-translating
description: >
  将英文 Markdown 文章翻译为中文，保留原文格式和结构。
  当用户说「翻译文章」「translate article」「转中文」时触发。
---

# 文章翻译 Skill

## 工作流

| Step | 职责 | 执行者 | 文档 | 输入 | 输出 |
|------|------|--------|------|------|------|
| 01 | 初始化 | 主Agent | step01-init.md | 用户提供文件路径 | state/ |
| 02 | 翻译输出 | SubAgent | step02-translate.md | 源文件路径 | output/ |

## 执行规范

- 渐进式披露：执行一步读一步
- SubAgent 返回极简状态，翻译结果写文件