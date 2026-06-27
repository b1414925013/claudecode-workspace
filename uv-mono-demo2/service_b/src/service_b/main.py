"""service_b — 编排层，同时调用 core 和 service_a。"""

from core import add, greet
from service_a import double_greet, temperature_report


def run() -> None:
    """演示跨两层依赖的调用链。"""
    # 直接调用 core
    print("=== core 直接调用 ===")
    print(f"add(10, 20) = {add(10, 20)}")
    print(greet("service_b"))

    # 调用 service_a（间接调用 core）
    print("\n=== service_a 调用 ===")
    print(double_greet("World"))
    print(temperature_report(100.0))


def summarize(items: list[int]) -> dict:
    """使用 core.add 实现聚合功能。"""
    total = 0
    for v in items:
        total = add(total, v)
    return {"count": len(items), "total": total, "average": total / len(items) if items else 0}


if __name__ == '__main__':
    print(summarize([10, 20, 30, 40, 50]))
