"""Claude API 客户端 - 通过 Claude Code CLI 生成测试用例"""

import json
import re
import subprocess
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Claude 客户端，通过 Claude Code CLI 生成测试用例"""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "MiniMax-M2.7",
        timeout: int = 120,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def generate_test_cases(self, doc_content: str, filename: str) -> List[Dict[str, Any]]:
        """根据文档内容生成测试用例（通过 Claude Code CLI）"""
        prompt = self._build_generation_prompt(doc_content, filename)
        response = self._call_claude(prompt)
        return self._parse_json_array(response)

    def execute_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个测试用例"""
        prompt = self._build_execution_prompt(test_case)
        response = self._call_claude(prompt)
        return self._parse_json_object(response)

    def _call_claude(self, prompt: str) -> str:
        """通过 Claude Code CLI 调用"""
        import platform
        env = {}
        if self.api_key:
            env["ANTHROPIC_API_KEY"] = self.api_key

        claude_cmd = "claude.cmd" if platform.system() == "Windows" else "claude"
        cmd = [
            claude_cmd,
            "--print",
            "--output-format", "json",
            "--dangerously-skip-permissions",
            "--model", self.model,
            "--system-prompt", "你是一个测试专家。根据用户输入的 /test-case-generator 或 /test-case-executor skill 指令生成测试用例或执行结果。输出必须是纯 JSON，不包含额外说明文字。"
        ]

        logger.info("调用 Claude CLI: %s", " ".join(cmd))
        logger.debug("Prompt 内容:\n%s", prompt)

        result = subprocess.run(
            cmd,
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=self.timeout,
            env={**subprocess.os.environ, **env} if env else None,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI 失败: {result.stderr.decode('utf-8', errors='replace')}")

        data = json.loads(result.stdout)
        return data.get("result", "")

    # ------------------------------------------------------------------
    # Prompt 构建
    # ------------------------------------------------------------------

    @staticmethod
    def _build_generation_prompt(content: str, filename: str) -> str:
        truncated = content[:4_000]
        if len(content) > 8_000:
            logger.info("文档内容超过 8000 字符，已截断")

        return f"""/test-case-generator

文档名称: {filename}
文档内容:
{truncated}"""

    @staticmethod
    def _build_execution_prompt(tc: Dict[str, Any]) -> str:
        steps = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(tc.get("steps", [])))
        return f"""/test-case-executor

用例编号: {tc.get('case_id', 'N/A')}
模块: {tc.get('module', 'N/A')}
功能点: {tc.get('feature', 'N/A')}
前置条件: {tc.get('precondition', '无')}
操作步骤:
{steps}
预期结果: {tc.get('expected', 'N/A')}"""

    # ------------------------------------------------------------------
    # 响应解析
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_json_block(text: str) -> str:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        return match.group(1).strip() if match else text.strip()

    @classmethod
    def _parse_json_array(cls, text: str) -> List[Dict[str, Any]]:
        body = cls._extract_json_block(text)
        result = cls._try_parse_json(body, "[", "]")
        if result is not None:
            return result
        raise ValueError(f"无法从响应中解析 JSON 数组:\n{text[:600]}")

    @classmethod
    def _parse_json_object(cls, text: str) -> Dict[str, Any]:
        body = cls._extract_json_block(text)
        result = cls._try_parse_json(body, "{", "}")
        if result is not None:
            return result
        raise ValueError(f"无法从响应中解析 JSON 对象:\n{text[:600]}")

    @staticmethod
    def _try_parse_json(text: str, open_br: str, close_br: str) -> Any | None:
        import re as _re

        start = text.find(open_br)
        if start == -1:
            return None
        end = text.rfind(close_br)
        if end <= start:
            return None
        raw = text[start:end + 1]

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        def _repair_cjk_quotes(s: str) -> str:
            s = _re.sub(r'([一-鿿㐀-䶿＀-￯])"', r'\1「', s)
            s = _re.sub(r'"([一-鿿㐀-䶿＀-￯])', r'」\1', s)
            return s

        try:
            fixed = _repair_cjk_quotes(raw)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        def _repair_bracket_quotes(s: str) -> str:
            has_standard_quotes = bool(_re.search(r'"\w+"\s*:', s))

            if not has_standard_quotes:
                result = []
                depth = 0
                for ch in s:
                    if ch == "「":
                        if depth == 0:
                            result.append('"')
                        else:
                            result.append("「")
                        depth += 1
                    elif ch == "」":
                        depth -= 1
                        if depth == 0:
                            result.append('"')
                        else:
                            result.append("」")
                    else:
                        result.append(ch)
                s = "".join(result)
                s = _re.sub(r'([{,])\s*([a-zA-Z_]\w*)\s*:', lambda m: f'{m.group(1)}"{m.group(2)}":', s)
            else:
                s = _repair_cjk_quotes(s)
            return s

        try:
            fixed2 = _repair_bracket_quotes(raw)
            return json.loads(fixed2)
        except json.JSONDecodeError:
            pass

        for trim in range(1, min(len(raw) - 2, 200)):
            candidate = raw[:len(raw) - trim].rstrip()
            if not candidate.endswith(close_br):
                continue
            for fixer in (None, _repair_cjk_quotes, _repair_bracket_quotes):
                try:
                    return json.loads(fixer(candidate) if fixer else candidate)
                except (json.JSONDecodeError, TypeError):
                    continue

        return None

    @staticmethod
    def _extract_balanced(text: str, open_bracket: str, close_bracket: str) -> str | None:
        start = text.find(open_bracket)
        if start == -1:
            return None
        depth = 0
        in_str = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch == open_bracket:
                depth += 1
            elif ch == close_bracket:
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
        return None