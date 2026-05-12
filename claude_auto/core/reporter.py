"""报告生成模块 - 输出 JSON / Markdown / HTML 三种格式测试报告"""

import json
import logging
import os
import string
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_TEMPLATES: Dict[str, string.Template] = {}

def _load_template(name: str) -> string.Template:
    if name not in _TEMPLATES:
        path = Path(__file__).parent / "templates" / name
        _TEMPLATES[name] = string.Template(path.read_text(encoding="utf-8"))
    return _TEMPLATES[name]


def generate_report(
    test_cases: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    output_dir: Path,
    screenshot_base: Path | None = None,
) -> tuple[Path, Path]:
    """生成主报告 + 子报告（HTML）+ JSON + Markdown

    Returns:
        (index_path, detail_dir) 主报告路径和详情目录路径
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    detail_dir = output_dir / "details"
    detail_dir.mkdir(exist_ok=True)

    # 统计
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "passed")
    failed = sum(1 for r in results if r.get("status") == "failed")
    errors = sum(1 for r in results if r.get("status") == "error")
    pass_rate = f"{passed / total * 100:.1f}%" if total else "0%"

    # 详情（含截图）
    details: List[Dict[str, Any]] = []
    for tc, result in zip(test_cases, results):
        steps = tc.get("steps", [])
        step_list = steps if isinstance(steps, list) else [str(steps)]
        screenshots_map: Dict[int, str] = {}
        for shot in result.get("screenshots", []):
            if isinstance(shot, dict) and "path" in shot:
                screenshots_map[shot["step"]] = shot["path"]

        paired_steps = []
        for si, s in enumerate(step_list):
            paired_steps.append({
                "text": s,
                "screenshot": screenshots_map.get(si, ""),
            })

        details.append({
            "case_id": tc.get("case_id", ""),
            "module": tc.get("module", ""),
            "feature": tc.get("feature", ""),
            "precondition": tc.get("precondition", ""),
            "steps": step_list,
            "paired_steps": paired_steps,
            "expected": tc.get("expected", ""),
            "priority": tc.get("priority", ""),
            "status": result.get("status", "unknown"),
            "actual_result": result.get("actual_result", ""),
            "error_info": result.get("error_info", ""),
            "execution_log": result.get("execution_log", []),
        })

    report = {
        "report_time": datetime.now().isoformat(),
        "summary": {"total": total, "passed": passed, "failed": failed, "errors": errors, "pass_rate": pass_rate},
        "details": details,
    }

    # --- JSON ---
    json_path = output_dir / f"report_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # --- Markdown ---
    md_path = output_dir / f"report_{timestamp}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 测试报告\n\n")
        f.write(f"**生成时间**: {report['report_time']}\n\n")
        f.write("## 测试摘要\n\n")
        f.write("| 指标 | 数值 |\n| --- | --- |\n")
        f.write(f"| 总用例数 | {total} |\n")
        f.write(f"| 通过 | {passed} |\n")
        f.write(f"| 失败 | {failed} |\n")
        f.write(f"| 错误 | {errors} |\n")
        f.write(f"| 通过率 | {pass_rate} |\n\n")
        f.write("## 测试详情\n\n")
        status_icon = {"passed": "✅", "failed": "❌", "error": "⚠️"}
        for d in details:
            icon = status_icon.get(d["status"], "❓")
            f.write(f"### {icon} {d['case_id']}\n\n")
            f.write(f"- **模块**: {d['module']}\n")
            f.write(f"- **功能点**: {d['feature']}\n")
            f.write(f"- **优先级**: {d['priority']}\n")
            f.write(f"- **状态**: {d['status']}\n")
            if d["error_info"]:
                f.write(f"- **错误信息**: {d['error_info']}\n")
            if d["execution_log"]:
                f.write("- **执行日志**:\n")
                for log_entry in d["execution_log"]:
                    f.write(f"  - {log_entry}\n")
            f.write("\n")

    # --- HTML 主报告 ---
    index_path = _generate_index_report(report, output_dir, timestamp, details)

    # --- HTML 子报告 ---
    _generate_case_reports(details, detail_dir, screenshot_base)

    logger.info("测试报告已生成:")
    logger.info("  JSON: %s", json_path)
    logger.info("  MD:   %s", md_path)
    logger.info("  HTML: %s (主报告)", index_path)
    return index_path, detail_dir


def print_summary(results: List[Dict[str, Any]]) -> None:
    """在控制台打印测试摘要"""
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "passed")
    failed = sum(1 for r in results if r.get("status") == "failed")
    errors = sum(1 for r in results if r.get("status") == "error")
    rate = f"{passed / total * 100:.1f}%" if total else "N/A"

    line = "=" * 50
    print(f"\n{line}")
    print("  测试执行完成")
    print(line)
    print(f"  总用例:  {total}")
    print(f"  通过:    {passed}")
    print(f"  失败:    {failed}")
    print(f"  错误:    {errors}")
    print(f"  通过率:  {rate}")
    print(line)


def _badge(status: str) -> str:
    icons = {"passed": "✓", "failed": "✗", "error": "!"}
    return f'<span class="badge badge-{status}">{icons.get(status, "?")} {status.upper()}</span>'


def _generate_index_report(
    report: Dict[str, Any], output_dir: Path, timestamp: str,
    details: List[Dict[str, Any]],
) -> Path:
    """生成主报告 index.html"""
    summary = report["summary"]

    stat_cards = f"""
    <div class="stats">
      <div class="card card-total"><div class="num">{summary["total"]}</div><div class="label">总用例</div></div>
      <div class="card card-pass"><div class="num">{summary["passed"]}</div><div class="label">通过</div></div>
      <div class="card card-fail"><div class="num">{summary["failed"]}</div><div class="label">失败</div></div>
      <div class="card card-error"><div class="num">{summary["errors"]}</div><div class="label">错误</div></div>
      <div class="card card-rate"><div class="num">{summary["pass_rate"]}</div><div class="label">通过率</div></div>
    </div>"""

    pct = summary["passed"] / summary["total"] * 100 if summary["total"] else 0
    progress_bar = f"""
    <div class="progress-wrap">
      <div class="progress-bar">
        <div class="progress-fill" style="width:{pct:.1f}%"></div>
      </div>
      <div class="progress-label">通过率 {summary["pass_rate"]}</div>
    </div>"""

    table_rows = []
    for i, d in enumerate(details):
        case_id = d["case_id"] or f"TC-{i + 1}"
        rel_path = f"details/{case_id}.html"
        table_rows.append(f"""<tr onclick="location.href='{rel_path}'" class="row-{d['status']}">
          <td class="col-id">{case_id}</td>
          <td class="col-module">{d['module']}</td>
          <td class="col-feature">{d['feature']}</td>
          <td class="col-priority">{d['priority']}</td>
          <td class="col-status">{_badge(d['status'])}</td>
        </tr>""")

    html = _load_template("index.html").substitute(
        timestamp=timestamp,
        report_time=report["report_time"],
        stat_cards=stat_cards,
        progress_bar=progress_bar,
        table_rows="".join(table_rows),
    )

    index_path = output_dir / f"index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    return index_path


def _generate_case_reports(
    details: List[Dict[str, Any]], detail_dir: Path,
    screenshot_base: Path | None = None,
) -> None:
    """生成每个用例的子报告"""
    def rel_screenshot(path: str) -> str:
        if not path or not screenshot_base:
            return ""
        full = Path(screenshot_base) / Path(path).name if not Path(path).is_absolute() else Path(path)
        try:
            rel = os.path.relpath(str(full.resolve()), str(detail_dir.resolve()))
            return rel.replace("\\", "/")
        except Exception:
            return str(full.name).replace("\\", "/")

    for i, d in enumerate(details):
        case_id = d["case_id"] or f"TC-{i + 1}"

        steps_html = '<ol class="step-list">'
        for ps in d.get("paired_steps", []):
            shot_path = rel_screenshot(ps.get("screenshot", ""))
            shot_img = ""
            if shot_path:
                shot_img = f'<a href="{shot_path}" target="_blank" class="shot-link"><img src="{shot_path}" class="shot-thumb" alt="截图"></a>'
            steps_html += f"<li><span class='step-text'>{ps['text']}</span>{shot_img}</li>"
        steps_html += "</ol>"
        if not d.get("paired_steps"):
            steps_html = "<p class='empty'>无步骤</p>"

        log_html = ""
        if d.get("execution_log"):
            log_html = "<div class='section'><h3>执行日志</h3><div class='log-box'>" + "".join(
                f"<div class='log-line'>{entry}</div>" for entry in d["execution_log"]
            ) + "</div></div>"

        error_html = ""
        if d.get("error_info"):
            error_html = f"<div class='section error-section'><h3>错误信息</h3><pre>{d['error_info']}</pre></div>"

        html = _load_template("case.html").substitute(
            case_id=case_id,
            status=d['status'],
            module=d['module'],
            feature=d['feature'],
            priority=d['priority'],
            precondition=d.get('precondition') or '无',
            expected=d.get('expected') or '无',
            actual_result=d.get('actual_result') or '无',
            steps_html=steps_html,
            error_html=error_html,
            log_html=log_html,
        )

        case_path = detail_dir / f"{case_id}.html"
        with open(case_path, "w", encoding="utf-8") as f:
            f.write(html)
