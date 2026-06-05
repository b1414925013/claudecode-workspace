# Project Development Team（项目开发团队）

## 基本信息

- **名称**: project_development_team
- **描述**: 项目开发团队 - 分层协作，Manager协调多个Worker
- **模式**: hierarchical（分层）

## 团队成员

| Agent | 角色 | 描述 |
|-------|------|------|
| manager | 项目经理 | 负责协调团队工作，分配任务，汇总结果 |
| frontend_dev | 前端开发 | 负责界面开发和用户交互 |
| backend_dev | 后端开发 | 负责API开发和业务逻辑 |
| dba | 数据库专家 | 负责数据库设计和优化 |

## 工作流程

- **类型**: 分层协作
- **描述**: Manager接收任务后，分配给相应的Worker执行，最后汇总结果

### Prompt 模板

**Manager:**
```
协调{workers}完成{task}，汇总他们的工作结果
```

**Worker:**
```
你是一个{role}专家，完成：{task}
```

## 使用示例

```python
# 分层协作：Manager 协调多个 Worker
manager = agent(description="项目经理", prompt="协调前端、后端、数据库专家完成项目", subagent_type="general-purpose")
frontend = agent(description="前端开发", prompt="你是一个前端专家，完成界面开发", subagent_type="general-purpose")
backend = agent(description="后端开发", prompt="你是一个后端专家，完成API开发", subagent_type="general-purpose")
dba = agent(description="数据库专家", prompt="你是一个数据库专家，完成数据库设计", subagent_type="general-purpose")
```