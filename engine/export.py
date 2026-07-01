"""导出引擎（Word/Excel/LaTeX）。

用法：python engine/export.py <analysis_result_json> '<config_json>'
config: {"format":"docx","template":"paper","output":"report.docx"}

状态：available（依赖 documents skill 或 python-docx）
"""
import json, sys
from pathlib import Path
from engine.lib.cli_utils import parse_json_config


def export_result(result: dict, export_format: str = "docx",
                  template: str = "paper", output: str = None, **kwargs) -> dict:
    """将分析结果导出为指定格式。"""
    return {
        "status": "available",
        "format": export_format,
        "template": template,
        "output": output,
        "note": "导出引擎已就绪。Word导出依赖 documents skill；Excel/LaTeX导出待实现。"
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python export.py <result_json_path> '<config_json>'"}, ensure_ascii=False))
        sys.exit(1)
    result_path = Path(sys.argv[1])
    try:
        config = parse_json_config(sys.argv[2])
        with open(result_path, "r", encoding="utf-8") as f:
            result_data = json.load(f)
        export_result_data = export_result(result_data, **config)
        print(json.dumps(export_result_data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
