# 回归表期刊格式验收用例

输入：

- `golden_outputs/ols_corrected.json`
- `golden_outputs/panel_corrected.json`

任务：

基于上述 engine JSON 输出生成论文期刊格式回归表。

必须满足：

- 表号使用 `Table 2: Baseline Regression Results` 或中文等价表号。
- 列名至少包含 `(1) 混合 OLS` 和 `(2) 固定效应 FE`。
- 每个变量系数与显著性星号同格，例如 `-0.405**`。
- t 值单独在下一行，并用括号包裹，例如 `(-2.145)`。
- 表底包含 `N`、`R²` 或 `Within R²`、`F统计量` 或模型检验项。
- 表注必须说明标准误类型，例如 `robust(HC1)`、`clustered`。
- 若报告 Hausman，必须写入模型选择说明，并标注可信度标签。
- 每条结果解读必须包含 `[VERIFIED]`、`[INFERRED]` 或 `[SPECULATIVE]`。
- 默认不得输出 Tab 分隔复制块；仅用户明确要求时才追加 TSV。

失败判定：

- 只输出自然语言结论，不输出回归表。
- 把 t 值和系数挤在同一格，或漏掉显著性星号。
- 未说明标准误类型。
- 默认输出 Tab 分隔复制块。
- 使用非 engine JSON 中的数字。
