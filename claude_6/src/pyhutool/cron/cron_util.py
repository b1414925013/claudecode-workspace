"""Cron 定时任务调度工具。

对齐 Hutool 的 ``cn.hutool.cron.CronUtil``，基于
[APScheduler 3.x](https://apscheduler.readthedocs.io/) 提供后台调度器与
类 Quartz cron 表达式任务管理。

设计说明
--------
- ``APScheduler`` 是可选依赖；未安装时调用任何方法抛 ``UtilError``；
- 调度器是进程内单例（``BackgroundScheduler``），首次调用
  :meth:`CronUtil.schedule` 时自动创建；
- 任务 ID 必须唯一；重复添加同 ID 会抛 ``UtilError``；
- cron 表达式采用 6/7 字段格式（秒 分 时 日 月 周 [年]），与 Quartz /
  Hutool 一致；
- 任务异常默认会记录日志但不中断调度器（APScheduler 默认行为）；
- ``start()`` 是异步启动，立即返回；调度在后台线程执行。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from pyhutool.core.exceptions import UtilError

__all__ = ["CronUtil"]

_scheduler: Any = None
_started: bool = False


def _require_apscheduler() -> Any:
    """惰性导入 ``APScheduler``；未安装时抛 ``UtilError``。"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError as e:
        raise UtilError(
            "pyhutool.cron 需要 apscheduler 支持，"
            "请运行：pip install 'pyhutool[cron]'",
            cause=e,
        ) from e
    return {
        "BackgroundScheduler": BackgroundScheduler,
        "CronTrigger": CronTrigger,
    }


def _get_scheduler() -> Any:
    """获取或惰性创建单例调度器。"""
    global _scheduler
    if _scheduler is None:
        mods = _require_apscheduler()
        BackgroundScheduler = mods["BackgroundScheduler"]
        _scheduler = BackgroundScheduler(daemon=True)
    return _scheduler


def _convert_cron(cron: str) -> Any:
    """把字符串 cron 表达式转换为 ``CronTrigger``。

    支持三种形式：
    - 5 字段：``分 时 日 月 周``（Quartz / crontab 默认，无秒）
    - 6 字段：``秒 分 时 日 月 周``
    - 7 字段：``秒 分 时 日 月 周 年``
    """
    mods = _require_apscheduler()
    CronTrigger = mods["CronTrigger"]
    fields = cron.split()
    if len(fields) == 5:
        # 5 字段直接用 from_crontab
        return CronTrigger.from_crontab(cron)
    if len(fields) == 6:
        return CronTrigger(
            second=fields[0],
            minute=fields[1],
            hour=fields[2],
            day=fields[3],
            month=fields[4],
            day_of_week=fields[5],
        )
    if len(fields) == 7:
        return CronTrigger(
            second=fields[0],
            minute=fields[1],
            hour=fields[2],
            day=fields[3],
            month=fields[4],
            day_of_week=fields[5],
            year=fields[6],
        )
    raise UtilError(
        f"无效的 cron 表达式（应为 5/6/7 字段）: {cron!r}"
    )


class CronUtil:
    """Cron 调度工具类，全部为静态方法。

    对应 Hutool ``cn.hutool.cron.CronUtil``。底层基于 APScheduler
    ``BackgroundScheduler``，任务在后台线程执行。
    """

    # ------------------------------------------------------------------
    # 任务管理
    # ------------------------------------------------------------------
    @staticmethod
    def schedule(
        id: str,
        cron: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """添加定时任务。

        Parameters
        ----------
        id:
            任务唯一标识。已存在同 ID 会抛 ``UtilError``。
        cron:
            cron 表达式（5/6/7 字段）。
            - 5 字段：``分 时 日 月 周``（Quartz 默认，无秒）
            - 6 字段：``秒 分 时 日 月 周``
            - 7 字段：``秒 分 时 日 月 周 年``
        func:
            待执行的回调函数。
        *args / **kwargs:
            回调参数。
        """
        sched = _get_scheduler()
        if sched.get_job(id) is not None:
            raise UtilError(f"任务 ID 已存在: {id!r}")
        trigger = _convert_cron(cron)
        try:
            sched.add_job(
                func,
                trigger=trigger,
                args=args,
                kwargs=kwargs,
                id=id,
                name=id,
                replace_existing=False,
            )
        except Exception as e:
            raise UtilError(f"添加任务失败: {e}", cause=e) from e

    @staticmethod
    def remove(id: str) -> bool:
        """移除任务。返回是否成功移除。"""
        sched = _get_scheduler()
        if sched.get_job(id) is None:
            return False
        try:
            sched.remove_job(id)
        except Exception as e:
            raise UtilError(f"移除任务失败: {e}", cause=e) from e
        return True

    @staticmethod
    def update_pattern(id: str, cron: str) -> None:
        """更新已存在任务的 cron 表达式。"""
        sched = _get_scheduler()
        if sched.get_job(id) is None:
            raise UtilError(f"任务不存在: {id!r}")
        trigger = _convert_cron(cron)
        try:
            sched.reschedule_job(id, trigger=trigger)
        except Exception as e:
            raise UtilError(f"更新任务 cron 失败: {e}", cause=e) from e

    # ------------------------------------------------------------------
    # 调度器控制
    # ------------------------------------------------------------------
    @staticmethod
    def start() -> None:
        """启动调度器（异步，立即返回）。"""
        global _started
        sched = _get_scheduler()
        if _started:
            return
        try:
            sched.start()
            _started = True
        except Exception as e:
            raise UtilError(f"启动调度器失败: {e}", cause=e) from e

    @staticmethod
    def stop(wait: bool = True) -> None:
        """停止调度器。``wait=True`` 等待正在执行的任务完成。"""
        global _started
        if not _started:
            return
        sched = _get_scheduler()
        try:
            sched.shutdown(wait=wait)
        except Exception as e:
            raise UtilError(f"停止调度器失败: {e}", cause=e) from e
        _started = False

    @staticmethod
    def restart() -> None:
        """重启调度器。"""
        CronUtil.stop(wait=True)
        # 重新创建调度器（旧的已 shutdown，不能复用）
        global _scheduler, _started
        _scheduler = None
        _started = False
        CronUtil.start()

    @staticmethod
    def is_started() -> bool:
        """调度器是否已启动。"""
        return _started

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    @staticmethod
    def size() -> int:
        """返回当前已注册任务数。"""
        sched = _get_scheduler()
        return len(sched.get_jobs())

    @staticmethod
    def get_ids() -> list[str]:
        """返回所有任务 ID 列表。"""
        sched = _get_scheduler()
        return [cast(str, job.id) for job in sched.get_jobs()]

    @staticmethod
    def clear() -> None:
        """清空所有任务（不停止调度器）。"""
        sched = _get_scheduler()
        try:
            for job in sched.get_jobs():
                sched.remove_job(cast(str, job.id))
        except Exception as e:
            raise UtilError(f"清空任务失败: {e}", cause=e) from e
