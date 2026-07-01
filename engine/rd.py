"""断点回归设计引擎（Sharp RD + 带宽选择 + McCrary检验）。

用法：python engine/rd.py <parquet_path> '<config_json>'
config: {"dv":"y","running_var":"score","cutoff":0,"bandwidth":"optimal"}

状态：planned（尚未实现）
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from engine.lib.cli_utils import load_dataframe, parse_json_config


def run_rd(df: pd.DataFrame, dv: str, running_var: str, cutoff: float,
           bandwidth: str = "optimal", **kwargs) -> dict:
    """执行Sharp RD估计。"""
    return {
        "status": "planned",
        "note": "RD引擎尚未实现。预计支持：Sharp RD + 最优带宽(CCT) + McCrary操纵检验。"
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python rd.py <parquet_path> '<config_json>'"}, ensure_ascii=False))
        sys.exit(1)
    parquet_path = Path(sys.argv[1])
    try:
        config = parse_json_config(sys.argv[2])
        df = load_dataframe(parquet_path)
        result = run_rd(df, **config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
