# Workflow: Heterogeneity Analysis — 异质性分析

## 触发条件

- 用户问"这个效应在不同组里一样吗？"、"分组看有什么不同？"、"异质性"
- method_selection 决策树路由到 heterogeneity

## 前置检查

- [ ] data_audit 已通过
- [ ] 方法在 method_capability.json 中 status=available
- [ ] 用户 tier >= pro
- [ ] 分组变量类别数 2-6（>6 建议用 median/quantile 分法）

## 执行步骤

### Step 1: 变量确认（不可跳过）

额外列出：
- 分组变量 + 分组方式（category / median / quantile）
- 每个分组的预期样本量

### Step 2: 基线表格（全样本 descriptive + correlation）

### Step 3: 执行异质性分析

```bash
 python engine/heterogeneity.py <parquet_path> <config>
```

输出包含：
- 每组回归系数
- Chow检验（组间系数差异显著性）
- 分组样本量

### Step 4: 分组回归对比表

多列对比三线表：
| 变量 | (1) 全样本 | (2) {组1标签} | (3) {组2标签} |
|---|---|---|---|

若某组样本量 < 30，标注"该组样本量不足，结果仅供参考"。

### Step 5: 结果解读

重点回答：
- 核心自变量的效应在不同组间是否有显著差异？
- 差异的经济含义是什么？
- 这对研究问题意味着什么？

## 分组方式选择

| 分组变量类型 | 推荐方式 | 说明 |
|-------------|---------|------|
| 二值分类（0/1） | category | 直接分组 |
| 有序分类（2-6类） | category | 直接分组 |
| 有序分类（>6类） | median | 中位数二分 |
| 连续变量 | median / quantile | 中位数二分或三分位数 |

## 输出模板

使用 `templates/paper.md`。

## 完成检查

- [ ] 变量确认已获用户确认
- [ ] 分组方式合理（类别数不超标）
- [ ] 多列对比三线表
- [ ] Chow检验结果
- [ ] 异质性解读（讲清楚"谁受影响更大/更小"）
- [ ] 可信度标签（小样本组降级）
- [ ] 所有数字可溯源到 engine 输出
