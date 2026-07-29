"""ID 生成工具。

对齐 Hutool 的 ``cn.hutool.core.util.IdUtil``，提供 UUID、ObjectId、NanoId 等唯一标识生成。
"""

from __future__ import annotations

import os
import threading
import time
import uuid as _uuid
from typing import Any

__all__ = ["IdUtil"]

# NanoId 默认字母表（URL 安全）
_NANO_ALPHABET = "_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_NANO_DEFAULT_SIZE = 21

# ObjectId 计数器（进程级自增）
_object_id_counter_lock = threading.Lock()
_object_id_counter: int = 0


class IdUtil:
    """ID 生成工具类，全部为静态方法。"""

    # ------------------------------------------------------------------
    # UUID
    # ------------------------------------------------------------------
    @staticmethod
    def random_uuid() -> str:
        """返回带连字符的标准 UUID（36 位）。"""
        return str(_uuid.uuid4())

    @staticmethod
    def simple_uuid() -> str:
        """返回不带连字符的简化 UUID（32 位），对应 Hutool ``simpleUUID``。"""
        return str(_uuid.uuid4()).replace("-", "")

    @staticmethod
    def fast_uuid() -> str:
        """返回不带连字符的 UUID（对应 Hutool ``fastUUID``，Python 内部即 ``uuid4``）。"""
        return IdUtil.simple_uuid()

    @staticmethod
    def ordered_uuid() -> str:
        """返回有序 UUID（UUIDv1），用于可排序场景。"""
        return str(_uuid.uuid1())

    # ------------------------------------------------------------------
    # ObjectId（MongoDB 风格 24 位十六进制）
    # ------------------------------------------------------------------
    @staticmethod
    def object_id() -> str:
        """生成 24 位 MongoDB 风格 ObjectId 字符串。

        结构：4 字节时间戳 + 5 字节随机 + 3 字节自增计数器。
        """
        global _object_id_counter
        timestamp = int(time.time()).to_bytes(4, "big")
        random_bytes = os.urandom(5)
        with _object_id_counter_lock:
            counter = _object_id_counter
            _object_id_counter = (_object_id_counter + 1) & 0xFFFFFF
        counter_bytes = counter.to_bytes(3, "big")
        return (timestamp + random_bytes + counter_bytes).hex()

    # ------------------------------------------------------------------
    # NanoId
    # ------------------------------------------------------------------
    @staticmethod
    def nano_id(size: int = _NANO_DEFAULT_SIZE) -> str:
        """生成 NanoId 风格随机字符串（默认 21 位，URL 安全）。"""
        if size <= 0:
            return ""
        alphabet = _NANO_ALPHABET
        # 使用系统随机数保证不可预测
        mask = (1 << (len(alphabet).bit_length())) - 1
        out: list[str] = []
        while len(out) < size:
            chunk = os.urandom(4)
            n = int.from_bytes(chunk, "big") & mask
            if n < len(alphabet):
                out.append(alphabet[n])
        return "".join(out)

    # ------------------------------------------------------------------
    # 雪花 ID（简化版，单机自增）
    # ------------------------------------------------------------------
    @staticmethod
    def snowflake_id(worker_id: int = 0, data_center_id: int = 0) -> int:
        """生成简化版雪花 ID（64 位整数）。

        结构：1 位符号 + 41 位时间戳 + 5 位 dataCenterId + 5 位 workerId + 12 位序列号。
        单机内线程安全，与 Hutool 完整雪花算法语义接近。
        """
        if not (0 <= worker_id < 32):
            raise ValueError("worker_id 范围 0-31")
        if not (0 <= data_center_id < 32):
            raise ValueError("data_center_id 范围 0-31")

        twepoch = 1_577_836_800_000  # 2020-01-01 UTC 毫秒
        now = int(time.time() * 1000)
        timestamp = now - twepoch

        global _object_id_counter
        with _object_id_counter_lock:
            seq = _object_id_counter & 0xFFF
            _object_id_counter = (_object_id_counter + 1) & 0xFFF

        snowflake = (timestamp & ((1 << 41) - 1)) << 22
        snowflake |= (data_center_id & 0x1F) << 17
        snowflake |= (worker_id & 0x1F) << 12
        snowflake |= seq
        return snowflake

    @staticmethod
    def to_string(id_value: Any) -> str:
        """将任意 ID 转为字符串。"""
        return str(id_value)
