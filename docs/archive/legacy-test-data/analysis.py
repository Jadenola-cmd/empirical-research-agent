"""资本结构影响因素 - 完整实证分析脚本（修复版）
方法：描述性统计 + 相关系数 + 混合OLS + 面板FE/RE + Hausman
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Step 1: 读取所有数据（保留原始列名，构建merge key映射）
# ============================================================

print("=" * 60)
print("Step 1: 数据读取")
print("=" * 60)

files = {
    'FI_T1': {
        'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T1.xlsx',
        'code_col': '股票代码',
        'date_col': '截止日期',
    },
    'FI_T4': {
        'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T4.xlsx',
        'code_col': '股票代码',
        'date_col': '截止日期',
    },
    'FI_T5': {
        'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T5.xlsx',
        'code_col': '股票代码',
        'date_col': '截止日期',
    },
    'FI_T8': {
        'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T8.xlsx',
        'code_col': '股票代码',
        'date_col': '会计年度',
    },
    'FS_Combas': {
        'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FS_Combas.xlsx',
        'code_col': '证券代码',
        'date_col': '会计期间',
    },
    'FS_Comscfi': {
        'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FS_Comscfi.xlsx',
        'code_col': '证券代码',
        'date_col': '会计期间',
    },
    'CG_Capchg': {
        'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/CG_Capchg.xlsx',
        'code_col': 'code',
        'date_col': 'date',
    },
    'CG_Ybasic': {
        'path': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/CG_Ybasic.xlsx',
        'code_col': '证券代码',
        'date_col': '统计截止日期',
    },
}

data = {}
for name, cfg in files.items():
    df = pd.read_excel(cfg['path'])
    df = df.rename(columns={cfg['code_col']: 'code', cfg['date_col']: 'date'})
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    data[name] = df
    print(f"  {name}: {len(df)}行, 列: {list(df.columns)[:6]}")

# ============================================================
# Step 2: 合并数据
# ============================================================

print("\n" + "=" * 60)
print("Step 2: 数据合并")
print("=" * 60)

df_main = data['FI_T1'].copy()
print(f"基准 FI_T1: {len(df_main)} 行, 公司数: {df_main['code'].nunique()}")

# FS_Combas
cols = [c for c in data['FS_Combas'].columns if c not in ['code','date','year']]
df_main = df_main.merge(
    data['FS_Combas'][['code','date','year'] + cols],
    on=['code','date','year'], how='left'
)
print(f"  合并 FS_Combas 后: 固定资产净额非缺失 = {df_main['固定资产净额'].notna().sum()}")

# FS_Comscfi
cols = [c for c in data['FS_Comscfi'].columns if c not in ['code','date','year']]
df_main = df_main.merge(
    data['FS_Comscfi'][['code','date','year'] + cols],
    on=['code','date','year'], how='left'
)
print(f"  合并 FS_Comscfi 后: 折旧非缺失 = {df_main['固定资产折旧、油气资产折耗、生产性生物资产折旧'].notna().sum()}")

# FI_T5
cols = [c for c in data['FI_T5'].columns if c not in ['code','date','year']]
df_main = df_main.merge(
    data['FI_T5'][['code','date','year'] + cols],
    on=['code','date','year'], how='left'
)
print(f"  合并 FI_T5 后: ROA非缺失 = {df_main['总资产净利润率（ROA）B'].notna().sum()}")

# FI_T4
cols = [c for c in data['FI_T4'].columns if c not in ['code','date','year']]
df_main = df_main.merge(
    data['FI_T4'][['code','date','year'] + cols],
    on=['code','date','year'], how='left'
)
print(f"  合并 FI_T4 后: 总资产周转率非缺失 = {df_main['总资产周转率B'].notna().sum()}")

# FI_T8
cols = [c for c in data['FI_T8'].columns if c not in ['code','date','year']]
df_main = df_main.merge(
    data['FI_T8'][['code','date','year'] + cols],
    on=['code','date','year'], how='left'
)
print(f"  合并 FI_T8 后: 营收增长率非缺失 = {df_main['营业收入增长率B'].notna().sum()}")

# CG_Capchg
cols = [c for c in data['CG_Capchg'].columns if c not in ['code','date','year']]
df_main = df_main.merge(
    data['CG_Capchg'][['code','date','year'] + cols],
    on=['code','date','year'], how='left'
)
print(f"  合并 CG_Capchg 后: 国有股股数非缺失 = {df_main['国有股股数'].notna().sum()}")

# CG_Ybasic
cols = [c for c in data['CG_Ybasic'].columns if c not in ['code','date','year']]
df_main = df_main.merge(
    data['CG_Ybasic'][['code','date','year'] + cols],
    on=['code','date','year'], how='left'
)
print(f"  合并 CG_Ybasic 后: 董事人数非缺失 = {df_main['董事人数'].notna().sum()}")

print(f"\n合并后总行数: {len(df_main)}")
print(f"公司数: {df_main['code'].nunique()}")
print(f"年份范围: {df_main['year'].min()} - {df_main['year'].max()}")

# ============================================================
# Step 3: 变量构建
# ============================================================

print("\n" + "=" * 60)
print("Step 3: 变量构建")
print("=" * 60)

df = df_main.copy()

# 因变量：剔除资产负债率 > 1 的异常样本（股东权益为负，资本结构无意义）
df['LEV'] = df['资产负债率']
df = df[df['LEV'] <= 1].copy()
print(f"  剔除 LEV > 1 后剩余: {len(df)} 条（剔除 {(190-len(df))} 条）")
print(f"  剩余公司数: {df['code'].nunique()}")

# 自变量
df['SIZE'] = np.log(df['资产总计'].clip(lower=1))
df['ROA'] = df['总资产净利润率（ROA）B']
df['GROWTH'] = df['营业收入增长率B']
df['TANG'] = (df['固定资产净额'].fillna(0) + df['存货净额'].fillna(0)) / df['资产总计'].clip(lower=1)
df['NDTS'] = df['固定资产折旧、油气资产折耗、生产性生物资产折旧'] / df['资产总计'].clip(lower=1)
df['TURN'] = df['总资产周转率B']
df['STATE'] = df['国有股股数'] / df['总股数'].clip(lower=1)

# 独立董事比例
df['INDEP'] = df['其中：独立董事人数'] / df['董事人数'].clip(lower=1)
# 管理层持股比例
df['MSHARE'] = df['管理层持股数量'] / df['总股数'].clip(lower=1)
df['MSHARE_LN'] = np.log(df['管理层持股数量'].clip(lower=0) + 1)

# 查看各变量缺失情况
var_list = ['LEV','SIZE','ROA','GROWTH','TANG','NDTS','TURN','STATE','INDEP','MSHARE_LN']
print("各变量非缺失观测数：")
for v in var_list:
    n = df[v].notna().sum()
    print(f"  {v}: {n} / {len(df)}")

# ============================================================
# Step 4: 缩尾处理（1%/99%）
# ============================================================

print("\n" + "=" * 60)
print("Step 4: 缩尾处理（1%/99%）")
print("=" * 60)

df_w = df.copy()
winsor_vars = ['LEV','SIZE','ROA','GROWTH','TANG','NDTS','TURN','STATE','INDEP','MSHARE_LN']

for v in winsor_vars:
    s = df_w[v].dropna()
    if len(s) == 0:
        continue
    low = s.quantile(0.01)
    high = s.quantile(0.99)
    df_w.loc[df_w[v].notna(), v] = df_w[v].clip(lower=low, upper=high)

df_w = df_w.dropna(subset=['LEV'])
print(f"缩尾后样本量: {len(df_w)}")
print(f"公司数: {df_w['code'].nunique()}")

# 保存合并数据
out_cols = ['code','date','year','LEV','SIZE','ROA','GROWTH','TANG','NDTS','TURN','STATE','INDEP','MSHARE_LN']
out_cols = [c for c in out_cols if c in df_w.columns]
df_w[out_cols].to_csv(
    'D:/00_Workspace/99_Sandbox/empirical技能-test/test-data/panel_data.csv',
    index=False, encoding='utf-8-sig'
)
print("已保存 panel_data.csv")

# ============================================================
# Step 5: 描述性统计
# ============================================================

print("\n" + "=" * 60)
print("Step 5: 描述性统计")
print("=" * 60)

desc_vars = ['LEV','SIZE','ROA','GROWTH','TANG','NDTS','TURN','STATE','INDEP','MSHARE_LN']
desc = df_w[desc_vars].describe().T[['count','mean','std','min','25%','50%','75%','max']]
print(desc.round(4).to_string())

desc.round(4).to_csv('D:/00_Workspace/99_Sandbox/empirical技能-test/test-data/descriptive_stats.csv')

# ============================================================
# Step 6: 相关系数矩阵
# ============================================================

print("\n" + "=" * 60)
print("Step 6: Pearson 相关系数矩阵")
print("=" * 60)

corr = df_w[desc_vars].corr()
print(corr.round(4).to_string())
corr.round(4).to_csv('D:/00_Workspace/99_Sandbox/empirical技能-test/test-data/correlation_matrix.csv')

# 检查是否有高相关（>0.7）
print("\n高相关检查（|r| > 0.7）：")
high_corr = []
for i in range(len(desc_vars)):
    for j in range(i+1, len(desc_vars)):
        v1, v2 = desc_vars[i], desc_vars[j]
        r = corr.loc[v1, v2]
        if abs(r) > 0.7:
            print(f"  {v1} ~ {v2}: {r:.4f}")
            high_corr.append((v1, v2, r))
if not high_corr:
    print("  无（所有 |r| < 0.7）")

# ============================================================
# Step 7: 混合OLS回归
# ============================================================

print("\n" + "=" * 60)
print("Step 7: 混合OLS回归（Pooled OLS）")
print("=" * 60)

import statsmodels.api as sm

reg_vars = ['SIZE','ROA','GROWTH','TANG','NDTS','TURN','STATE','INDEP','MSHARE_LN']
df_reg = df_w[['code','year','LEV'] + reg_vars].dropna()
N = len(df_reg)
N_firm = df_reg['code'].nunique()
N_year = df_reg['year'].nunique()
print(f"回归样本量: {N}（{N_firm}家公司 × {N_year}年）")

X = sm.add_constant(df_reg[reg_vars])
y = df_reg['LEV']
model_ols = sm.OLS(y, X).fit()

print("\n--- 混合OLS回归结果 ---")
print(model_ols.summary().tables[1])
print(f"\nR2 = {model_ols.rsquared:.4f}")
print(f"Adj R2 = {model_ols.rsquared_adj:.4f}")
print(f"F = {model_ols.fvalue:.4f}, p = {model_ols.f_pvalue:.4f}")

# 保存结果（论文三线表格式）
ols_coef = pd.DataFrame({
    'variable': model_ols.params.index,
    'coef': model_ols.params.values,
    'std_err': model_ols.bse.values,
    't_value': model_ols.tvalues.values,
    'p_value': model_ols.pvalues.values,
})
ols_coef['sig'] = ols_coef['p_value'].apply(
    lambda p: '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.1 else ''))
)
ols_coef.to_csv('D:/00_Workspace/99_Sandbox/empirical技能-test/test-data/ols_results.csv', index=False)
print("\n已保存 ols_results.csv")

# ============================================================
# Step 8: VIF检验
# ============================================================

print("\n" + "=" * 60)
print("Step 8: VIF 多重共线性检验")
print("=" * 60)

from statsmodels.stats.outliers_influence import variance_inflation_factor

X_vif = sm.add_constant(df_reg[reg_vars])
vif_data = pd.DataFrame()
vif_data['variable'] = X_vif.columns
vif_data['VIF'] = [variance_inflation_factor(X_vif.values, i) for i in range(X_vif.shape[1])]
print(vif_data.round(2).to_string())
vif_data.round(2).to_csv('D:/00_Workspace/99_Sandbox/empirical技能-test/test-data/vif_results.csv', index=False)
print("\n已保存 vif_results.csv")

# ============================================================
# Step 9: 面板回归（FE/RE + Hausman）
# ============================================================

print("\n" + "=" * 60)
print("Step 9: 面板回归（FE/RE + Hausman）")
print("=" * 60)

try:
    from linearmodels import PanelOLS, RandomEffects
    
    df_panel = df_reg.copy().set_index(['code','year'])
    X_panel = df_panel[reg_vars]
    y_panel = df_panel['LEV']
    
    # 固定效应
    model_fe = PanelOLS(y_panel, X_panel, entity_effects=True, time_effects=False)
    result_fe = model_fe.fit(cov_type='clustered', cluster_entity=True)
    
    print("\n--- 固定效应（FE）结果 ---")
    print(result_fe.summary)
    
    # 随机效应
    model_re = RandomEffects(y_panel, X_panel)
    result_re = model_re.fit(cov_type='clustered', cluster_entity=True)
    
    print("\n--- 随机效应（RE）结果 ---")
    print(result_re.summary)
    
    # Hausman检验
    print("\n--- Hausman 检验 ---")
    try:
        hausman = result_fe.hausman(result_re)
        print(hausman)
    except Exception as e:
        print(f"Hausman检验失败: {e}")
    
    # 保存FE结果
    fe_coef = pd.DataFrame({
        'variable': result_fe.params.index,
        'coef': result_fe.params.values,
        'std_err': result_fe.std_errors.values,
        't_value': result_fe.tstats.values,
        'p_value': result_fe.pvalues.values,
    })
    fe_coef['sig'] = fe_coef['p_value'].apply(
        lambda p: '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.1 else ''))
    )
    fe_coef.to_csv('D:/00_Workspace/99_Sandbox/empirical技能-test/test-data/fe_results.csv', index=False)
    
    # 保存RE结果
    re_coef = pd.DataFrame({
        'variable': result_re.params.index,
        'coef': result_re.params.values,
        'std_err': result_re.std_errors.values,
        't_value': result_re.tstats.values,
        'p_value': result_re.pvalues.values,
    })
    re_coef['sig'] = re_coef['p_value'].apply(
        lambda p: '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.1 else ''))
    )
    re_coef.to_csv('D:/00_Workspace/99_Sandbox/empirical技能-test/test-data/re_results.csv', index=False)
    
    print("\n已保存 fe_results.csv 和 re_results.csv")
    print(f"\nFE: R2_within = {result_fe.rsquared_within:.4f}")
    print(f"RE: R2_overall = {result_re.rsquared:.4f}")
    
except Exception as e:
    print(f"面板回归出错: {e}")
    import traceback; traceback.print_exc()

print("\n" + "=" * 60)
print("全部分析完成！")
print("=" * 60)
print("输出文件:")
print("  - panel_data.csv      合并后面板数据")
print("  - descriptive_stats.csv  描述性统计")
print("  - correlation_matrix.csv 相关系数矩阵")
print("  - ols_results.csv       混合OLS结果")
print("  - vif_results.csv       VIF检验结果")
print("  - fe_results.csv        固定效应结果")
print("  - re_results.csv        随机效应结果")
