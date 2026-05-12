# Step 02 - 翻译输出

- 执行者：SubAgent（general-purpose）
- 输入：源文件路径（从 state/progress.json 读取）
- 输出：output/translated.md

## 执行说明

启动 SubAgent，传入以下 Prompt：

> 你是专业的英中翻译专家。
>
> 请读取 {input_path} 文件，将其翻译为简体中文。
>
> 翻译要求：
> 1. 保留所有 Markdown 格式（标题、列表、代码块、链接）
> 2. 技术术语保留英文原文，括号标注中文
> 3. 译文自然流畅，不要翻译腔
>
> 将翻译结果写入 {output_path}/translated.md
>
> 完成后只返回一行：翻译完成，共 N 段，输出路径：{output_path}/translated.md

## 验证检查点

- [ ] output/translated.md 存在且非空
- [ ] 文件是合法的 Markdown 格式
- [ ] 标题层级与原文一致

## 下一步

工作流结束。向用户报告输出路径。