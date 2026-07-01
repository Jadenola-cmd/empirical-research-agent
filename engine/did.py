"""DID Engine - Standard DID + Event Study + Parallel Trends Test.

Usage:
  python engine/did.py <parquet> '<json_config>'

Modes:
  standard: {"dv":"y","treatment":"treat","time":"post","entity":"id"}
  event_study: {"dv":"y","treatment":"treat","time_var":"year","treatment_time":2015,"entity":"id","event_study":true}
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
import numpy as np
from engine.lib.cli_utils import exit_for_result, load_dataframe, parse_json_config


class NpEncoder(json.JSONEncoder):
    """Handle numpy types for JSON serialization."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.bool_)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def _sig(p):
    """Convert p-value to significance stars."""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def run_standard_did(df, dv, treatment, time, controls=None, entity=None):
    """Standard DID with binary post indicator."""
    df = df.copy()
    df["_did"] = df[treatment] * df[time]

    exog = [treatment, time, "_did"] + (controls or [])
    clean = df[[dv] + exog].dropna()

    import statsmodels.api as sm
    X = sm.add_constant(clean[exog])
    y = clean[dv]

    try:
        if entity and entity in clean.columns:
            model = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": clean[entity]})
            se_type = f"clustered({entity})"
        else:
            model = sm.OLS(y, X).fit(cov_type="HC1")
            se_type = "HC1"
    except Exception:
        model = sm.OLS(y, X).fit()
        se_type = "standard"

    result = {
        "method": "standard_did",
        "did_coefficient": round(model.params.get("_did", 0), 6),
        "se": round(model.bse.get("_did", 0), 6),
        "t_stat": round(model.tvalues.get("_did", 0), 4),
        "p_value": round(model.pvalues.get("_did", 0), 4),
        "sig": _sig(model.pvalues.get("_did", 0)),
        "r2": round(model.rsquared, 4),
        "n": int(len(clean)),
        "se_type": se_type,
        "coefficients": {},
    }

    for var in model.params.index:
        pv = model.pvalues[var]
        result["coefficients"][var] = {
            "coef": round(model.params[var], 6),
            "se": round(model.bse[var], 6),
            "t_stat": round(model.tvalues[var], 4),
            "p_value": round(pv, 4),
            "sig": _sig(pv),
        }

    return result


def run_event_study(df, dv, treatment, time_var, treatment_time,
                    entity=None, controls=None,
                    pre_periods=None, post_periods=None):
    """Event study with relative-time dummies and parallel trends F-test."""
    df = df.copy()

    # Compute relative time
    df["_rel"] = df[time_var] - treatment_time
    rel_values = sorted(df["_rel"].unique())

    # Determine windows
    pre_values = [v for v in rel_values if v < 0]
    post_values = [v for v in rel_values if v > 0]
    if pre_periods is not None:
        pre_values = [v for v in pre_values if v >= -pre_periods]
    if post_periods is not None:
        post_values = [v for v in post_values if v <= post_periods]

    all_periods = sorted(pre_values + post_values)
    base_period = -1

    # Generate treatment x relative-time interactions
    interact_cols = []
    interact_map = {}
    for p in all_periods:
        if p == base_period:
            continue
        col_name = f"_did_r{p}"
        df[col_name] = df[treatment] * (df["_rel"] == p).astype(float)
        interact_cols.append(col_name)
        interact_map[col_name] = p

    exog_vars = list(interact_cols)

    # Entity fixed effects
    if entity is not None and entity in df.columns:
        entity_dummies = pd.get_dummies(df[entity], prefix="_e", drop_first=True).astype(float)
        df = pd.concat([df, entity_dummies], axis=1)
        exog_vars.extend(entity_dummies.columns.tolist())

    # Time fixed effects
    time_dummies = pd.get_dummies(df[time_var], prefix="_t", drop_first=True).astype(float)
    df = pd.concat([df, time_dummies], axis=1)
    exog_vars.extend(time_dummies.columns.tolist())

    if controls:
        exog_vars.extend([c for c in controls if c in df.columns])

    # Regression
    cols_needed = [dv] + exog_vars
    clean = df[cols_needed].dropna()

    import statsmodels.api as sm
    X = sm.add_constant(clean[exog_vars])
    y = clean[dv]

    try:
        model = sm.OLS(y, X).fit(cov_type="HC1")
        se_type = "HC1"
    except Exception:
        model = sm.OLS(y, X).fit()
        se_type = "standard"

    # Extract event study coefficients
    event_coefs = []
    for col in interact_cols:
        if col in model.params.index:
            rt = interact_map[col]
            pv = model.pvalues[col]
            event_coefs.append({
                "relative_time": int(rt),
                "period_type": "pre" if rt < 0 else "post",
                "coef": round(model.params[col], 6),
                "se": round(model.bse[col], 6),
                "ci_lower": round(model.params[col] - 1.96 * model.bse[col], 6),
                "ci_upper": round(model.params[col] + 1.96 * model.bse[col], 6),
                "t_stat": round(model.tvalues[col], 4),
                "p_value": round(pv, 4),
                "sig": _sig(pv),
            })

    # Parallel trends test: F-test on all pre-treatment interactions
    pre_cols_in_model = [
        c for c in interact_cols
        if c in model.params.index and interact_map[c] < 0 and interact_map[c] != base_period
    ]

    if len(pre_cols_in_model) >= 2:
        # Restricted model without pre-trend interactions
        restricted_vars = [v for v in exog_vars if v not in pre_cols_in_model]
        Xr = sm.add_constant(clean[restricted_vars])
        model_r = sm.OLS(y, Xr).fit()

        q = len(pre_cols_in_model)
        f_stat = ((model_r.ssr - model.ssr) / q) / (model.ssr / model.df_resid)
        from scipy import stats
        parallel_pvalue = 1 - stats.f.cdf(f_stat, q, model.df_resid)

        parallel_trends = {
            "f_stat": round(f_stat, 4),
            "p_value": round(parallel_pvalue, 4),
            "passed": parallel_pvalue >= 0.05,
            "pre_periods_tested": q,
            "interpretation": (
                "Parallel trends hold: no significant pre-treatment differences"
                if parallel_pvalue >= 0.05
                else "Parallel trends VIOLATED: DID estimate may be biased"
            ),
        }
    elif len(pre_cols_in_model) == 1:
        pv = model.pvalues[pre_cols_in_model[0]]
        parallel_trends = {
            "f_stat": None,
            "p_value": round(pv, 4),
            "passed": pv >= 0.05,
            "pre_periods_tested": 1,
            "interpretation": (
                "Parallel trends hold (single pre-period)"
                if pv >= 0.05
                else "Parallel trends questionable (single pre-period significant)"
            ),
            "note": "Only 1 pre-treatment period available; more periods recommended for reliable testing.",
        }
    else:
        parallel_trends = {
            "f_stat": None,
            "p_value": None,
            "passed": None,
            "pre_periods_tested": 0,
            "interpretation": "Cannot test parallel trends: no pre-treatment periods or base period issue.",
        }

    result = {
        "method": "event_study",
        "treatment_time": int(treatment_time),
        "base_period": int(base_period),
        "n_periods": len(all_periods),
        "n_pre_periods": len(pre_values),
        "n_post_periods": len(post_values),
        "n": int(len(clean)),
        "r2": round(model.rsquared, 4),
        "se_type": se_type,
        "event_coefficients": sorted(event_coefs, key=lambda x: x["relative_time"]),
        "parallel_trends": parallel_trends,
    }

    return result


def run_did(df, dv, treatment, time=None, time_var=None,
            treatment_time=None, entity=None, controls=None,
            event_study=False, pre_periods=None, post_periods=None, **kwargs):
    """Unified DID entry point.

    Two modes:
    1. Standard DID: provide binary 'time' (post indicator)
    2. Event study: provide 'time_var' + 'treatment_time' + event_study=True
    """
    if event_study and time_var is not None and treatment_time is not None:
        return run_event_study(
            df, dv, treatment, time_var, treatment_time,
            entity=entity, controls=controls,
            pre_periods=pre_periods, post_periods=post_periods,
        )
    elif time is not None:
        return run_standard_did(df, dv, treatment, time, controls=controls, entity=entity)
    else:
        return {
            "error": (
                "Specify DID mode:\\n"
                "  Standard DID: time='post_dummy'\\n"
                "  Event study: time_var='year', treatment_time=2015, event_study=True"
            )
        }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: did.py <parquet_path> '<json_config>'",
            "examples": {
                "standard_did": '{"dv":"y","treatment":"treat","time":"post","entity":"id"}',
                "event_study": '{"dv":"y","treatment":"treat","time_var":"year","treatment_time":2015,"entity":"id","event_study":true}',
            }
        }, ensure_ascii=False))
        sys.exit(1)

    try:
        config = parse_json_config(sys.argv[2])
        df = load_dataframe(sys.argv[1])
        result = run_did(df, **config)
        print(json.dumps(result, ensure_ascii=False, indent=2, cls=NpEncoder))
        sys.exit(exit_for_result(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
