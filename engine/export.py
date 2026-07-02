"""导出引擎（Word/Excel/LaTeX）。

用法：python engine/export.py <analysis_result_json> '<config_json>'
config: {"format":"docx","template":"paper","output":"report.docx"}

状态：available（依赖 documents skill 或 python-docx）
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.lib.cli_utils import parse_config_arg

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _fmt_num(value):
    if value is None:
        return ""
    return f"{float(value):.3f}"


def _model_label(result, index):
    model_type = result.get("type")
    if model_type == "ols":
        return f"({index}) 混合 OLS"
    if model_type == "fe":
        return f"({index}) 固定效应 FE"
    if model_type == "re":
        return f"({index}) 随机效应 RE"
    return f"({index}) {model_type or '模型'}"


def _coefficient_map(result):
    return {row["variable"]: row for row in result.get("coefficients", [])}


def _ordered_variables(results):
    ordered = []
    for result in results:
        for row in result.get("coefficients", []):
            variable = row["variable"]
            if variable != "_cons" and variable not in ordered:
                ordered.append(variable)
    if any("_cons" in _coefficient_map(result) for result in results):
        ordered.append("_cons")
    return ordered


def _render_regression_table(results):
    labels = [_model_label(result, idx + 1) for idx, result in enumerate(results)]
    coef_maps = [_coefficient_map(result) for result in results]
    lines = ["**Table 2: Baseline Regression Results**", ""]
    lines.append("| 变量 | " + " | ".join(labels) + " |")
    lines.append("|---|" + "|".join("---" for _ in labels) + "|")

    for variable in _ordered_variables(results):
        coef_cells = []
        t_cells = []
        for coef_map in coef_maps:
            row = coef_map.get(variable)
            if row:
                coef_cells.append(f"{_fmt_num(row.get('coef'))}{row.get('sig', '')}")
                t_cells.append(f"({_fmt_num(row.get('t_stat'))})")
            else:
                coef_cells.append("")
                t_cells.append("")
        lines.append(f"| {variable} | " + " | ".join(coef_cells) + " |")
        lines.append("|  | " + " | ".join(t_cells) + " |")

    stat_rows = [
        ("N", lambda result: result.get("n")),
        ("R²", lambda result: result.get("r2")),
        ("Adjusted R²", lambda result: result.get("r2_adj")),
        ("Within R²", lambda result: result.get("r2_within")),
        ("F统计量", lambda result: result.get("f_stat")),
        ("Hausman p值", lambda result: (result.get("hausman") or {}).get("p_value")),
    ]
    for label, getter in stat_rows:
        values = [_fmt_num(getter(result)) for result in results]
        if any(values):
            lines.append(f"| {label} | " + " | ".join(values) + " |")

    se_types = ", ".join(dict.fromkeys(result.get("se_type", "未说明") for result in results))
    controls = sorted({var for result in results for var in result.get("control_vars", [])})
    control_note = f" All models include controls: {', '.join(controls)}." if controls else ""
    lines.extend([
        "",
        f"Notes: t-statistics in parentheses. Standard errors are {se_types}. ***p<0.01, **p<0.05, *p<0.1.{control_note}",
    ])
    return "\n".join(lines)


def _render_interpretation(results):
    lines = ["", "### 结果解读"]
    for result in results:
        label = _model_label(result, results.index(result) + 1)
        primary = result.get("indep_vars", [None])[0]
        coef = _coefficient_map(result).get(primary) if primary else None
        if coef:
            lines.append(
                f"- [VERIFIED] {label} 中，{primary} 的系数为 {_fmt_num(coef.get('coef'))}"
                f"{coef.get('sig', '')}，t值为 {_fmt_num(coef.get('t_stat'))}，结果完全来自 engine JSON。"
            )
        hausman = result.get("hausman")
        if hausman:
            lines.append(
                f"- [VERIFIED] Hausman 检验 p值为 {_fmt_num(hausman.get('p_value'))}，"
                f"模型选择结论为：{hausman.get('conclusion')}。"
            )
    return "\n".join(lines)


def _render_paper_markdown(results):
    return "\n".join([
        "## 实证结果",
        "",
        "### 2. 基准回归",
        "",
        _render_regression_table(results),
        _render_interpretation(results),
    ])


def export_result(result: dict, export_format: str = "docx",
                  template: str = "paper", output: str = None, comparison_results=None, **kwargs) -> dict:
    """将分析结果导出为指定格式。"""
    payload = {
        "status": "available",
        "format": export_format,
        "template": template,
        "output": output,
    }
    if export_format == "markdown" and template == "paper":
        results = [result] + list(comparison_results or [])
        payload["content"] = _render_paper_markdown(results)
        if output:
            Path(output).write_text(payload["content"], encoding="utf-8")
        return payload
    payload["note"] = "导出引擎已就绪。Word导出依赖 documents skill；Excel/LaTeX导出待实现。"
    return payload


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python export.py <result_json_path> '<config_json>'"}, ensure_ascii=False))
        sys.exit(1)
    result_path = Path(sys.argv[1])
    try:
        config = parse_config_arg(sys.argv)
        with open(result_path, "r", encoding="utf-8-sig") as f:
            result_data = json.load(f)
        comparison_results = []
        for comparison_path in config.pop("comparison_paths", []):
            with open(comparison_path, "r", encoding="utf-8-sig") as f:
                comparison_results.append(json.load(f))
        export_result_data = export_result(result_data, comparison_results=comparison_results, **config)
        print(json.dumps(export_result_data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
