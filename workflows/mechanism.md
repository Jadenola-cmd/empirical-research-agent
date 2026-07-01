# Workflow: Mechanism Analysis — 机制分析（中介效应 / 调节效应）

## 触发条件

- 用户问"X通过什么渠道影响Y？"、"M是中介吗？"、"Z调节了X-Y关系吗？"
- method_selection 决策树路由到 mechanism

## 前置检查

- [ ] data_audit 已通过
- [ ] 方法在 method_capability.json 中 status=available
- [ ] 用户 tier >= pro

## 分支 A: 中介效应（Mediation）

### 前置条件
- 中介变量 M 为连续数值型
- Y 为连续变量
- 理论上有 X→M→Y 的逻辑链

### 执行

**Step 1: 变量确认**（不可跳过，同 hypothesis.md 的确认流程）

**Step 2: 基线表格**（descriptive + correlation）

**Step 3: Baron-Kenny三步法**
```bash
 python engine/mediation.py <parquet_path> <config>
```

输出包含：
- Step 1: Y ~ X（总效应 c）
- Step 2: M ~ X（路径 a）
- Step 3: Y ~ X + M（直接效应 c'' + 路径 b）
- Sobel检验：间接效应 a×b 的显著性

### 结果判定

| 情况 | 判定 | 可信度 |
|------|------|--------|
| a、b、c均显著，c''不显著 | 完全中介 | [VERIFIED] |
| a、b、c均显著，c''显著但系数减小 | 部分中介 | [VERIFIED] |
| a或b不显著，Sobel显著 | 间接效应存在 | [INFERRED] |
| a或b不显著，Sobel不显著 | 中介效应不显著 | [VERIFIED] |

### 附加输出
- 中介路径汇总表（c/a/b/c'' + 显著性）
- Sobel检验结果

## 分支 B: 调节效应（Moderation）

### 前置条件
- 调节变量 Z 为数值型或二值分类
- Y 为连续变量

### 执行

**Step 1: 变量确认**（不可跳过）

**Step 2: 基线表格**

**Step 3: 调节效应分析**
```bash
 python engine/moderation.py <parquet_path> <config>
```

输出包含：
- 无交互项模型（主效应）
- 有交互项模型（交互项 X×Z 的系数和显著性）
- 简单斜率检验（Z在均值±1SD处的X→Y斜率）

### 结果判定

- 交互项显著 → 调节效应存在 [VERIFIED]
- 交互项显著 + 简单斜率方向变化 → 调节效应有意义 [VERIFIED]
- 交互项不显著 → 调节效应不存在 [VERIFIED]

## 输出模板

使用 `templates/paper.md`。

## 完成检查

- [ ] 变量确认已获用户确认
- [ ] 中介：三步回归 + Sobel检验 + 路径汇总表
- [ ] 调节：主效应 + 交互项 + 简单斜率
- [ ] 机制解读文字（讲清楚"X如何影响Y"的故事线）
- [ ] 可信度标签（中介效应结论需要更保守评级）
- [ ] 所有数字可溯源到 engine 输出
