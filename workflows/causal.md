# Workflow: Causal Inference — 因果推断（DID / PSM / PSM-DID / IV / RD）

## 触发条件

- 用户问"X导致Y吗？"、"政策效果"、"处理效应"、"因果识别"
- method_selection 决策树路由到 causal

## 前置检查

- [ ] data_audit 已通过
- [ ] 方法在 method_capability.json 中 status=available 或 beta
- [ ] 用户 tier >= 方法 tier（causal 方法需要 premium）
- [ ] 数据满足对应方法的前置条件（见 data_audit.md 方法匹配检查）

## 方法分支

### 分支 A: DID（双重差分）

**前置条件**：面板结构 + 二值处理变量 + 前/后时期

**执行**：
```bash
 python engine/did.py <parquet_path> <config>
```

**附加输出**：
- 平行趋势检验图（event study）
- 安慰剂检验（可选）

### 分支 B: PSM（倾向得分匹配）

**前置条件**：二值处理变量 + 足够协变量

**执行**：
```bash
 python engine/psm.py <parquet_path> <config>
```

**附加输出**：
- 平衡性检验表（匹配前后协变量差异）
- 倾向得分分布图
- ATT（平均处理效应）

### 分支 C: PSM-DID

**前置条件**：面板 + 二值处理 + 协变量

**执行**：
```bash
 python engine/psm.py <parquet_path> <config>
```

### 分支 D: IV（工具变量）[beta]

**前置条件**：工具变量 + 内生回归元

**执行**：
```bash
 python engine/iv.py <parquet_path> <config>
```

**附加输出**：
- 第一阶段F统计量（弱工具变量检验）
- Wu-Hausman内生性检验

### 分支 E: RD（断点回归）[planned]

状态为 planned，告知用户"该方法尚未实现"。

## 输出要求

按 reporting.md 生成报告，额外包含：
- 识别策略说明（为什么这个因果识别策略适用于当前数据）
- 处理效应估计 + 可信度标签
- 稳健性检验建议（引用 capability.json 中对应方法的 robustness_checks）

## 输出模板

使用 `templates/paper.md`。

## 完成检查

- [ ] 识别策略已说明
- [ ] 方法前置条件已验证
- [ ] 处理效应系数 + 标准误
- [ ] 对应方法的附加检验（平行趋势/平衡性/第一阶段F等）
- [ ] 因果结论 + 可信度标签（因果推断类结论需格外保守评级）
- [ ] 所有数字可溯源到 engine 输出
