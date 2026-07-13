# Result Diff Protocol — 结果迭代差异说明

## 位置

结果迭代模式的必经协议。每次基于上一轮结果调整后，报告必须包含 `result_diff`。

## 必填字段

```yaml
result_diff:
  base_result: "上一轮结果或模型编号"
  changed:
    - field: ""
      before: ""
      after: ""
      reason: "用户明确要求"
  unchanged:
    - "dep_var"
    - "indep_vars"
    - "standard_error"
  impact_scope: "仅影响样本/变量/模型/报告口径中的哪些部分"
```

## 使用规则

- 只列用户本轮明确要求修改的内容。
- 未提及字段必须列入 unchanged 或在文字中说明保持不变。
- 如果本轮修改导致 Step 4A/4B 需要重新确认，必须先阻断确认。
- 不得用 result_diff 包装一次全新的研究设计。

## 阻断条件

- 没有上一轮 `model_spec`。
- 本轮修改范围不清。
- Agent 自行加入用户未要求的变量、样本或模型设定。
