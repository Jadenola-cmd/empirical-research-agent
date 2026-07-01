import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_cmd(*args):
    return subprocess.run(
        [PYTHON, *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def parse_json(stdout):
    return json.loads(stdout)


def test_descriptive_cli_succeeds_with_default_numeric_columns():
    proc = run_cmd("engine/descriptive.py", "tests/fixtures/panel_data.parquet")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = parse_json(proc.stdout)
    assert payload["type"] == "descriptive"
    assert any(row["name"] == "LEV" for row in payload["vars"])


def test_correlation_cli_succeeds_with_default_numeric_columns():
    proc = run_cmd("engine/correlation.py", "tests/fixtures/panel_data.parquet")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = parse_json(proc.stdout)
    assert payload["type"] == "correlation"
    assert "LEV" in payload["vars"]
    assert "ROA" in payload["vars"]


def test_data_audit_reads_csv_and_recognizes_code_year_panel():
    proc = run_cmd("engine/data_audit.py", "tests/fixtures/panel_data.csv", "--method", "panel")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = parse_json(proc.stdout)
    assert payload["file"]["rows"] == 174
    assert payload["method_match"]["ready"] is True
    assert payload["method_match"]["detected"]["entity"] == "code"
    assert payload["method_match"]["detected"]["time"] == "year"


def test_invalid_json_config_returns_json_error_without_traceback():
    proc = run_cmd("engine/ols.py", "tests/fixtures/panel_data.parquet", "{bad json}")
    assert proc.returncode == 1
    assert "Traceback" not in proc.stderr
    payload = parse_json(proc.stdout)
    assert "error" in payload
    assert "Invalid JSON config" in payload["error"]


def test_psm_and_did_business_errors_exit_nonzero(tmp_path):
    df = pd.read_parquet(ROOT / "tests/fixtures/panel_data.parquet").copy()
    df["bad_treat"] = df["STATE"]
    bad_psm = tmp_path / "bad_psm.parquet"
    df.to_parquet(bad_psm)

    psm_proc = run_cmd(
        "engine/psm.py",
        str(bad_psm),
        '{"dv":"LEV","treatment":"bad_treat","covariates":["ROA","SIZE"],"method":"nearest"}',
    )
    assert psm_proc.returncode == 1
    assert "Traceback" not in psm_proc.stderr
    assert "error" in parse_json(psm_proc.stdout)

    did_proc = run_cmd(
        "engine/did.py",
        "tests/fixtures/panel_data.parquet",
        '{"dv":"LEV","treatment":"STATE"}',
    )
    assert did_proc.returncode == 1
    assert "Traceback" not in did_proc.stderr
    assert "error" in parse_json(did_proc.stdout)


def test_reporting_protocol_does_not_default_to_tab_blocks():
    reporting = (ROOT / "protocols/reporting.md").read_text(encoding="utf-8")
    paper = (ROOT / "templates/paper.md").read_text(encoding="utf-8")
    assert "默认不输出 Tab 分隔复制块" in reporting
    assert "默认不附 Tab 分隔复制块" in paper


def test_requirements_include_linearmodels_for_panel():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "linearmodels>=5.0" in requirements


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            if "tmp_path" in fn.__code__.co_varnames:
                import tempfile

                with tempfile.TemporaryDirectory() as d:
                    fn(Path(d))
            else:
                fn()
            print(f"PASS {name}")
        except Exception as exc:
            failures += 1
            print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)
