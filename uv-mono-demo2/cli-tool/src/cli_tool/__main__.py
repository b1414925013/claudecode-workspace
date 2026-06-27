"""cli-tool — 可执行的命令行入口。

运行方式：
    uv run --package cli-tool python -m cli_tool
"""

from service_b import run, summarize


def main() -> None:
    print("=" * 40)
    print("  CLI Tool — 演示完整调用链路")
    print("=" * 40)

    run()

    print("\n=== summarize 聚合演示 ===")
    data = [3, 7, 10, 15]
    result = summarize(data)
    print(f"items={data} => {result}")


if __name__ == "__main__":
    main()
