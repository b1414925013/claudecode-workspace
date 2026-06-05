"""Playwright MCP 测试计划 —— 将测试用例转为 MCP 可执行操作"""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Playwright MCP 工具映射（参数格式见 _format_mcp_args）
_MCP_ACTIONS: dict[str, str] = {
    "navigate": "browser_navigate",
    "fill": "browser_type",
    "click": "browser_click",
    "press_key": "browser_press_key",
    "assert": "browser_snapshot",
    "check": "browser_click",
    "wait": "browser_wait_for",
    "screenshot": "browser_take_screenshot",
}

# 自然语言 → 动作类型映射
_ACTION_KEYWORDS: dict[str, str] = {
    "打开": "navigate",
    "访问": "navigate",
    "跳转": "navigate",
    "输入": "fill",
    "填写": "fill",
    "键入": "fill",
    "点击": "click",
    "单击": "click",
    "选择": "click",
    "勾选": "check",
    "回车": "press_key",
    "按下": "press_key",
    "等待": "wait",
    "验证": "assert",
    "断言": "assert",
    "检查": "assert",
    "确认": "assert",
}


# ---------------------------------------------------------------------------
# 计划生成
# ---------------------------------------------------------------------------

def build_plan(
    test_cases: List[Dict[str, Any]],
    base_url: str,
    screenshot_dir: str = "output/screenshots",
) -> Dict[str, Any]:
    """将测试用例转为 MCP 可执行的浏览器操作计划"""
    plan: Dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "target_url": base_url.rstrip("/"),
        "screenshot_dir": screenshot_dir,
        "test_cases": [],
    }
    for tc in test_cases:
        browser_steps: List[Dict[str, Any]] = []
        for step_text in tc.get("steps", []):
            step = _parse_step(step_text, base_url)
            step["mcp_tool"] = _MCP_ACTIONS.get(step["action"], "")
            browser_steps.append(step)
        plan["test_cases"].append({
            "case_id": tc.get("case_id", ""),
            "module": tc.get("module", ""),
            "feature": tc.get("feature", ""),
            "precondition": tc.get("precondition", ""),
            "expected": tc.get("expected", ""),
            "priority": tc.get("priority", ""),
            "browser_steps": browser_steps,
        })
    return plan


def save_plan(plan: Dict[str, Any], output_dir: Path) -> Path:
    """保存 Playwright MCP 计划到 JSON"""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "playwright_plan.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    logger.info("[OK] MCP 计划已保存: %s (%d 个用例)", path, len(plan["test_cases"]))
    return path


# ---------------------------------------------------------------------------
# MCP 执行器
# ---------------------------------------------------------------------------

def execute_plan(
    plan: Dict[str, Any],
    screenshot_dir: str = "output/screenshots",
    server_cmd: List[str] | None = None,
    output_dir: str | Path | None = None,
) -> List[Dict[str, Any]]:
    """通过 Playwright MCP 服务器驱动浏览器执行测试

    启动 @playwright/mcp 子进程，通过 MCP 协议调用 browser_* 工具，
    逐条执行每个测试用例的浏览器操作，自动截图。
    """
    from core.mcp_client import MCPClient

    if not server_cmd:
        server_cmd = ["npx", "@playwright/mcp", "--headless"]

    base_url = plan.get("target_url", "")
    test_cases = plan.get("test_cases", [])
    screenshot_root = Path(screenshot_dir)
    screenshot_root.mkdir(parents=True, exist_ok=True)
    results: List[Dict[str, Any]] = []

    project_root = Path(__file__).resolve().parent.parent

    with MCPClient(server_cmd, project_root=project_root) as mcp:
        # 列出可用工具（调试用）
        tools = mcp.list_tools()
        tool_names = {t["name"] for t in tools}
        logger.info("MCP 可用工具: %s", ", ".join(sorted(tool_names)))

        total = len(test_cases)
        for idx, tc in enumerate(test_cases, 1):
            case_id = tc.get("case_id", f"TC-{idx}")
            steps = tc.get("browser_steps", [])
            logger.info("执行测试 [%d/%d]: %s", idx, total, case_id)

            result: Dict[str, Any] = {
                "case_id": case_id,
                "status": "passed",
                "actual_result": "",
                "error_info": "",
                "execution_log": [],
                "screenshots": [],
            }

            try:
                # 先导航到目标地址
                _mcp_call(mcp, "browser_navigate", {"url": base_url}, result)
                _mcp_screenshot(mcp, case_id, 0, screenshot_root, result)

                for si, step in enumerate(steps):
                    mcp_tool = step.get("mcp_tool", "")
                    args = _format_mcp_args(step)
                    if not mcp_tool or mcp_tool not in tool_names:
                        logger.warning("  [%s] 跳过未知工具: %s", case_id, mcp_tool)
                        continue

                    ok = _mcp_call(mcp, mcp_tool, args, result)
                    # 每步截图
                    _mcp_screenshot(mcp, case_id, si + 1, screenshot_root, result)

                    if not ok:
                        result["status"] = "failed"

                result["actual_result"] = (
                    "所有步骤执行完成" if result["status"] == "passed" else "存在失败的步骤"
                )

            except Exception as e:
                result["status"] = "error"
                result["error_info"] = str(e)
                result["actual_result"] = f"执行异常: {e}"

            logger.info("  → %s: %s", case_id, result["status"])
            results.append(result)

    # 保存结果
    if output_dir is None:
        output_dir = Path(screenshot_dir).parent / "test_cases"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "playwright_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)
    logger.info("[OK] 执行结果已保存: %s", out_path)

    return results


def _mcp_call(mcp, tool: str, args: Dict[str, Any],
              result: Dict[str, Any]) -> bool:
    """调用 MCP 工具并记录结果"""
    log = f"[{tool}] {json.dumps(args, ensure_ascii=False)}"
    try:
        resp = mcp.call_tool(tool, args)
        is_error = resp.get("isError", False)
        content = resp.get("content", [])
        text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
        status = "FAIL" if is_error else "OK"
        log += f" → {status}"
        if text:
            log += f" | {text[:200]}"
        result["execution_log"].append(log)
        return not is_error
    except Exception as e:
        log += f" → EXCEPTION: {e}"
        result["execution_log"].append(log)
        if not result.get("error_info"):
            result["error_info"] = str(e)
        return False


def _mcp_screenshot(mcp, case_id: str, step_idx: int,
                     screenshot_root: Path, result: Dict[str, Any]) -> None:
    """通过 MCP 截图"""
    filename = f"{case_id}_step_{step_idx:02d}.png"
    shot_path = screenshot_root / filename
    # 使用相对 output/ 的路径，MCP 服务器保存到项目根目录
    rel_path = os.path.relpath(str(shot_path), Path.cwd()).replace("\\", "/")
    try:
        mcp.call_tool("browser_take_screenshot", {"type": "png", "filename": rel_path})
        result["screenshots"].append({
            "step": step_idx,
            "path": os.path.relpath(str(shot_path), screenshot_root.parent).replace("\\", "/"),
        })
    except Exception as e:
        logger.warning("截图失败 %s: %s", filename, e)


# ---------------------------------------------------------------------------
# MCP 执行说明书
# ---------------------------------------------------------------------------

def save_mcp_instructions(plan: Dict[str, Any], output_dir: Path) -> Path:
    """生成 MCP 操作手册，指导 Claude Code 使用 Playwright MCP 执行测试

    输出 Markdown 文件，每个步骤映射到 Playwright MCP 工具调用。
    """
    base_url = plan.get("target_url", "")
    test_cases = plan.get("test_cases", [])
    lines: List[str] = [
        "# Playwright MCP 测试执行说明书",
        "",
        f"目标地址: {base_url}",
        f"用例总数: {len(test_cases)}",
        f"生成时间: {plan.get('generated_at', '')}",
        "",
        "---",
        "## 执行说明",
        "",
        "请使用 Playwright MCP 工具逐条执行以下测试用例。",
        "每个步骤已映射到对应的 MCP 工具，按顺序执行即可。",
        "每步操作后调用 browser_screenshot 保存截图。",
        "全部执行完毕后，将结果填入 playwright_results.json。",
        "",
        "可用 MCP 工具:",
        "- browser_navigate({url})",
        "- browser_fill({selector, value})",
        "- browser_click({selector})",
        "- browser_snapshot()",
        "- browser_take_screenshot({path})",
        "",
    ]

    for idx, tc in enumerate(test_cases):
        case_id = tc.get("case_id", f"TC-{idx}")
        lines.extend([
            f"## {idx + 1}. {case_id} — {tc.get('feature', '')}",
            "",
            f"- 模块: {tc.get('module', '')}",
            f"- 优先级: {tc.get('priority', '')}",
            f"- 前置条件: {tc.get('precondition', '无')}",
            f"- 预期结果: {tc.get('expected', '')}",
            "",
            "### MCP 执行步骤",
            "",
        ])

        for si, step in enumerate(tc.get("browser_steps", [])):
            mcp_tool = step.get("mcp_tool", step.get("action", "?"))
            desc = step.get("description", "")
            args = _format_mcp_args(step)

            lines.append(f"**步骤 {si + 1}**: {desc or mcp_tool}")
            lines.append("")
            lines.append(f"```json")
            lines.append(json.dumps({"tool": mcp_tool, "args": args}, ensure_ascii=False, indent=2))
            lines.append(f"```")
            lines.append("")

        # 结果模板
        lines.extend([
            "### 结果记录",
            "",
            "执行完毕后，将以下 JSON 填入 `playwright_results.json`:",
            "",
            f"""```json
{{
  "case_id": "{case_id}",
  "status": "passed",
  "actual_result": "描述实际结果",
  "error_info": "失败时填写原因",
  "screenshots": []
}}
```""",
            "",
            "---",
            "",
        ])

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "mcp_instructions.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("[OK] MCP 操作手册已生成: %s", path)
    return path


def _format_mcp_args(step: Dict[str, Any]) -> Dict[str, Any]:
    """将步骤参数格式化为 MCP 工具参数（匹配 @playwright/mcp 实际 schema）"""
    action = step.get("action", "")
    sel = step.get("selector", "")
    if action == "navigate":
        return {"url": step.get("url", "")}
    elif action == "fill":
        return {"target": sel, "text": step.get("value", ""), "slowly": True, "submit": True}
    elif action in ("click", "check"):
        return {"target": sel}
    elif action == "press_key":
        return {"key": "Enter"}
    elif action == "assert":
        return {"target": sel}
    elif action == "wait":
        return {"timeout": int(step.get("value", "2000"))}
    elif action == "screenshot":
        return {"type": "png", "filename": str(step.get("value", "screenshot.png"))}
    return {}


# ---------------------------------------------------------------------------
# 结果加载
# ---------------------------------------------------------------------------

def load_results(output_dir: Path) -> List[Dict[str, Any]] | None:
    """加载执行结果（由 Claude Code 通过 MCP 执行后填写）"""
    path = output_dir / "playwright_results.json"
    if not path.exists():
        logger.error("结果文件不存在: %s", path)
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = data.get("results", [])
    logger.info("[OK] 加载执行结果: %s (%d 条)", path, len(results))
    return results


# ---------------------------------------------------------------------------
# 步骤解析（自然语言 → 结构化操作）
# ---------------------------------------------------------------------------

def _parse_step(text: str, base_url: str) -> Dict[str, Any]:
    text = text.strip()
    action = _detect_action(text)

    step: Dict[str, Any] = {"description": text, "action": action}

    if action == "custom":
        # 尝试从结构化格式解析：action: params
        m = re.match(r'^(navigate|fill|click|press_key|wait|assert|screenshot)\s*[:：]\s*(.*)', text)
        if m:
            action = m.group(1)
            step["action"] = action
            text = m.group(2).strip()

    if action == "navigate":
        step["url"] = _extract_url(text, base_url)
    elif action == "fill":
        parts = text.split(',', 1)
        step["selector"] = parts[0].strip() if parts else ""
        step["value"] = parts[1].strip() if len(parts) > 1 else ""
    elif action in ("click", "check"):
        step["selector"] = text
    elif action == "assert":
        m = re.search(r'text=(.+)', text)
        step["selector"] = m.group(1) if m else text
    elif action == "press_key":
        step["key"] = text.split(',')[0].strip() or "Enter"
    elif action == "wait":
        m = re.search(r'\d+', text)
        step["value"] = m.group() if m else "2000"
    elif action == "screenshot":
        step["value"] = text.split(',')[0].strip() or "screenshot.png"

    return step


def _detect_action(text: str) -> str:
    for keyword, action in _ACTION_KEYWORDS.items():
        if keyword in text:
            if keyword == "验证" and "验证码" in text:
                continue
            if keyword in ("确认", "检查"):
                if "框" in text or "字段" in text:
                    return "fill"
            return action
    return "custom"


def _extract_url(text: str, base_url: str) -> str:
    page_map = {"登录页": "/login", "首页": "/", "注册页": "/register", "个人中心": "/profile"}
    for cn, path in page_map.items():
        if cn in text:
            return f"{base_url}{path}"
    m = re.search(r'(?:打开|访问|跳转)\s*(?:页面|链接|地址)?\s*[：:]\s*(\S+)', text)
    if m:
        path = m.group(1)
        return path if path.startswith("http") else f"{base_url}/{path.lstrip('/')}"
    m = re.search(r'(/[\w\-/.?=&%]+)', text)
    if m:
        return f"{base_url}{m.group(1)}"
    return base_url


def _extract_selector(text: str) -> str:
    ui_keywords = {
        "搜索框": "#kw",
        "搜索": "#kw",
        "关键词": "#kw",
        "密码框": "input[type=password]",
        "密码": "input[type=password]",
        "用户名": "input[name=username]",
        "邮箱": "input[type=email]",
        "验证码": "#captcha",
    }
    for cn, sel in ui_keywords.items():
        if cn in text:
            return sel

    m = re.search(r'(?:输入|填写|键入)\s*(?:关键词|内容|文本)?\s*"?(.+?)"?\s*(?:”)?$', text)
    if m:
        hint = m.group(1).strip()
        if hint and not any(c in hint for c in "在的于"):
            return _hint_to_selector(hint)

    m = re.search(r'点击\s*(.+?)(?:\s+按钮|\s+链接|$)', text)
    if m:
        hint = m.group(1).strip()
        if hint not in ("页面", "链接", "地址"):
            return _hint_to_selector(hint)

    m = re.search(r'[：:]\s*(.+?)$', text)
    if m:
        hint = m.group(1).strip()
        if hint:
            return _hint_to_selector(hint)

    fallback = ["搜索", "登录", "确认", "提交", "注册", "发送", "密码", "用户名"]
    for kw in fallback:
        if kw in text:
            return _hint_to_selector(kw)

    return f"text={text[:20]}"


def _hint_to_selector(hint: str) -> str:
    hint = hint.strip().rstrip("按钮").rstrip("链接").rstrip("输入框").rstrip("区").strip()
    KNOWN: dict[str, str] = {
        "百度一下": "#su",
        "搜索": "#kw",
        "登录": "button:has-text('登录')",
        "注册": "button:has-text('注册')",
        "提交": "button[type=submit]",
        "发送": "button:has-text('发送')",
        "确认": "button:has-text('确认')",
        "密码": "input[type=password]",
        "用户名": "input[name=username]",
        "邮箱": "input[type=email]",
        "验证码": "#captcha",
    }
    if hint in KNOWN:
        return KNOWN[hint]
    return f"text={hint}"


def _extract_value(text: str) -> str:
    m = re.search(r'「(.+?)」', text)
    if m:
        return m.group(1)
    m = re.search(r'[""](.+?)[""]', text)
    if m:
        return m.group(1)
    m = re.search(r'(?:输入|填写|键入)\s*\S*?(?:关键词|内容|文本|信息)?\s*(\S+)$', text)
    if m:
        return m.group(1).strip("「」\"'")
    m = re.search(r'(?:输入|填写|键入)\s*\S+\s+(\S+)', text)
    if m:
        return m.group(1).strip("「」\"'")
    return "test_value"


def _extract_assert_text(text: str) -> str:
    m = re.search(r'[：:]\s*(.+?)$', text)
    return m.group(1).strip() if m else text


def _extract_wait_time(text: str) -> str:
    m = re.search(r'(\d+)\s*秒', text)
    return f"{m.group(1)}000" if m else "2000"


def _extract_filename(text: str) -> str:
    m = re.search(r'[""](.+?)[""]', text)
    return m.group(1) if m else f"screenshot_{datetime.now().strftime('%H%M%S')}.png"
