"""pyhutool.cron - 定时任务调度模块（依赖 apscheduler）。

对齐 Hutool ``cn.hutool.cron`` 包，提供 ``CronUtil`` 静态工具类。
底层基于 [APScheduler](https://apscheduler.readthedocs.io/) 3.x。

注意：``apscheduler`` 是可选依赖。若未安装，调用本模块任何方法都会抛
``UtilError``，提示用户 ``pip install "pyhutool[cron]"``。
"""

from pyhutool.cron.cron_util import CronUtil

__all__ = ["CronUtil"]
