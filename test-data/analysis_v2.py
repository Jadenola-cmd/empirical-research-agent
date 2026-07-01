"""资本结构影响因素 - 完整实证分析脚本 v2
架构：数据合并预处理 → 保存 parquet → 调用 engine/ 脚本计算 → 汇总结果JSON
所有统计计算通过 engine/ 脚本完成，本脚本只做数据管道和引擎调用编排。
"""

import sys
import json
import subprocess
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 配置
# ============================================================
PYTHON = r"C:\Users\简洁\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
SKILL_DIR = r"C:\Users\简洁\.workbuddy\skills\empirical-research-agent"
OUT_DIR = r"D:\00_Workspace\99_Sandbox\empirical技能-test\test-data"
PARQUET_PATH = fr"{OUT_DIR}\panel_data.parquet"

DATA_FILES = {
    'FI_T1':      {'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T1.xlsx',     'code_col': '股票代码',     'date_col': '截止日期'},
    'FI_T4':      {'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T4.xlsx',     'code_col': '股票代码',     'date_col': '截止日期'},
    'FI_T5':      {'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T5.xlsx',     'code_col': '股票代码',     'date_col': '截止日期'},
    'FI_T8':      {'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T8.xlsx',     'code_col': '股票代码',     'date_col': '会计年度'},
    'FS_Combas':  {'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FS_Combas.xlsx',  'code_col': '证券代码',     'date_col': '会计期间'},
    'FS_Comscfi': {'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FS_Comscfi.xlsx', 'code_col': '证券代码',     'date_col': '会计期间'},
    'CG_Capchg':  {'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/CG_Capchg.xlsx',  'code_col': 'code',         'date_col': 'date'},
    'CG_Ybasic':  {'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/CG_Ybasic.xlsx',  'code_col': '证券代码',     'date_col': '统计截止日期'},
}

VAR_LIST = ['LEV', 'SIZE', 'ROA', 'GROWTH', 'TANG', 'NDTS', 'TURN', 'STATE', 'INDEP', 'MSHARE_LN']
REG_VARS = ['SIZE', 'ROA', 'GROWTH', 'TANG', 'NDTS', 'TURN', 'STATE', 'INDEP', 'MSHARE_LN']


def run_engine(script: str, args: list) -> dict:
    """调用 engine/ 子脚本，返回 JSON 结果字典。"""
    script_path = fr"{SKILL_DIR}\engine\{script}"
    cmd = [PYTHON, script_path] + args
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding='utf-8',
        cwd=SKILL_DIR
    )
    if result.returncode != 0:
        raise RuntimeError(f"engine/{script} 失败:\nSTDOUT:{result.stdout}\nSTDERR:{result.stderr}")
    output = result.stdout.strip()
    if not output:
        raise RuntimeError(f"engine/{script} 无输出\nSTDERR:{result.stderr}")
    return json.loads(output)


# ============================================================
# Step 1: 数据读取与合并
# ============================================================
print("=" * 60)
print("Step 1: 数据读取与合并")
print("=" * 60)

data = {}
for name, cfg in DATA_FILES.items():
    df = pd.read_excel(cfg['path'])
    df = df.rename(columns={cfg['code_col']: 'code', cfg['date_col']: 'date'})
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    data[name] = df
    print(f"  {name}: {len(df)}行")

df_main = data['FI_T1'].copy()
for src in ['FS_Combas', 'FS_Comscfi', 'FI_T5', 'FI_T4', 'FI_T8', 'CG_Capchg', 'CG_Ybasic']:
    extra_cols = [c for c in data[src].columns if c not in ['code', 'date', 'year']]
    df_main = df_main.merge(
        data[src][['code', 'date', 'year'] + extra_cols],
        on=['code', 'date', 'year'], how='left'
    )

print(f"\n合并后: {len(df_main)}行，{df_main['code'].nunique()}家公司，{df_main['year'].min()}-{df_main['year'].max()}")

# ============================================================
# Step 2: 变量构建
# ============================================================
print("\n" + "=" * 60)
print("Step 2: 变量构建")
print("=" * 60)

df = df_main.copy()

# 因变量：剔除 LEV > 1（股东权益为负）
df['LEV'] = df['资产负债率']
before = len(df)
df = df[df['LEV'] <= 1].copy()
print(f"  剔除 LEV>1：{before-len(df)}条，剩余{len(df)}条")

# 自变量
df['SIZE']      = np.log(df['资产总计'].clip(lower=1))
df['ROA']       = df['总资产净利润率（ROA）B']
df['GROWTH']    = df['营业收入增长率B']
df['TANG']      = (df['固定资产净额'].fillna(0) + df['存货净额'].fillna(0)) / df['资产总计'].clip(lower=1)
df['NDTS']      = df['固定资产折旧、油气资产折耗、生产性生物资产折旧'] / df['资产总计'].clip(lower=1)
df['TURN']      = df['总资产周转率B']
df['STATE']     = df['国有股股数'] / df['总股数'].clip(lower=1)
df['INDEP']     = df['其中：独立董事人数'] / df['董事人数'].clip(lower=1)
df['MSHARE_LN'] = np.log(df['管理层持股数量'].clip(lower=0) + 1)

print("各变量非缺失观测：")
for v in VAR_LIST:
    print(f"  {v}: {df[v].notna().sum()}/{len(df)}")

# ============================================================
# Step 3: 缩尾处理（1%/99%）
# ============================================================
print("\n" + "=" * 60)
print("Step 3: 缩尾处理（1%/99%）")
print("=" * 60)

df_w = df.copy()
for v in VAR_LIST:
    s = df_w[v].dropna()
    if len(s) == 0:
        continue
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    df_w.loc[df_w[v].notna(), v] = df_w[v].clip(lower=lo, upper=hi)

df_w = df_w.dropna(subset=['LEV'])
print(f"缩尾后样本量: {len(df_w)}，公司数: {df_w['code'].nunique()}")

# 保存 parquet（engine 脚本读这个文件）
out_cols = ['code', 'year'] + VAR_LIST
df_w[out_cols].to_parquet(PARQUET_PATH, index=False)
print(f"已保存 panel_data.parquet -> {PARQUET_PATH}")

# 同时保存 CSV 供人工核查
df_w[out_cols].to_csv(fr"{OUT_DIR}\panel_data.csv", index=False, encoding='utf-8-sig')

# ============================================================
# Step 4: 描述性统计（调用 engine/descriptive.py）
# ============================================================
print("\n" + "=" * 60)
print("Step 4: 描述性统计 [engine/descriptive.py]")
print("=" * 60)

desc_result = run_engine("descriptive.py", [PARQUET_PATH, "--columns", ",".join(VAR_LIST)])
print(f"  描述统计完成，变量数: {len(desc_result['vars'])}")

# ============================================================
# Step 5: 相关系数矩阵（调用 engine/correlation.py）
# ============================================================
print("\n" + "=" * 60)
print("Step 5: 相关系数矩阵 [engine/correlation.py]")
print("=" * 60)

corr_result = run_engine("correlation.py", [PARQUET_PATH, "--columns", ",".join(VAR_LIST)])
print(f"  相关系数矩阵完成，方法: {corr_result['method']}")

# ============================================================
# Step 6: VIF（调用 engine/diagnostics.py）
# ============================================================
print("\n" + "=" * 60)
print("Step 6: VIF 多重共线性检验 [engine/diagnostics.py]")
print("=" * 60)

diag_config = json.dumps({
    "dv": "LEV",
    "iv": REG_VARS,
    "controls": [],
    "model_type": "ols"
})
try:
    diag_result = run_engine("diagnostics.py", [PARQUET_PATH, diag_config])
    print(f"  VIF 检验完成")
except Exception as e:
    print(f"  VIF 检验失败（将跳过）: {e}")
    diag_result = None

# ============================================================
# Step 7: 混合 OLS（调用 engine/ols.py）
# ============================================================
print("\n" + "=" * 60)
print("Step 7: 混合 OLS [engine/ols.py]")
print("=" * 60)

ols_config = json.dumps({
    "dep_var": "LEV",
    "indep_vars": REG_VARS,
    "control_vars": [],
    "robust_se": True
})
ols_result = run_engine("ols.py", [PARQUET_PATH, ols_config])
print(f"  OLS 完成，N={ols_result['n']}, R2={ols_result['r2']:.4f}")

# ============================================================
# Step 8: 面板固定效应（调用 engine/panel.py，model_type=fe）
# ============================================================
print("\n" + "=" * 60)
print("Step 8: 面板固定效应 [engine/panel.py, fe]")
print("=" * 60)

fe_config = json.dumps({
    "dep_var": "LEV",
    "indep_vars": REG_VARS,
    "control_vars": [],
    "entity_var": "code",
    "time_var": "year",
    "model_type": "fe",
    "cluster_var": "code"
})
fe_result = run_engine("panel.py", [PARQUET_PATH, fe_config])
print(f"  FE 完成，N={fe_result['n']}, R2_within={fe_result.get('r2_within', 'N/A')}")
if fe_result.get('hausman'):
    h = fe_result['hausman']
    print(f"  Hausman: chi2={h['chi2']:.4f}, p={h['p_value']:.4f} → {h['conclusion']}")

# ============================================================
# Step 9: 面板随机效应（调用 engine/panel.py，model_type=re）
# ============================================================
print("\n" + "=" * 60)
print("Step 9: 面板随机效应 [engine/panel.py, re]")
print("=" * 60)

re_config = json.dumps({
    "dep_var": "LEV",
    "indep_vars": REG_VARS,
    "control_vars": [],
    "entity_var": "code",
    "time_var": "year",
    "model_type": "re",
    "cluster_var": "code"
})
re_result = run_engine("panel.py", [PARQUET_PATH, re_config])
print(f"  RE 完成，N={re_result['n']}, R2_overall={re_result.get('r2_overall', 'N/A')}")

# ============================================================
# Step 10: 汇总结果保存
# ============================================================
print("\n" + "=" * 60)
print("Step 10: 汇总结果")
print("=" * 60)

all_results = {
    "descriptive": desc_result,
    "correlation": corr_result,
    "diagnostics": diag_result,
    "ols":         ols_result,
    "fe":          fe_result,
    "re":          re_result,
}

results_path = fr"{OUT_DIR}\all_results.json"
with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"已保存 all_results.json -> {results_path}")
print("\n全部引擎调用完成！")
