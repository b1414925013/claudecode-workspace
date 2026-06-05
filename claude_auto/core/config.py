"""配置管理模块 - 从 config.yaml 读取配置信息"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml


class Config:
    """全局配置类（单例），提供类型化配置访问"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._data = self._load()
        self._run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._overridden_run_id: str | None = None

    # ------------------------------------------------------------------
    # 私有方法
    # ------------------------------------------------------------------

    @staticmethod
    def _root() -> Path:
        """项目根目录（core/ 的上一级）"""
        return Path(__file__).resolve().parent.parent

    @staticmethod
    def _load() -> dict:
        config_path = Config._root() / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

    def _path(self, *keys: str, default: str) -> Path:
        """从嵌套字典中取值并拼成项目根目录下的绝对路径"""
        val = self._data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k, {})
            else:
                val = {}
        return self._root() / (val if isinstance(val, str) else default)

    # ------------------------------------------------------------------
    # 运行目录（每次启动自动创建唯一目录）
    # ------------------------------------------------------------------

    @property
    def run_id(self) -> str:
        """当前运行的 ID，格式 run_YYYYMMDD_HHMMSS"""
        if self._overridden_run_id:
            return self._overridden_run_id
        return f"run_{self._run_ts}"

    def set_run_id(self, run_id: str) -> None:
        """指向已有的 run 目录（--report-only 模式用）"""
        self._overridden_run_id = run_id

    @property
    def run_dir(self) -> Path:
        """当前运行的输出根目录 output/run_{timestamp}/"""
        return self._root() / "output" / self.run_id

    # ------------------------------------------------------------------
    # Claude API 配置
    # ------------------------------------------------------------------

    @property
    def api_key(self) -> str:
        return self._data.get("claude", {}).get("api_key", "")

    @property
    def base_url(self) -> str | None:
        """API 基础地址，为空则使用 Anthropic 官方端点"""
        val = self._data.get("claude", {}).get("base_url", "")
        return val.strip() or None

    @property
    def model(self) -> str:
        return self._data.get("claude", {}).get("model", "claude-sonnet-4-20250514")

    @property
    def max_tokens(self) -> int:
        return int(self._data.get("claude", {}).get("max_tokens", 4096))

    @property
    def temperature(self) -> float:
        return float(self._data.get("claude", {}).get("temperature", 0.3))

    # ------------------------------------------------------------------
    # 路径配置
    # ------------------------------------------------------------------

    @property
    def docs_path(self) -> Path:
        return self._path("paths", "docs", default="test_docs")

    @property
    def testcase_output_path(self) -> Path:
        return self.run_dir / "test_cases"

    @property
    def report_output_path(self) -> Path:
        return self.run_dir / "reports"

    @property
    def log_enabled(self) -> bool:
        return bool(self._data.get("logging", {}).get("enabled", True))

    @property
    def log_level(self) -> str:
        return str(self._data.get("logging", {}).get("level", "INFO"))

    # ------------------------------------------------------------------
    # Playwright 配置
    # ------------------------------------------------------------------

    @property
    def pw_base_url(self) -> str:
        return str(self._data.get("playwright", {}).get("base_url", "http://localhost:3000"))

    @property
    def pw_headless(self) -> bool:
        return bool(self._data.get("playwright", {}).get("headless", True))

    @property
    def pw_screenshot_dir(self) -> Path:
        return self.run_dir / "screenshots"

    # ------------------------------------------------------------------
    # 执行策略
    # ------------------------------------------------------------------

    @property
    def execution_mode(self) -> str:
        """auto: 生成后立即执行; manual: 生成后等待确认"""
        return str(self._data.get("execution", {}).get("mode", "auto")).lower()

    @property
    def execution_engine(self) -> str:
        """api: Claude API 模拟执行; playwright: Playwright MCP 真实浏览器"""
        return str(self._data.get("execution", {}).get("engine", "api")).lower()

    # ------------------------------------------------------------------
    # 校验
    # ------------------------------------------------------------------

    def validate(self):
        """启动前校验必要配置项，不通过则抛出 ValueError"""
        errors = []
        if not self.api_key:
            errors.append("config.yaml 中 claude.api_key 未配置")
        if not self.docs_path.exists():
            errors.append(f"文档目录不存在: {self.docs_path}")
        if errors:
            raise ValueError("\n".join(errors))

    # ---------------------------------------------------------------------------
    # CLI
    # ---------------------------------------------------------------------------

    @staticmethod
    def build_cli_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Claude Code 自动化测试工具")
        parser.add_argument("--report-only", action="store_true", help="基于已有执行结果生成报告")
        parser.add_argument("--run", type=str, default="", help="指定历史 run ID（如 run_20260503_143000）")
        return parser

    def resolve_run(self, run_arg: str) -> str | None:
        if run_arg:
            return run_arg
        runs = sorted(self._root().glob("output/run_*"))
        return runs[-1].name if runs else None


# ---------------------------------------------------------------------------
# 日志初始化
# ---------------------------------------------------------------------------

def setup_logging(config: Config) -> None:
    """配置日志：控制台输出 + 文件输出（可选）"""
    # 创建运行目录（含 test_cases / reports / screenshots 子目录）
    for sub in ("test_cases", "reports", "screenshots"):
        (config.run_dir / sub).mkdir(parents=True, exist_ok=True)

    level = getattr(logging, config.log_level.upper(), logging.INFO)

    # 移除 root logger 上已有的 handler，避免 basicConfig 静默失效
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    # 控制台 handler - 用 errors=replace 避免 GBK 编码崩溃
    class _SafeWriter:
        """包装 stdout.write，遇到编码错误用 ? 替换"""
        def write(self, msg):
            try:
                sys.stdout.write(msg)
            except UnicodeEncodeError:
                safe = msg.encode(sys.stdout.encoding, errors="replace").decode(
                    sys.stdout.encoding
                )
                sys.stdout.write(safe)
        def flush(self):
            sys.stdout.flush()

    console = logging.StreamHandler(_SafeWriter())  # type: ignore[arg-type]

    handlers: list[logging.Handler] = [console]

    if config.log_enabled:
        # 运行专属日志
        handlers.append(
            logging.FileHandler(config.run_dir / "run.log", encoding="utf-8")
        )

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s (%(filename)s:%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )
