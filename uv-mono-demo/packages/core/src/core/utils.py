"""core — 底层公共工具函数与类。"""


def add(a: int, b: int) -> int:
    """返回两数之和。"""
    return a + b


def greet(name: str) -> str:
    """返回问候语。"""
    return f"Hello, {name}!"


def celsius_to_fahrenheit(c: float) -> float:
    """摄氏温度转华氏温度。"""
    return round(c * 9.0 / 5.0 + 32.0, 1)


class Provider:
    """演示类依赖的提供者。"""

    def __init__(self, prefix: str = "[core]") -> None:
        self._prefix = prefix

    def announce(self, message: str) -> str:
        return f"{self._prefix} {message}"
