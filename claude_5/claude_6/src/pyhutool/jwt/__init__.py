"""pyhutool.jwt - JWT 签发与验证模块（依赖 pyjwt）。

对齐 Hutool ``cn.hutool.jwt`` 包，提供 ``JWT`` builder 对象与 ``JWTUtil``
静态工具类。底层基于 [PyJWT](https://pyjwt.readthedocs.io)。

注意：``pyjwt`` 是可选依赖。若未安装，调用本模块任何方法都会抛
``UtilError``，提示用户 ``pip install "pyhutool[jwt]"``。
"""

from pyhutool.jwt.jwt_util import JWT, JWTUtil

__all__ = ["JWT", "JWTUtil"]
