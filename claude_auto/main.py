"""Claude Code 自动化测试工具 — 主入口"""

from core.runner import Runner
from core.config import Config


def main() -> None:
    args = Config.build_cli_parser().parse_args()
    runner = Runner()
    runner.run(args)


if __name__ == "__main__":
    main()
