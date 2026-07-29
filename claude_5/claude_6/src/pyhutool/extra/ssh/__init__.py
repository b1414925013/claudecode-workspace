"""pyhutool.extra.ssh - SSH 客户端模块（依赖 paramiko）。

对齐 Hutool ``cn.hutool.extra.ssh`` 包，提供 ``JschUtil`` 静态工具类。
底层基于 [paramiko](https://www.paramiko.org/)。

注意：``paramiko`` 是可选依赖。若未安装，调用本模块任何方法都会抛
``UtilError``，提示用户 ``pip install "pyhutool[ssh]"``。
"""

from pyhutool.extra.ssh.jsch_util import JschUtil

__all__ = ["JschUtil"]
