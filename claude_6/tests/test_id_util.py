"""IdUtil 单元测试。"""

from __future__ import annotations

import re

import pytest

from pyhutool.core import IdUtil


class TestUUID:
    """UUID。"""

    def test_random_uuid(self) -> None:
        u = IdUtil.random_uuid()
        assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", u)

    def test_simple_uuid(self) -> None:
        u = IdUtil.simple_uuid()
        assert len(u) == 32
        assert "-" not in u

    def test_fast_uuid(self) -> None:
        u = IdUtil.fast_uuid()
        assert len(u) == 32

    def test_ordered_uuid(self) -> None:
        u = IdUtil.ordered_uuid()
        assert len(u) == 36

    def test_uuid_uniqueness(self) -> None:
        assert IdUtil.random_uuid() != IdUtil.random_uuid()
        assert IdUtil.simple_uuid() != IdUtil.simple_uuid()


class TestObjectId:
    """ObjectId。"""

    def test_object_id_format(self) -> None:
        oid = IdUtil.object_id()
        assert len(oid) == 24
        assert re.fullmatch(r"[0-9a-f]{24}", oid) is not None

    def test_object_id_increasing_prefix(self) -> None:
        """同一秒内前 8 位（时间戳）应相同。"""
        a = IdUtil.object_id()
        b = IdUtil.object_id()
        assert a[:8] == b[:8]

    def test_object_id_unique(self) -> None:
        ids = {IdUtil.object_id() for _ in range(100)}
        assert len(ids) == 100


class TestNanoId:
    """NanoId。"""

    def test_nano_id_default_size(self) -> None:
        s = IdUtil.nano_id()
        assert len(s) == 21

    def test_nano_id_custom_size(self) -> None:
        assert len(IdUtil.nano_id(10)) == 10
        assert IdUtil.nano_id(0) == ""
        assert IdUtil.nano_id(-1) == ""

    def test_nano_id_alphabet(self) -> None:
        allowed = set("_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        s = IdUtil.nano_id(50)
        assert set(s) <= allowed

    def test_nano_id_unique(self) -> None:
        ids = {IdUtil.nano_id() for _ in range(100)}
        assert len(ids) == 100


class TestSnowflake:
    """雪花 ID。"""

    def test_snowflake_id_unique(self) -> None:
        ids = [IdUtil.snowflake_id(1, 1) for _ in range(100)]
        assert len(set(ids)) == 100

    def test_snowflake_id_positive(self) -> None:
        assert IdUtil.snowflake_id(0, 0) > 0

    def test_snowflake_invalid_worker(self) -> None:
        with pytest.raises(ValueError):
            IdUtil.snowflake_id(32, 0)

    def test_snowflake_invalid_data_center(self) -> None:
        with pytest.raises(ValueError):
            IdUtil.snowflake_id(0, 32)


def test_to_string() -> None:
    assert IdUtil.to_string(123) == "123"
    assert IdUtil.to_string("abc") == "abc"
