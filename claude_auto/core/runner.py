"""测试流程运行器 - 封装完整业务流程"""

import json
import logging
import sys
from pathlib import Path

from core.config import Config, setup_logging
from core.doc_parser import DocParser
from core.claude_client import ClaudeClient
from core.testcase_generator import TestCaseGenerator, execute_test_cases
from core.reporter import generate_report, print_summary
from core.playwright_executor import build_plan, save_plan, execute_plan, load_results

logger = logging.getLogger("runner")


class Runner:
    """自动化测试流程运行器"""

    def __init__(self):
        self.config = Config()
        setup_logging(self.config)
        self.config.validate()
        self.client: ClaudeClient | None = None

    # ---------------------------------------------------------------------------
    # 入口
    # ---------------------------------------------------------------------------

    def run(self, args) -> None:
        """根据命令行参数执行对应流程"""
        engine = self.config.execution_engine
        mode = self.config.execution_mode

        logger.info("=" * 50)
        logger.info("Claude Code 自动化测试工具")
        logger.info("输出: output/%s    引擎: %s    模式: %s", self.config.run_id, engine, mode)
        logger.info("=" * 50)

        if args.report_only:
            self._run_report_only(args.run)
        else:
            self._run_full(args)

    # ---------------------------------------------------------------------------
    # 报��模式
    # ---------------------------------------------------------------------------

    def _run_report_only(self, run_arg: str) -> None:
        run_id = self.config.resolve_run(run_arg)
        if not run_id:
            logger.error("未找到历史 run 目录")
            sys.exit(1)
        self.config.set_run_id(run_id)
        logger.info("使用历史 run: output/%s", run_id)

        results = load_results(self.config.testcase_output_path)
        if results is None:
            sys.exit(1)

        plan_path = self.config.testcase_output_path / "playwright_plan.json"
        if plan_path.exists():
            with open(plan_path, encoding="utf-8") as f:
                plan = json.load(f)
            test_cases = [{
                "case_id": c["case_id"], "module": c["module"],
                "feature": c["feature"], "precondition": c.get("precondition", ""),
                "steps": [s.get("description", str(s)) for s in c.get("browser_steps", [])],
                "expected": c.get("expected", ""), "priority": c.get("priority", ""),
            } for c in plan.get("test_cases", [])]
        else:
            test_cases = []

        generate_report(test_cases, results, self.config.report_output_path,
                        screenshot_base=self.config.pw_screenshot_dir
                        if self.config.execution_engine == "playwright" else None)
        print_summary(results)

    # ---------------------------------------------------------------------------
    # 完整流程
    # ---------------------------------------------------------------------------

    def _run_full(self, args) -> None:
        # 1. 解析文档
        logger.info("")
        logger.info("[1/4] 解析文档...")
        parser = DocParser(self.config.docs_path)
        documents = parser.parse_all()
        if not documents:
            logger.error("没有可解析的文档")
            sys.exit(1)

        # 2. 生成测试用例
        logger.info("")
        logger.info("[2/4] 生成测试用例...")
        self.client = ClaudeClient(
            api_key=self.config.api_key,
            model=self.config.model,
            timeout=120,
        )
        generator = TestCaseGenerator(self.client, self.config.testcase_output_path)
        test_cases = generator.generate(documents)
        if not test_cases:
            logger.error("没有生成测试用例")
            sys.exit(1)
        generator.save(test_cases)

        # 3. 构建浏览器计划
        plan = None
        if self.config.execution_engine == "playwright":
            logger.info("")
            logger.info("  生成浏览器操作计划...")
            plan = build_plan(test_cases, self.config.pw_base_url,
                              screenshot_dir=str(self.config.pw_screenshot_dir))
            save_plan(plan, self.config.testcase_output_path)

        # 4. manual 模式
        if self.config.execution_mode == "manual":
            self._wait_manual_confirm()

        # 5. 执行测试
        results = self._execute_tests(plan, test_cases)

        # 6. 生成报告
        logger.info("")
        logger.info("[4/4] 生成测试报告...")
        generate_report(test_cases, results, self.config.report_output_path,
                        screenshot_base=self.config.pw_screenshot_dir
                        if self.config.execution_engine == "playwright" else None)
        print_summary(results)
        logger.info("所有任务完成！输出目录: output/%s", self.config.run_id)

    # ---------------------------------------------------------------------------
    # 内部方法
    # ---------------------------------------------------------------------------

    def _wait_manual_confirm(self) -> None:
        logger.info("")
        logger.info("=" * 50)
        logger.info("测试用例已生成至: output/%s/test_cases/", self.config.run_id)
        logger.info("请审阅后确认是否继续执行")
        logger.info("=" * 50)
        try:
            answer = input("  继续执行测试？(y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = "n"
        if answer != "y":
            logger.info("已取消执行，测试用例已保存")
            sys.exit(0)

    def _execute_tests(self, plan, test_cases):
        logger.info("")
        if self.config.execution_engine == "playwright":
            logger.info("[3/4] 通过 Playwright MCP 执行测试...")
            server_cmd = ["npx.cmd", "@playwright/mcp"]
            if self.config.pw_headless:
                server_cmd.append("--headless")
            logger.info("启动 MCP 服务器 (%s)", "无头模式" if self.config.pw_headless else "有头模式")
            return execute_plan(plan, screenshot_dir=str(self.config.pw_screenshot_dir),
                                server_cmd=server_cmd, output_dir=self.config.testcase_output_path)
        else:
            logger.info("[3/4] 通过 Claude API 执行测试...")
            return execute_test_cases(self.client, test_cases)