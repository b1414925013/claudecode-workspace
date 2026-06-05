# Data Pipeline Team（数据管道团队）

## 基本信息

- **名称**: data_pipeline_team
- **描述**: 数据处理管道团队 - 顺序执行，流水线作业
- **模式**: sequential（顺序）

## 团队成员

| Agent | 描述 | 工具 |
|-------|------|------|
| crawler | 负责从各个数据源爬取原始数据 | web_fetch, bash |
| cleaner | 负责清洗和格式化数据 | bash |
| storage | 负责将数据存入数据库 | bash |

## 工作流程

- **类型**: 顺序执行
- **描述**: 流水线作业：爬取 → 清洗 → 存储
- **输入**: 原始数据源列表
- **输出**: 清洗后存入数据库的数据

## 使用示例

```python
# 顺序执行：先爬取，再清洗，最后存储
crawler = agent(description="爬虫", prompt="爬取数据", subagent_type="general-purpose")
cleaner = agent(description="清洗", prompt="清洗数据", subagent_type="general-purpose")
storage = agent(description="存储", prompt="存储数据", subagent_type="general-purpose")
```