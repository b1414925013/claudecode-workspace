# CronUtil 定时任务调度

`pyhutool.cron.CronUtil` 对齐 Hutool `cn.hutool.cron.CronUtil`，基于
[APScheduler](https://apscheduler.readthedocs.io/) 3.x 提供后台调度器与
类 Quartz cron 表达式任务管理。

## 安装

```bash
pip install "pyhutool[cron]"
```

未安装 `apscheduler` 时调用任何方法都会抛 `UtilError` 提示安装。

## 快速使用

```python
from pyhutool.cron import CronUtil

def job(name: str) -> None:
    print(f"hello {name}")

# 添加任务
CronUtil.schedule("job1", "*/2 * * * *", job, "world")
CronUtil.schedule("job2", "0 9 * * 1-5", job, "weekday")

# 启动调度器（异步，立即返回）
CronUtil.start()

# 查询
CronUtil.is_started()   # True
CronUtil.size()         # 2
CronUtil.get_ids()      # ["job1", "job2"]

# 更新 cron 表达式
CronUtil.update_pattern("job1", "*/5 * * * *")

# 移除
CronUtil.remove("job2")

# 停止调度器（等待正在执行的任务完成）
CronUtil.stop()
```

## Cron 表达式

支持 3 种字段数：

| 字段数 | 含义 | 示例 |
|--------|------|------|
| 5 | `分 时 日 月 周`（Quartz / crontab 默认，无秒） | `0 * * * *` |
| 6 | `秒 分 时 日 月 周` | `0 0 * * * *` |
| 7 | `秒 分 时 日 月 周 年` | `0 0 0 1 1 * 2099` |

字段语义与 Quartz 一致：

| 字段 | 允许值 | 特殊字符 |
|------|--------|----------|
| 秒 | 0-59 | `,` `-` `*` `/` |
| 分 | 0-59 | `,` `-` `*` `/` |
| 时 | 0-23 | `,` `-` `*` `/` |
| 日 | 1-31 | `,` `-` `*` `/` `?` `L` |
| 月 | 1-12 / JAN-DEC | `,` `-` `*` `/` |
| 周 | 0-7 / SUN-SAT | `,` `-` `*` `/` `?` `L` `#` |
| 年 | 1970-2099 | `,` `-` `*` `/` |

## API 参考

| 方法 | 说明 |
|------|------|
| `schedule(id, cron, func, *args, **kwargs)` | 添加任务（ID 重复抛错） |
| `remove(id) -> bool` | 移除任务，返回是否成功 |
| `update_pattern(id, cron)` | 更新任务 cron |
| `start()` / `stop(wait=True)` | 启动 / 停止调度器 |
| `restart()` | 重启（任务清空） |
| `is_started() -> bool` | 调度器状态 |
| `size() -> int` | 任务数量 |
| `get_ids() -> list[str]` | 任务 ID 列表 |
| `clear()` | 清空任务 |

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 底层 | 自研 `Scheduler` | APScheduler 3.x |
| 调度器 | 进程内单例 | 同（`BackgroundScheduler`） |
| cron 表达式 | 6 字段（秒+5） | 5/6/7 字段全支持 |
| 任务 ID | 字符串 | 同 |
| 异常处理 | 任务异常中断 | 任务异常不中断（APScheduler 默认） |
| 依赖 | 内置 | `apscheduler` (extras) |

## 注意事项

- `BackgroundScheduler(daemon=True)`：进程退出时调度线程自动退出；
- 任务异常默认会记录日志但不中断调度器，可在 `func` 内自行 `try/except`；
- `restart()` 会清空已注册任务，因为 APScheduler shutdown 后 scheduler
  对象不能复用，会重建；
- `start()` / `stop()` 均幂等，重复调用不会抛错。
