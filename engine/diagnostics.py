"""回归诊断引擎（VIF/异方差/模型设定检验）。

用法：python engine/diagnostics.py <parquet_path> '<config_json>'
config: {"dv":"y","iv":["x1","x2"],"controls":["c1"],"model_type":"ols"}
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
import numpy as np
from engine.lib.cli_utils import load_dataframe, parse_config_arg


def run_diagnostics(df: pd.DataFrame, dv: str, iv: list, controls: list = None,
                    model_type: str = "ols", **kwargs) -> dict:
    """执行回归诊断。"""
    all_iv = iv + (controls or [])
    cols_needed = [dv] + all_iv
    df_clean = df[cols_needed].dropna()

    result = {"n": int(len(df_clean)), "vif": {}, "diagnostics": {}}

    # VIF
    try:
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        import statsmodels.api as sm
        X = sm.add_constant(df_clean[all_iv])
        for i, var in enumerate(X.columns):
            if var != "const":
                result["vif"][var] = round(variance_inflation_factor(X.values, i), 2)
    except ImportError:
        result["vif"] = {"note": "需要 statsmodels"}

    # Breusch-Pagan异方差检验
    try:
        import statsmodels.api as sm
        X = sm.add_constant(df_clean[all_iv])
        y = df_clean[dv]
        model = sm.OLS(y, X).fit()
        from statsmodels.stats.diagnostic import het_breuschpagan
        _, bp_pvalue, _, _ = het_breuschpagan(model.resid, X)
        result["diagnostics"]["breusch_pagan_pvalue"] = round(bp_pvalue, 4)
        result["diagnostics"]["heteroskedasticity"] = "存在异方差" if bp_pvalue < 0.05 else "无异方差"
    except ImportError:
        pass

    return result


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python diagnostics.py <parquet_path> '<config_json>'"}, ensure_ascii=False))
        sys.exit(1)
    parquet_path = Path(sys.argv[1])
    try:
        config = parse_config_arg(sys.argv)
        df = load_dataframe(parquet_path)
        result = run_diagnostics(df, **config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
