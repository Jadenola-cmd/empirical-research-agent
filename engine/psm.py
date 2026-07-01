"""PSM Engine - Propensity Score Matching + Balance Check + ATT.

Usage:
  python engine/psm.py <parquet> '<json_config>'

Modes:
  psm: {"dv":"y","treatment":"treat","covariates":["x1","x2"],"method":"nearest","caliper":0.05}
  psm_did: {"dv":"y","treatment":"treat","covariates":["x1","x2"],"method":"nearest","did":true,"time":"post","entity":"id"}

Status: available (production-ready)
Dependencies: scikit-learn, statsmodels
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
import numpy as np
from engine.lib.cli_utils import exit_for_result, load_dataframe, parse_json_config


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.bool_)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def _sig(p):
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def _std_mean_diff(group1, group2):
    """Standardized mean difference between two groups."""
    mean_diff = np.mean(group1) - np.mean(group2)
    pooled_var = (np.var(group1, ddof=1) + np.var(group2, ddof=1)) / 2
    if pooled_var <= 0:
        return 0.0
    return mean_diff / np.sqrt(pooled_var)


def _estimate_propensity(X, treatment):
    """Estimate propensity scores using logistic regression."""
    try:
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X, treatment)
        ps = model.predict_proba(X)[:, 1]
        return ps, model
    except ImportError:
        raise ImportError("scikit-learn required for PSM: pip install scikit-learn")


def _nearest_neighbor_match(ps, treatment, caliper=0.05):
    """Nearest neighbor matching with caliper.

    Returns matched indices for treated units.
    """
    treated_idx = np.where(treatment == 1)[0]
    control_idx = np.where(treatment == 0)[0]

    ps_treated = ps[treated_idx]
    ps_control = ps[control_idx]

    matched_pairs = []
    matched_control_used = set()

    # Sort treated by propensity score (descending) for greedy matching
    sort_order = np.argsort(-ps_treated)
    for ti in sort_order:
        t_ps = ps_treated[ti]
        # Find nearest control within caliper
        distances = np.abs(ps_control - t_ps)
        sorted_controls = np.argsort(distances)

        found = False
        for ci in sorted_controls:
            if distances[ci] <= caliper and ci not in matched_control_used:
                matched_pairs.append((treated_idx[ti], control_idx[ci]))
                matched_control_used.add(ci)
                found = True
                break

        if not found:
            # No match within caliper - this treated unit is unmatched
            matched_pairs.append((treated_idx[ti], None))

    return matched_pairs


def _kernel_match_weights(ps, treatment, bandwidth=None):
    """Kernel matching: each treated unit gets weighted average of all controls."""
    treated_idx = np.where(treatment == 1)[0]
    control_idx = np.where(treatment == 0)[0]

    ps_treated = ps[treated_idx]
    ps_control = ps[control_idx]

    if bandwidth is None:
        # Silverman's rule of thumb
        n = len(ps_control)
        bandwidth = 1.06 * np.std(ps_control, ddof=1) * n ** (-0.2)
        bandwidth = max(bandwidth, 0.01)

    weights = np.zeros((len(treated_idx), len(control_idx)))
    for i, t_ps in enumerate(ps_treated):
        diff = (ps_control - t_ps) / bandwidth
        # Gaussian kernel
        w = np.exp(-0.5 * diff ** 2) / np.sqrt(2 * np.pi)
        w = w / w.sum()  # Normalize
        weights[i] = w

    return treated_idx, control_idx, weights


def _check_balance(df, treatment, covariates, matched_pairs=None, weights=None):
    """Check covariate balance before and after matching."""
    treated = df[df[treatment] == 1]
    control = df[df[treatment] == 0]

    balance = []
    for cov in covariates:
        if cov not in df.columns:
            continue

        # Before matching
        smd_before = _std_mean_diff(treated[cov].values, control[cov].values)
        t_before = smd_before  # Simplified SMD

        # After matching
        if matched_pairs is not None:
            matched_treated_vals = []
            matched_control_vals = []
            for t_idx, c_idx in matched_pairs:
                if c_idx is not None:
                    matched_treated_vals.append(df.iloc[t_idx][cov])
                    matched_control_vals.append(df.iloc[c_idx][cov])
            if matched_treated_vals:
                smd_after = _std_mean_diff(
                    np.array(matched_treated_vals),
                    np.array(matched_control_vals)
                )
            else:
                smd_after = None
        elif weights is not None:
            # Kernel: weighted control mean
            treated_idx, control_idx, w = weights
            treated_vals = df.iloc[treated_idx][cov].values
            control_vals = df.iloc[control_idx][cov].values
            weighted_control = w @ control_vals
            smd_after = _std_mean_diff(treated_vals, weighted_control)
        else:
            smd_after = None

        balance.append({
            "variable": cov,
            "smd_before": round(smd_before, 4),
            "smd_after": round(smd_after, 4) if smd_after is not None else None,
            "balanced_after": abs(smd_after) < 0.25 if smd_after is not None else None,
            "mean_treated": round(float(treated[cov].mean()), 4),
            "mean_control": round(float(control[cov].mean()), 4),
        })

    return balance


def _compute_att(df, dv, treatment_col, matched_pairs):
    """Compute ATT from matched pairs."""
    diffs = []
    n_matched = 0
    for t_idx, c_idx in matched_pairs:
        if c_idx is not None:
            d = df.iloc[t_idx][dv] - df.iloc[c_idx][dv]
            diffs.append(d)
            n_matched += 1

    if n_matched == 0:
        return None, 0

    att = np.mean(diffs)
    att_se = np.std(diffs, ddof=1) / np.sqrt(n_matched)
    att_t = att / att_se if att_se > 0 else 0

    # P-value from t-distribution
    from scipy import stats as sp_stats
    att_p = 2 * (1 - sp_stats.t.cdf(abs(att_t), n_matched - 1))

    return {
        "att": round(float(att), 6),
        "se": round(float(att_se), 6),
        "t_stat": round(float(att_t), 4),
        "p_value": round(float(att_p), 4),
        "sig": _sig(att_p),
        "n_treated": int(np.sum(df[treatment_col])),
        "n_control": int(np.sum(1 - df[treatment_col])),
        "n_matched": n_matched,
    }, n_matched


def run_psm(df, dv, treatment, covariates, method="nearest",
            caliper=0.05, did=False, time=None, entity=None, **kwargs):
    """Run PSM analysis.

    Parameters
    ----------
    df : DataFrame
    dv : outcome variable
    treatment : treatment indicator (0/1)
    covariates : list of covariate column names
    method : matching method ("nearest" or "kernel")
    caliper : caliper width for nearest neighbor matching
    did : if True, run PSM-DID
    time : post indicator for PSM-DID
    entity : entity column for PSM-DID
    """
    df = df.copy()

    # Validate
    if treatment not in df.columns:
        return {"error": f"Treatment column '{treatment}' not found"}
    if dv not in df.columns:
        return {"error": f"Outcome column '{dv}' not found"}

    valid_covs = [c for c in covariates if c in df.columns]
    if len(valid_covs) == 0:
        return {"error": "No valid covariates found in data"}

    # Drop missing
    cols_needed = [dv, treatment] + valid_covs
    if did and time:
        cols_needed.append(time)
    if did and entity:
        cols_needed.append(entity)
    df_clean = df[cols_needed].dropna()

    treat_col = df_clean[treatment].values
    X = df_clean[valid_covs].values

    if len(np.unique(treat_col)) != 2:
        return {"error": f"Treatment variable must be binary (0/1), got {len(np.unique(treat_col))} unique values"}

    n_treated = int(np.sum(treat_col))
    n_control = int(np.sum(1 - treat_col))
    if n_treated < 10 or n_control < 10:
        return {"error": f"Insufficient sample: {n_treated} treated, {n_control} control (min 10 each)"}

    # 1. Estimate propensity scores
    try:
        ps, ps_model = _estimate_propensity(X, treat_col)
    except Exception as e:
        return {"error": f"Propensity score estimation failed: {str(e)}"}

    # 2. Match
    if method == "nearest":
        matched_pairs = _nearest_neighbor_match(ps, treat_col, caliper=caliper)
        match_weights = None
    elif method == "kernel":
        matched_pairs = None
        match_weights = _kernel_match_weights(ps, treat_col)
    else:
        return {"error": f"Unknown method '{method}'. Use 'nearest' or 'kernel'."}

    # 3. Balance check
    balance = _check_balance(df_clean, treatment, valid_covs, matched_pairs, match_weights)

    # 4. Compute ATT
    if did and time is not None:
        # PSM-DID: match on pre-treatment covariates, then DID on matched sample
        if matched_pairs:
            # Build matched sample
            matched_rows = []
            for t_idx, c_idx in matched_pairs:
                if c_idx is not None:
                    matched_rows.append(t_idx)
                    matched_rows.append(c_idx)
            if matched_rows:
                df_matched = df_clean.iloc[matched_rows].copy()
                # Run DID on matched sample
                df_matched["_did"] = df_matched[treatment] * df_matched[time]
                import statsmodels.api as sm
                exog = [treatment, time, "_did"]
                X_did = sm.add_constant(df_matched[exog])
                y_did = df_matched[dv]
                try:
                    m_did = sm.OLS(y_did, X_did).fit(cov_type="HC1")
                except Exception:
                    m_did = sm.OLS(y_did, X_did).fit()

                did_coef = m_did.params.get("_did", 0)
                did_p = m_did.pvalues.get("_did", 1)
                att_result = {
                    "att": round(float(did_coef), 6),
                    "se": round(float(m_did.bse.get("_did", 0)), 6),
                    "t_stat": round(float(m_did.tvalues.get("_did", 0)), 4),
                    "p_value": round(float(did_p), 4),
                    "sig": _sig(did_p),
                    "n_treated": n_treated,
                    "n_control": n_control,
                    "n_matched": len(matched_rows) // 2,
                    "note": "PSM-DID: ATT computed as DID coefficient on matched sample",
                }
            else:
                att_result = {"error": "No matched pairs found"}
        else:
            att_result = {"error": "PSM-DID currently only supports nearest neighbor matching"}
    else:
        if matched_pairs:
            att_result, n_matched = _compute_att(df_clean, dv, treatment, matched_pairs)
        elif match_weights:
            treated_idx, control_idx, w = match_weights
            treated_y = df_clean.iloc[treated_idx][dv].values
            control_y = df_clean.iloc[control_idx][dv].values
            weighted_control = w @ control_y
            diffs = treated_y - weighted_control
            att_val = np.mean(diffs)
            att_se = np.std(diffs, ddof=1) / np.sqrt(len(diffs))
            from scipy import stats as sp_stats
            att_t = att_val / att_se if att_se > 0 else 0
            att_p = 2 * (1 - sp_stats.t.cdf(abs(att_t), len(diffs) - 1))
            att_result = {
                "att": round(float(att_val), 6),
                "se": round(float(att_se), 6),
                "t_stat": round(float(att_t), 4),
                "p_value": round(float(att_p), 4),
                "sig": _sig(att_p),
                "n_treated": n_treated,
                "n_control": n_control,
                "note": "Kernel matching: ATT uses weighted control mean",
            }
        else:
            att_result = {"error": "No matching performed"}

    # 5. Propensity score statistics
    ps_stats = {
        "mean_treated": round(float(np.mean(ps[treat_col == 1])), 4),
        "mean_control": round(float(np.mean(ps[treat_col == 0])), 4),
        "min": round(float(np.min(ps)), 4),
        "max": round(float(np.max(ps)), 4),
        "common_support_pct": round(float(np.mean((ps > 0.01) & (ps < 0.99)) * 100), 1),
    }

    # 6. Overall balance assessment
    balanced_count = sum(1 for b in balance if b.get("balanced_after") == True)
    total_count = sum(1 for b in balance if b.get("balanced_after") is not None)

    result = {
        "method": f"psm_{method}" + ("_did" if did else ""),
        "matching_method": method,
        "caliper": caliper if method == "nearest" else None,
        "n_original": int(len(df_clean)),
        "n_treated": n_treated,
        "n_control": n_control,
        "n_matched": att_result.get("n_matched", 0) if isinstance(att_result, dict) else 0,
        "propensity_stats": ps_stats,
        "balance": balance,
        "balance_summary": {
            "balanced_count": balanced_count,
            "total_count": total_count,
            "pct_balanced": round(balanced_count / total_count * 100, 1) if total_count > 0 else 0,
            "assessment": (
                "Good balance achieved" if balanced_count == total_count
                else f"{balanced_count}/{total_count} covariates balanced after matching"
            ),
        },
        "att": att_result,
    }

    return result


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: psm.py <parquet_path> '<json_config>'",
            "examples": {
                "psm_nearest": '{"dv":"y","treatment":"treat","covariates":["x1","x2"],"method":"nearest","caliper":0.05}',
                "psm_kernel": '{"dv":"y","treatment":"treat","covariates":["x1","x2"],"method":"kernel"}',
                "psm_did": '{"dv":"y","treatment":"treat","covariates":["x1","x2"],"method":"nearest","did":true,"time":"post","entity":"id"}',
            }
        }, ensure_ascii=False))
        sys.exit(1)

    try:
        config = parse_json_config(sys.argv[2])
        df = load_dataframe(sys.argv[1])
        result = run_psm(df, **config)
        print(json.dumps(result, ensure_ascii=False, indent=2, cls=NpEncoder))
        sys.exit(exit_for_result(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
