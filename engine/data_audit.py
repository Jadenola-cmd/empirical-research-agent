"""数据质检引擎：读取数据并生成质检报告。

用法：python engine/data_audit.py <parquet_path> [--method <method>]

输出：JSON格式质检报告，包含文件级/结构级/质量级/方法匹配检查结果。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
import numpy as np
from engine.lib.cli_utils import load_dataframe


ENTITY_CANDIDATES = ("entity", "id", "firm_id", "code", "company_id", "stock_code")
TIME_CANDIDATES = ("time", "year", "date", "period")


def _find_column(columns, candidates):
    lowered = {col.lower(): col for col in columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def audit_data(df: pd.DataFrame, method: str = None) -> dict:
    """对DataFrame执行完整质检，返回报告dict。"""
    report = {
        "file": {"rows": len(df), "cols": len(df.columns), "columns": list(df.columns)},
        "structure": {"numeric_cols": [], "categorical_cols": [], "constant_cols": []},
        "quality": {"missing": {}, "outliers": {}},
        "method_match": {"method": method, "ready": True, "issues": [], "detected": {}},
        "overall": "PASS",
    }

    # 结构级检查
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            report["structure"]["numeric_cols"].append(col)
            if df[col].std() == 0:
                report["structure"]["constant_cols"].append(col)
        else:
            report["structure"]["categorical_cols"].append(col)

    if not report["structure"]["numeric_cols"]:
        report["overall"] = "BLOCK"
        report["method_match"]["issues"].append("数据中无可用数值列")

    # 质量检查
    for col in df.columns:
        missing_rate = df[col].isna().mean()
        if missing_rate > 0:
            report["quality"]["missing"][col] = round(missing_rate, 4)
            if missing_rate > 0.5:
                if report["overall"] != "BLOCK":
                    report["overall"] = "WARN"

    # 异常值检查（数值列）
    for col in report["structure"]["numeric_cols"]:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 3 * iqr, q3 + 3 * iqr
        outlier_count = ((df[col] < lower) | (df[col] > upper)).sum()
        if outlier_count > 0:
            report["quality"]["outliers"][col] = int(outlier_count)
            if report["overall"] == "PASS":
                report["overall"] = "WARN"

    # 方法匹配检查
    if method:
        if method in ("panel", "did", "psm_did"):
            entity_col = _find_column(df.columns, ENTITY_CANDIDATES)
            time_col = _find_column(df.columns, TIME_CANDIDATES)
            report["method_match"]["detected"] = {"entity": entity_col, "time": time_col}
            if entity_col is None:
                report["method_match"]["ready"] = False
                report["method_match"]["issues"].append("缺少个体标识列（entity/id/firm_id等）")
            if time_col is None:
                report["method_match"]["ready"] = False
                report["method_match"]["issues"].append("缺少时间列（time/year/period等）")

    return report


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: python data_audit.py <parquet_path> [--method <method>]"}, ensure_ascii=False))
        sys.exit(1)

    data_path = Path(sys.argv[1])
    method = None
    if "--method" in sys.argv:
        idx = sys.argv.index("--method")
        if idx + 1 < len(sys.argv):
            method = sys.argv[idx + 1]

    try:
        df = load_dataframe(data_path)
        report = audit_data(df, method)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
