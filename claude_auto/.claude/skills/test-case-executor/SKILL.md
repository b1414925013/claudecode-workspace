---
name: test-case-executor
description: 执行自动化测试用例。根据测试用例定义生成模拟执行结果。当用户需要执行测试用例或模拟测试执行时触发此技能。
---

# Test Case Executor

根据测试用例生成模拟执行结果 JSON。

## 输入格式

```
用例编号: TC-xxx
模块: xxx
功能点: xxx
前置条件: xxx
操作步骤:
1. 步骤1
2. 步骤2
预期结果: xxx
```

## 输出格式

严格 JSON 格式：
```json
{
  "case_id": "TC-xxx",
  "status": "passed|failed|error",
  "actual_result": "实际执行结果描述",
  "error_info": "仅 status 为 failed 或 error 时填写",
  "execution_log": ["步骤1执行日志", "步骤2执行日志"]
}
```

## 规则

1. 根据步骤合理性判断 status：
   - 步骤完整可执行 → `passed`
   - 步骤存在缺陷 → `failed`
   - 步骤无法执行 → `error`
2. 逐步骤生成 execution_log
3. 内部引号使用「」