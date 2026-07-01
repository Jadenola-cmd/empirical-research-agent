"""相关系数矩阵引擎。

用法：python engine/correlation.py <parquet_path> [--columns col1,col2,...]
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from engine.lib import stats_core
from engine.lib.cli_utils import load_dataframe, numeric_columns

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: python correlation.py <parquet_path> [--columns col1,col2,...]"}, ensure_ascii=False))
        sys.exit(1)
    parquet_path = Path(sys.argv[1])
    columns = None
    if "--columns" in sys.argv:
        idx = sys.argv.index("--columns")
        if idx + 1 < len(sys.argv):
            columns = sys.argv[idx + 1].split(",")
    try:
        df = load_dataframe(parquet_path)
        result = stats_core.run_correlation(df, numeric_columns(df, columns, min_count=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
