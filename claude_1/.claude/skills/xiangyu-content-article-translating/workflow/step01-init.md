# Step 01 - 初始化

- 执行者：主 Agent
- 输入：用户提供的文件路径
- 输出：state/progress.json

## 执行说明

1. 接收用户提供的 Markdown 文件路径
2. 验证文件存在且为 .md 格式
3. 在 Skill 目录下创建运行目录：runs/{keyword}-{timestamp}/
4. 创建 state/progress.json，记录源文件路径和当前状态
5. 创建 output/ 目录

## 验证检查点

- [ ] 源文件存在且可读
- [ ] runs/ 下生成了运行目录
- [ ] state/progress.json 已创建

## 下一步

→ step02-translate.md