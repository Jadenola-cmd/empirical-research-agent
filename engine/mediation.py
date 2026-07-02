"""中介效应分析引擎（Baron-Kenny三步法 + Sobel检验）。

用法：python engine/mediation.py <parquet_path> '<config_json>'
config: {"dv":"y","iv":"x","mediator":"m","controls":["c1","c2"]}
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from engine.lib import stats_core
from engine.lib.cli_utils import load_dataframe, parse_config_arg

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python mediation.py <parquet_path> '<config_json>'"}, ensure_ascii=False))
        sys.exit(1)
    parquet_path = Path(sys.argv[1])
    try:
        config = parse_config_arg(sys.argv)
        df = load_dataframe(parquet_path)
        result = stats_core.run_mediation(df, **config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
