# Stata Reference — Stata等价命令参考

## 用途

当用户熟悉Stata语法时，提供Stata等价命令对照，帮助理解engine输出结果。

## 方法对照表

### 描述性统计
| engine | Stata等价命令 |
|--------|-------------|
| descriptive.py | `summarize varlist, detail` |
| correlation.py | `pwcorr varlist, sig star(0.05)` |

### OLS回归
| engine | Stata等价命令 |
|--------|-------------|
| ols.py (se_type=HC1) | `reg y x1 x2, robust` |
| ols.py (无稳健) | `reg y x1 x2` |
| diagnostics.py (VIF) | `vif` |
| diagnostics.py (BP) | `estat hettest` |

### 面板回归
| engine | Stata等价命令 |
|--------|-------------|
| panel.py (FE) | `xtreg y x1 x2, fe robust` |
| panel.py (RE) | `xtreg y x1 x2, re robust` |
| Hausman检验 | `hausman fe re` |
| cluster SE | `xtreg y x1 x2, fe cluster(id)` |

### 因果推断
| engine | Stata等价命令 |
|--------|-------------|
| did.py | `reg y treat##post, robust` |
| did.py (event_study) | `eventdd y x1 x2, timevar(t) method(fe) cluster(id)` |
| psm.py (nearest) | `psmatch2 treat x1 x2, out(y) neighbor(1) caliper(0.05)` |
| psm.py (kernel) | `psmatch2 treat x1 x2, out(y) kernel` |
| iv.py | `ivregress 2sls y (x = z), robust` |
| rd.py | `rdrobust y score, c(0)` |

### 机制分析
| engine | Stata等价命令 |
|--------|-------------|
| mediation.py | `sgmediation y, iv(x) mv(m) cv(c1 c2)` |
| moderation.py | `reg y c.x##c.z, robust` + `margins, dydx(x) at(z=(low high))` |

### 异质性分析
| engine | Stata等价命令 |
|--------|-------------|
| heterogeneity.py (category) | `bysort group: reg y x1 x2, robust` |

## 结果字段对照

| engine JSON字段 | Stata输出对应 |
|----------------|-------------|
| coef | Coefficient (β) |
| se | Std. Err. |
| t_stat | t |
| p_value | P>|t| |
| r2 | R-squared |
| f_stat | F |
| n | Number of obs |
| hausman.chi2 | chi2 |
| hausman.pvalue | Prob>chi2 |
