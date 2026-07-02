"""数据预处理引擎：清洗、缩尾、标准化、缺失值处理。

用法：python engine/preprocess.py <parquet_path> '<config_json>'

config示例：
{
  "drop_cols": ["col1", "col2"],
  "dropna": true,
  "winsorize": {"col1": [0.01, 0.99], "col2": [0.01, 0.99]},
  "standardize": ["col1", "col2"],
  "output": "cleaned.parquet"
}
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from engine.lib import cleaner_core
from engine.lib.cli_utils import load_dataframe, parse_config_arg


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python preprocess.py <parquet_path> '<config_json>'"}, ensure_ascii=False))
        sys.exit(1)

    parquet_path = Path(sys.argv[1])

    try:
        config = parse_config_arg(sys.argv)
        df = load_dataframe(parquet_path)
        result = cleaner_core.clean_dataframe(df, **config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
