"""异常体系单元测试。"""

from __future__ import annotations

import pytest

from pyhutool.core import PyHutoolError, StateError, UtilError
from pyhutool.core.exceptions import wrap_as_util_error


def test_pyhutool_error_basic() -> None:
    err = PyHutoolError("boom")
    assert err.message == "boom"
    assert err.cause is None
    assert str(err) == "boom"


def test_pyhutool_error_with_cause() -> None:
    cause = ValueError("root")
    err = PyHutoolError("surface", cause=cause)
    assert err.cause is cause
    assert "ValueError" in str(err)
    assert "root" in str(err)


def test_util_error_inherits() -> None:
    assert issubclass(UtilError, PyHutoolError)
    err = UtilError("util fail")
    assert isinstance(err, PyHutoolError)


def test_state_error_inherits() -> None:
    assert issubclass(StateError, PyHutoolError)
    err = StateError("bad state", cause=RuntimeError("inner"))
    assert err.cause is not None
    assert str(err).startswith("bad state")


def test_wrap_as_util_error() -> None:
    cause = KeyError("missing")
    wrapped = wrap_as_util_error(None, cause)
    assert isinstance(wrapped, UtilError)
    assert wrapped.cause is cause


def test_raise_and_catch() -> None:
    with pytest.raises(PyHutoolError):
        raise UtilError("x")
