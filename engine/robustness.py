"""稳健性检验编排器。

用法：python engine/robustness.py <parquet_path> '<config_json>'
config: {"method":"ols","checks":["winsorize","vif"],"primary_model_params":{...}}

状态：available（编排器就绪，具体检验项实现待补充）
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from engine.lib.cli_utils import load_dataframe, parse_json_config


def run_robustness(df: pd.DataFrame, method: str, checks: list,
                   primary_model_params: dict = None, **kwargs) -> dict:
    """按方法执行稳健性检验列表。"""
    results = {"method": method, "checks": []}
    for check in checks:
        results["checks"].append({
            "check": check,
            "status": "placeholder",
            "note": f"检验项 '{check}' 已注册，具体实现待补充"
        })
    return results


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python robustness.py <parquet_path> '<config_json>'"}, ensure_ascii=False))
        sys.exit(1)
    parquet_path = Path(sys.argv[1])
    try:
        config = parse_json_config(sys.argv[2])
        df = load_dataframe(parquet_path)
        result = run_robustness(df, **config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
