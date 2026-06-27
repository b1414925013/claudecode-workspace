"""service_a — 业务逻辑层，演示跨包调用 core。"""

from core import add, celsius_to_fahrenheit, Provider


def double_greet(name: str) -> str:
    """调用 core.greet() 两次，返回拼接结果。"""
    p = Provider("[service-a]")
    first = p.announce(f"greeting {name} once")
    second = p.announce(f"greeting {name} again")
    return f"{first}\n{second}"


def temperature_report(celsius: float) -> str:
    """将摄氏温度列表转为华氏温度报告，演示跨包数值计算。"""
    f = celsius_to_fahrenheit(celsius)
    return f"{celsius}°C = {f}°F"
