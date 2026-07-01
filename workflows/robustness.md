# Workflow: Robustness Checks — 稳健性检验

## 触发条件

- 用户问"结果稳不稳？"、"稳健性检验"、"换变量/换方法试试"
- method_selection 决策树路由到 robustness
- 用户完成主回归后主动建议

## 前置条件

- [ ] 主回归已完成（有 engine 输出）
- [ ] 主回归方法在 capability.json 中有对应的 robustness_checks 列表
- [ ] 用户 tier >= premium

## 执行逻辑

本 workflow 不独立计算，而是**编排** capability.json 中对应方法的 robustness_checks 列表。

### 查询稳健性检验项

从 method_capability.json 中读取当前方法的 `robustness_checks` 字段：

| 方法 | 稳健性检验项 |
|------|-------------|
| ols | winsorize, vif, breusch_pagan, reset_test |
| panel | cluster_se, lagged_iv, fe_vs_re |
| did | parallel_trends, placebo_test, staggered_did |
| psm | caliper_sensitivity, alternative_matching, rosenbaum_bounds |
| iv | weak_iv_test, overidentification_test |
| mediation | bootstrap_mediation, alternative_mediator |
| moderation | mean_centering, alternative_moderator |
| heterogeneity | alternative_grouping, interaction_test |

### 执行

```bash
python engine/robustness.py <parquet_path> --method <primary_method> --checks <check1,check2,...> [--model_params <primary_model_params>]
```

robustness.py 负责：
1. 读取主回归的参数配置
2. 对每个检验项执行相应操作（缩尾/换变量/换方法/换标准误）
3. 生成对比表（原始结果 vs 各稳健性检验结果）

### 输出

**稳健性检验汇总表**：

| 检验项 | 核心系数 | 方向 | 显著性 | 结论 |
|--------|---------|------|--------|------|
| 原始结果 | -0.532 | 负 | *** | — |
| 缩尾1% | -0.518 | 负 | *** | 通过 |
| 替换变量度量 | -0.487 | 负 | ** | 通过 |
| 聚类标准误 | -0.532 | 负 | ** | 通过 |

**解读要点**：
- 核心系数的方向和显著性在稳健性检验中是否保持一致？
- 哪些检验项的结果有变化？变化是否影响核心结论？
- 综合评定：结果是 **稳健** / **基本稳健** / **不够稳健**

## 可信度升级规则

- 全部稳健性检验通过 → 主回归核心结论可从 [INFERRED] 升级到 [VERIFIED]
- 部分通过 → 维持原评级，注明未通过的检验项
- 核心检验不通过 → 主回归结论降级到 [SPECULATIVE]

## 输出模板

使用 `templates/paper.md`（作为主回归报告的第六章节"稳健性检验"）。

## 完成检查

- [ ] 从 capability.json 查询了正确的稳健性检验列表
- [ ] 每个检验项有明确的结果
- [ ] 稳健性汇总表
- [ ] 综合评定（稳健/基本稳健/不够稳健）
- [ ] 可信度标签更新
- [ ] 所有数字可溯源到 engine 输出
