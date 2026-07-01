"""异质性分析引擎（分组回归 + Chow检验）。

用法：python engine/heterogeneity.py <parquet_path> '<config_json>'
config: {"dv":"y","iv":["x1"],"controls":["c1"],"group_var":"industry","method":"category","base_model":"ols"}
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from engine.lib import stats_core
from engine.lib.cli_utils import load_dataframe, parse_json_config

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python heterogeneity.py <parquet_path> '<config_json>'"}, ensure_ascii=False))
        sys.exit(1)
    parquet_path = Path(sys.argv[1])
    try:
        config = parse_json_config(sys.argv[2])
        df = load_dataframe(parquet_path)
        result = stats_core.run_heterogeneity(df, **config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
