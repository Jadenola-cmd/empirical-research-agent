"""Shared helpers for engine command-line entrypoints."""
import json
import sys
from pathlib import Path

import pandas as pd


def print_json(payload, *, encoder=None, exit_code=None):
    print(json.dumps(payload, ensure_ascii=False, indent=2, cls=encoder))
    if exit_code is not None:
        sys.exit(exit_code)


def print_error(message, *, exit_code=1):
    print_json({"error": str(message)}, exit_code=exit_code)


def parse_json_config(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Windows PowerShell often strips quotes unless users pass escaped JSON.
        try:
            return json.loads(raw.encode("utf-8").decode("unicode_escape"))
        except Exception as exc:
            raise ValueError(f"Invalid JSON config: {exc}") from exc


def parse_config_arg(argv, *, index=2):
    if len(argv) <= index:
        raise ValueError("Missing JSON config")
    if argv[index] == "--config-file":
        if len(argv) <= index + 1:
            raise ValueError("Missing config file path after --config-file")
        config_path = Path(argv[index + 1])
        try:
            return json.loads(config_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON config file: {exc}") from exc
    return parse_json_config(argv[index])


def load_dataframe(path):
    data_path = Path(path)
    ext = data_path.suffix.lower()
    if ext == ".parquet":
        return pd.read_parquet(data_path)
    if ext == ".csv":
        for encoding in ("utf-8", "utf-8-sig", "gbk", "gb2312"):
            try:
                return pd.read_csv(data_path, encoding=encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Unable to decode CSV file: {data_path}")
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(data_path)
    if ext == ".dta":
        return pd.read_stata(data_path)
    raise ValueError(f"Unsupported file format: {ext}. Supported: .csv, .xlsx, .parquet, .dta")


def numeric_columns(df, columns=None, *, min_count=1):
    selected = list(columns) if columns else [
        col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])
    ]
    missing = [col for col in selected if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")
    selected = [col for col in selected if pd.api.types.is_numeric_dtype(df[col])]
    if len(selected) < min_count:
        raise ValueError(f"Need at least {min_count} numeric column(s), got {len(selected)}")
    return selected


def exit_for_result(result):
    return 1 if isinstance(result, dict) and "error" in result else 0
