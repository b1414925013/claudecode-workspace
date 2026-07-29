"""pyhutool 统一异常体系。

设计说明
--------
Java Hutool 使用 ``Exception`` 后缀（如 ``HutoolException``、``UtilException``），
遵循 PEP 8 的 Python 约定使用 ``Error`` 后缀。pyhutool 采取混合策略：

- 工具类（``StrUtil`` 等）保留 Hutool 类名语义；
- 异常类采用 Python 习惯的 ``Error`` 后缀，并在文档中标注 Hutool 对应类。

异常层级
--------
- ``PyHutoolError``      ← Hutool ``HutoolException``（所有 pyhutool 异常基类）
    - ``UtilError``      ← Hutool ``UtilException``（工具运行时异常）
    - ``StateError``     ← Hutool ``StateException``（非法状态）
"""

from __future__ import annotations

from typing import Any


class PyHutoolError(Exception):
    """所有 pyhutool 异常的基类。

    对应 Hutool 的 ``cn.hutool.core.exceptions.HutoolException``。

    Parameters
    ----------
    message:
        异常信息。
    cause:
        原始异常（可选），对应 Java 的 cause 链。
    """

    def __init__(self, message: str = "", cause: BaseException | None = None) -> None:
        """初始化 pyhutool 异常实例。"""
        super().__init__(message)
        self.message = message
        self.cause = cause

    def __str__(self) -> str:
        """返回异常的字符串表示。"""
        if self.cause is not None:
            return f"{self.message} [caused by: {type(self.cause).__name__}: {self.cause}]"
        return self.message


class UtilError(PyHutoolError):
    """工具运行时异常。

    对应 Hutool 的 ``cn.hutool.core.exceptions.UtilException``。
    用于表示工具方法执行期间发生的可恢复错误。
    """

    def __init__(self, message: str = "", cause: BaseException | None = None) -> None:
        """初始化工具异常实例。"""
        super().__init__(message, cause)


class StateError(PyHutoolError):
    """非法状态异常。

    对应 Hutool 的 ``cn.hutool.core.exceptions.StateException``。
    用于表示在非法状态下调用了方法，或前置条件不满足。
    """

    def __init__(self, message: str = "", cause: BaseException | None = None) -> None:
        """初始化状态异常实例。"""
        super().__init__(message, cause)


def wrap_as_util_error(func_return: Any, cause: BaseException) -> UtilError:
    """将原始异常包装为 ``UtilError`` 的辅助函数。

    Parameters
    ----------
    func_return:
        预留参数（保持 API 兼容），当前未使用。
    cause:
        原始异常。

    Returns
    -------
    UtilError
        包装后的异常。
    """
    return UtilError(str(cause), cause=cause)
