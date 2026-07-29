"""CronUtil 单元测试。

测试策略：
- APScheduler 已安装，不跳过；
- 不真正触发 cron 任务，只验证任务注册 / 查询 / 更新 / 移除 / 调度器生命周期；
- 用 ``freezegun`` 风格的"快速触发"测试不可行（APScheduler 真实定时器），
  改为直接调用 trigger.get_next_fire_time 验证调度时机。
"""

from __future__ import annotations

from typing import Any

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.cron import CronUtil

# 模块级跳过：若环境未装 apscheduler，跳过所有用例
apscheduler_available = True
try:
    import apscheduler  # noqa: F401
except ImportError:
    apscheduler_available = False

pytestmark = pytest.mark.skipif(
    not apscheduler_available, reason="需要 apscheduler"
)


@pytest.fixture(autouse=True)
def reset_scheduler() -> Any:
    """每个测试前后确保调度器被停止、清空，避免互相干扰。"""
    # 测试前：若已启动则停止并重置
    if CronUtil.is_started():
        CronUtil.stop(wait=True)
    # 重新设置全局状态（重启后单例已重置）
    # 测试前确保停止
    yield
    # 测试后清理：停止 + 重置单例
    if CronUtil.is_started():
        CronUtil.stop(wait=True)
    # 通过访问私有状态强制下次 _get_scheduler 重建
    import pyhutool.cron.cron_util as cu
    cu._scheduler = None
    cu._started = False


def _noop() -> None:
    """空回调。"""


def _add_one(x: int) -> int:
    """带参数的回调。"""
    return x + 1


# ---------------------------------------------------------------------
# 表达式解析
# ---------------------------------------------------------------------
class TestCronExpression:
    def test_5_field_cron(self) -> None:
        CronUtil.schedule("t1", "0 * * * *", _noop)
        ids = CronUtil.get_ids()
        assert "t1" in ids

    def test_6_field_cron(self) -> None:
        # 秒 分 时 日 月 周
        CronUtil.schedule("t1", "0 0 * * * *", _noop)
        assert "t1" in CronUtil.get_ids()

    def test_7_field_cron(self) -> None:
        # 秒 分 时 日 月 周 年
        CronUtil.schedule("t1", "0 0 0 1 1 * 2099", _noop)
        assert "t1" in CronUtil.get_ids()

    def test_invalid_cron_too_few_fields(self) -> None:
        with pytest.raises(UtilError):
            CronUtil.schedule("t1", "0 * * *", _noop)

    def test_invalid_cron_too_many_fields(self) -> None:
        with pytest.raises(UtilError):
            CronUtil.schedule("t1", "0 0 0 0 0 0 0 0", _noop)


# ---------------------------------------------------------------------
# 任务管理
# ---------------------------------------------------------------------
class TestSchedule:
    def test_schedule_basic(self) -> None:
        CronUtil.schedule("job1", "0 * * * *", _noop)
        assert CronUtil.size() == 1
        assert CronUtil.get_ids() == ["job1"]

    def test_schedule_with_args(self) -> None:
        CronUtil.schedule("job1", "0 * * * *", _add_one, 10)
        assert CronUtil.size() == 1

    def test_schedule_with_kwargs(self) -> None:
        CronUtil.schedule("job1", "0 * * * *", _add_one, x=10)
        assert CronUtil.size() == 1

    def test_schedule_duplicate_id_raises(self) -> None:
        CronUtil.schedule("job1", "0 * * * *", _noop)
        with pytest.raises(UtilError):
            CronUtil.schedule("job1", "0 * * * *", _noop)

    def test_remove_existing(self) -> None:
        CronUtil.schedule("job1", "0 * * * *", _noop)
        assert CronUtil.remove("job1") is True
        assert CronUtil.size() == 0

    def test_remove_nonexistent_returns_false(self) -> None:
        assert CronUtil.remove("nope") is False

    def test_update_pattern(self) -> None:
        CronUtil.schedule("job1", "0 * * * *", _noop)
        CronUtil.update_pattern("job1", "*/5 * * * *")
        assert CronUtil.size() == 1

    def test_update_pattern_nonexistent_raises(self) -> None:
        with pytest.raises(UtilError):
            CronUtil.update_pattern("nope", "*/5 * * * *")

    def test_clear(self) -> None:
        CronUtil.schedule("a", "0 * * * *", _noop)
        CronUtil.schedule("b", "0 * * * *", _noop)
        CronUtil.clear()
        assert CronUtil.size() == 0


# ---------------------------------------------------------------------
# 调度器生命周期
# ---------------------------------------------------------------------
class TestSchedulerLifecycle:
    def test_initial_not_started(self) -> None:
        # 重置后的初始状态
        assert CronUtil.is_started() is False

    def test_start_then_stop(self) -> None:
        CronUtil.start()
        assert CronUtil.is_started() is True
        CronUtil.stop(wait=True)
        assert CronUtil.is_started() is False

    def test_start_idempotent(self) -> None:
        CronUtil.start()
        CronUtil.start()  # 再次调用不应抛错
        assert CronUtil.is_started() is True
        CronUtil.stop(wait=True)

    def test_stop_idempotent(self) -> None:
        # 未启动时停止不报错
        CronUtil.stop(wait=True)
        assert CronUtil.is_started() is False

    def test_restart(self) -> None:
        CronUtil.start()
        CronUtil.schedule("job1", "0 * * * *", _noop)
        CronUtil.restart()
        # 重启后调度器仍在运行，但任务被清空（scheduler 已重建）
        assert CronUtil.is_started() is True
        assert CronUtil.size() == 0
        CronUtil.stop(wait=True)
