# Model Spec Protocol — 模型设定记录

## 位置

标准流水线 Step 0 之后生成或继承，Step 4A/4B 之前锁定。

## 目的

`model_spec` 是模型执行和结果迭代的单一设定来源，用于避免在 Y/X、样本、控制变量、固定效应和标准误之间来回漂移。

## 推荐字段

```yaml
research_mode: 研究探索 | 模型执行 | 结果迭代
research_question: ""
data_files: []
dep_var: ""
indep_vars: []
control_vars: []
method: ""
run_intent: false
fixed_effects: []
standard_error: ""
cluster_var: ""
sample_filter: ""
merge_plan: ""
missing_policy: ""
winsorize_policy: ""
confirmed:
  variable_mapping: false
  sample_build: false
```

## 最低可执行 model_spec

进入模型执行模式的最低条件是同时具备：

| 字段 | 含义 |
|---|---|
| `dep_var` | 因变量 Y |
| `indep_vars` | 至少一个核心自变量 X |
| `method` | 用户明确要求的方法，或足以由 `method_selection.md` 判定的方法类型 |
| `run_intent` | 用户明确要求执行模型、跑回归、重跑或生成回归报告 |

控制变量、固定效应、标准误、聚类变量、样本筛选、合并方案、缺失值处理和缩尾方案可以缺失。缺失时不得由 Agent 自动补全，必须在 Step 4A/4B 阻断确认。

## 使用规则

- 研究探索模式可以输出 `model_spec` 草案，但不得把草案当作已确认设定执行正式回归。
- 模型执行模式必须至少满足“最低可执行 model_spec”。
- 结果迭代模式必须继承上一轮 `model_spec`，只修改用户明确要求调整的字段。
- `model_spec` 与用户原始设定冲突时，以用户明确设定为准，并提示冲突点。
- “写代码并跑一下”“解读后重跑”“推荐方法并帮我做”等混合意图，必须设置 `run_intent: true` 并进入标准流水线。

## 阻断条件

- 回归类方法缺少 Y、X、方法设定或执行意图时，不得进入模型执行。
- 用户明确设定与 Agent 推断不一致时，不得静默覆盖。
- 结果迭代无法找到上一轮 `model_spec` 时，不得假装继承。
