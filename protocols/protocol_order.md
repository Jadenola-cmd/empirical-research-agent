# Protocol Order — 协议执行顺序与阻断规则

## 设计原则

protocols/ 层是 **阻断型** 的：不通过的步骤终止执行或降级输出，不得跳过。
这与 modes/ 层的"研究阶段识别"、workflows/ 层的"编排型"和 engine/ 层的"计算型"有本质区别。

## 执行顺序

每次用户请求经过以下关卡，按顺序执行：

```
用户请求
  │
  ├─ [Step 0] modes/*.md          ← 研究场景识别：探索 / 执行 / 迭代
  │     └─ 无法判断 → 默认研究探索模式
  │
  ├─ [P0] anti_hallucination.md  ← 横切约束，全程生效
  │
  ├─ [P1] data_audit.md          ← 前置阻断：数据不通过 → 拒绝执行，返回质检报告
  │     └─ 不通过 → TERMINATE
  │
  ├─ [P2] method_selection.md    ← 路由决策：选方法 → 查 capability.json
  │     └─ 方法不在capability中 → 告知用户"当前版本暂不支持"
  │     └─ 方法tier > 用户tier → 提示升级
  │
  ├─ [Step 4A] variable_mapping.md ← 硬阻断：变量映射未确认 → 不得回归
  │
  ├─ [Step 4B] panel_build_plan.md ← 硬阻断：样本构建未确认 → 不得回归
  │
  ├─ [workflow 执行]             ← 由对应 workflow/*.md 编排 engine/ 调用
  │
  ├─ [P3] result_validation.md   ← 后置阻断：可信度评级 [VERIFIED]/[INFERRED]/[SPECULATIVE]
  │     └─ [SPECULATIVE] 项 → 不进论文正文建议
  │
  └─ [P4] reporting.md           ← 输出规范：三线表 + 解读文字 + 模板选择
```

## 阻断规则速查

| 协议 | 触发时机 | 阻断后果 | 恢复条件 |
|------|---------|---------|---------|
| anti_hallucination | 全程 | 立即终止当前回复，修正后重试 | 提供真实数据或engine输出 |
| data_audit | 用户上传数据后 | 拒绝跑分析，返回质检报告 | 用户修正数据或确认接受风险 |
| method_selection | 选方法时 | 提示"暂不支持"或"需要升级" | 用户选择替代方法或升级tier |
| variable_mapping | 回归前 | 不得执行回归 | 用户确认 Y/X/控制变量、来源、计算方式和方向 |
| panel_build_plan | 多表/面板回归前 | 不得执行回归 | 用户确认主表、合并表、join、缺失值、缩尾和最终样本 |
| result_validation | engine输出后 | [SPECULATIVE]标签项降级处理 | 补充稳健性检验后重新评级 |
| reporting | 生成输出时 | 不阻断，仅格式警告 | 按模板重新排版 |

## 实现约定

- 每个协议文件必须包含明确的"阻断条件"章节
- Agent 执行时必须先读对应协议文件，再执行操作
- 协议之间通过 method_capability.json 共享能力边界信息
- 用户可以通过"跳过质检"明确要求绕过 P1（但 Agent 必须在输出中标注风险）
- 用户不能跳过变量映射确认和样本构建确认来获得正式回归结论；非交互环境只能降级为探索性结果
