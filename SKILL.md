---
name: empirical-research-agent
description: 用于论文写作者快速跑计量分析。当用户提供CSV/Excel数据并提出OLS/面板回归/DID/PSM/调节效应/中介效应/异质性分析等计量需求时使用，自动诊断数据、检查方法适用性、运行分析并按检查清单生成论文可用的解读文字。所有数字来自确定性Python计算引擎，禁止Agent心算或编造。
---

# Empirical Research Agent — 论文实证分析Agent

## 核心原则（最先读）

本skill的架构哲学：**场景识别 > 协议阻断 > 工作流编排 > 引擎计算**。

1. **所有数字必须来自 `engine/` 脚本输出或用户提供的数据文件。** 严禁Agent心算、推断、编造任何数字。
2. **protocols/ 层是阻断型的**：不通过的步骤终止执行或降级输出，不得跳过。
3. **结果解读必须标注可信度标签**：[VERIFIED] / [INFERRED] / [SPECULATIVE]。
4. **不支持的方法不能替代**：用户要求的方法不在 `method_capability.json` 中时，告知"当前版本暂不支持"，不得用近似方法替代。

## 第一层：操作意图路由

收到用户请求后，先按操作意图做互斥分流；凡涉及数据诊断、探索、建模、重跑或报告生成的请求，都进入“标准流水线”，并立刻执行 Step 0 研究阶段识别。`modes/` 决定用户当前研究阶段，`workflows/` 只在研究阶段确定后负责具体方法编排。

按以下优先级判断：

| 优先级 | 用户输入特征 | 路由 | 读哪个文件 |
|---|---|---|
| 1 | 只要求写代码、脚本或命令，不要求运行，不要求输出分析数字 | 代码生成模式 | 跳到对应 `workflows/` 的代码分支，只输出代码 |
| 2 | 只要求解读用户已有结果，不改变量/样本/模型，不重跑 | 结果解读模式 | 读 `protocols/result_validation.md` → `protocols/reporting.md` |
| 3 | 只问该用什么方法，不要求执行、不要求输出数字 | 方法咨询 | 读 `protocols/method_selection.md` → 返回建议（不出数字） |
| 4 | 涉及数据诊断、探索、建模、重跑、报告生成，或意图混合 | 标准流水线 → Step 0 研究阶段识别 | 先读 `protocols/protocol_order.md` → 再按阶段读 `modes/research_explore.md` / `modes/model_execute.md` / `modes/result_iterate.md` |

混合意图规则：

- “帮我写代码并跑一下” → 标准流水线，不走代码生成旁路。
- “帮我解读结果，并把控制变量加上 size 重跑” → 标准流水线 → 结果迭代模式。
- “我有数据，想看某政策效果，该用什么方法并帮我做” → 标准流水线，先 Step 0，再做方法选择和阻断确认。
- “只看看数据” / “帮我看看能做什么” → 标准流水线 → 研究探索模式。

标准流水线内的读取顺序固定为：

1. `protocols/protocol_order.md`
2. 对应 `modes/*.md`
3. `protocols/model_spec.md`
4. 必要的阻断协议：`variable_mapping.md` / `panel_build_plan.md`
5. 对应 `workflows/*.md`

## 操作模式

操作模式和研究阶段不是同一层分类：

- 操作模式负责决定是否进入标准流水线。
- 研究阶段只在标准流水线内部由 `modes/` 识别。

### 模式1：标准流水线（默认）

用户请求涉及数据诊断、探索、建模、重跑或报告生成时，按 `protocols/protocol_order.md` 的顺序执行：

```
[Step 0] research_mode       ← 研究场景识别：读 modes/*.md
  ↓
[P0] anti_hallucination.md   ← 全程生效
  ↓
[P1] data_audit.md           ← 数据质检（不通过→终止）
  ↓
[P2] method_selection.md     ← 选方法 + 查 capability.json
  ↓
[Step 4A] variable_mapping.md ← 变量映射确认（回归前硬阻断）
  ↓
[Step 4B] panel_build_plan.md ← 样本构建确认（多表/面板回归前硬阻断）
  ↓
[workflow]                   ← 执行对应 workflow/*.md
  ↓
[P3] result_validation.md    ← 可信度评级
  ↓
[P4] reporting.md            ← 输出报告
```

#### Step 0：研究阶段识别

在标准流水线开始前，先判断用户处于哪个研究阶段。`modes/` 只管理研究阶段，不承载具体方法编排；具体方法仍由 `workflows/` 负责，阻断规则仍由 `protocols/` 负责，确定性计算仍由 `engine/` 负责。

| 研究场景 | 进入条件 | 行为边界 | 必读文件 |
|---|---|---|---|
| 结果迭代模式 | 有上一轮 `model_spec`，且用户要求修改变量、样本、模型、控制变量、固定效应、标准误或报告口径 | 必须继承上一轮 `model_spec`，只修改用户明确要求调整的部分，并输出 `result_diff` | `modes/result_iterate.md`、`protocols/model_spec.md`、`protocols/result_diff.md` |
| 模型执行模式 | 用户给出最低可执行 `model_spec`，且明确要求跑模型或生成回归报告 | 严格按用户设定执行，不得擅自更换 Y/X、重定义变量方向、扩展研究问题；缺失控制变量、固定效应、标准误或样本方案时进入 Step 4A/4B 确认 | `modes/model_execute.md`、`protocols/model_spec.md` |
| 研究探索模式 | 用户只提供数据、主题或模糊问题，未达到最低可执行 `model_spec` | 只输出候选研究问题、变量映射建议、数据可用性判断和探索性结果；不得生成正式因果结论 | `modes/research_explore.md`、`protocols/model_spec.md` |

默认规则：如果无法判断，默认进入研究探索模式，而不是模型执行模式。

### 模式2：代码生成模式

触发条件：用户只要求写代码、脚本或命令，且不要求运行、不要求输出分析数字。

Agent行为：
- 读对应 `workflows/*.md` 的代码生成分支
- 输出完整可运行的Python脚本
- **不执行脚本，不预判结果，不输出任何数字**
- 如果用户同时要求“跑一下”“生成结果”“输出报告”，改走标准流水线

### 模式3：结果解读模式

触发条件：用户只要求解读已有结果，不修改变量、样本、模型、控制变量、固定效应、标准误或报告口径。

Agent行为：
- 读 `protocols/result_validation.md`
- 读对应的 `resources/` 参考文件
- 只解读用户提供的真实输出，标注可信度标签
- 如果用户要求基于结果继续调整并重跑，改走标准流水线 → 结果迭代模式

### 模式4：方法咨询

触发条件：用户只问方法选择，不要求执行分析、不要求输出统计数字。

Agent行为：
- 读 `protocols/method_selection.md` 决策树
- 返回方法建议和理由
- 不执行任何分析，不输出数字
- 如果用户要求“推荐方法并帮我做”，改走标准流水线

## 标准流水线详细步骤

### Step 0: 研究阶段识别
先读对应 `modes/*.md`，按以下顺序判断用户当前研究阶段：

1. 结果迭代模式：有上一轮 `model_spec`，且用户要求修改变量、样本、模型、控制变量、固定效应、标准误或报告口径。
2. 模型执行模式：用户给出最低可执行 `model_spec`，且明确要求跑模型或生成回归报告。
3. 研究探索模式：用户只提供数据、主题或模糊问题，未达到最低可执行 `model_spec`。

最低可执行 `model_spec` = `dep_var` + `indep_vars` + `method` + `run_intent`。控制变量、固定效应、标准误和样本构建方案可以缺失，但缺失项必须在 Step 4A/4B 中阻断确认，不得由 Agent 自动补全。

如果无法判断，默认进入研究探索模式。识别后生成或继承 `model_spec`，后续所有回归设定以 `protocols/model_spec.md` 为单一记录来源。

### Step 0 边界案例

| 用户请求 | 路径 |
|---|---|
| “我有数据，帮我看看能做什么” | 标准流水线 → 研究探索模式 |
| “用 OLS 看 tax 对 innovation 的影响” | 标准流水线 → 模型执行模式，Step 4A 继续确认变量映射 |
| “基于上一轮，把 X 换成 tax_avoidance” | 标准流水线 → 结果迭代模式 |
| “帮我写 OLS 代码并跑一下” | 标准流水线，不走代码生成旁路 |
| “帮我解读这张回归表，并把控制变量加上 size 重跑” | 标准流水线 → 结果迭代模式 |

### Step 1: 加载数据
```bash
python engine/data_audit.py <file_path>
```
支持 .csv / .xlsx / .parquet / .dta 格式。

### Step 2: 数据质检 [P1]
读取 `engine/data_audit.py` 输出，按 `protocols/data_audit.md` 判断 PASS / WARN / BLOCK。
- BLOCK → 终止，返回质检报告
- WARN → 告知用户风险，等待确认

### Step 3: 方法选择 [P2]
按 `protocols/method_selection.md` 决策树选方法，查 `method_capability.json` 确认可用性和tier层级。

### Step 4A: 变量映射确认（硬阻断，回归类方法不可跳过）
读取 `protocols/variable_mapping.md`。任何回归前必须向用户输出并等待确认：

- Y / X / 控制变量
- 来源表
- 来源字段
- 计算方式
- 经济含义
- 方向说明

尤其要说明：

- Y 是创新投入、创新产出，还是创新质量。
- X 值越大代表税负越重，还是避税程度越高。
- 如果变量经过转换，必须说明对系数方向的影响。

用户确认前不得执行回归。

### Step 4B: 样本构建确认（硬阻断，多表/面板回归不可跳过）
读取 `protocols/panel_build_plan.md`。多表数据回归前必须向用户输出并等待确认：

- 主表
- 合并表
- join key
- join type
- 合并前样本量
- 合并后样本量
- 缺失值处理
- 缩尾处理
- 最终样本量

用户确认前不得执行回归。

如果非交互环境无法确认，报告必须标注：

```text
[WARN] 未经过变量/样本确认，本报告仅为探索性结果，不得作为正式结论。
```

### Step 5: 基线表格（回归类方法默认执行）
在跑用户要求的方法之前，先跑：
```bash
 python engine/descriptive.py <parquet_path> <config>
 python engine/correlation.py <parquet_path> <config>
```

### Step 6: 执行分析
按对应 `workflows/*.md` 的编排执行 `engine/` 脚本。

### Step 7: 结果验证 [P3]
按 `protocols/result_validation.md` 对每条结论标注可信度标签：
- [VERIFIED] → 可进入论文正文
- [INFERRED] → 可进入论文讨论
- [SPECULATIVE] → 不得进入论文正文

### Step 8: 输出报告 [P4]
按 `protocols/reporting.md` 生成三线表 + 解读文字。
按用户场景选择模板：`templates/thesis.md` / `templates/paper.md` / `templates/report.md`。

每份报告开头必须包含“任务卡”：

- 当前研究场景：研究探索 / 模型执行 / 结果迭代
- 完成等级：探索性 / 草稿级 / 已验证
- 是否经过变量确认：是 / 否
- 是否经过样本构建确认：是 / 否
- 是否可作为正式结论：是 / 否

### Step 9（可选）: 导出Word
若用户要求输出Word文档，调用 documents skill 生成 .docx 文件。

## 支持的方法

详见 `method_capability.json`。当前版本支持：

| 层级 | 方法 |
|------|------|
| Free | descriptive, correlation, diagnostics |
| Pro | ols, panel, mediation, moderation, heterogeneity, visualization |
| Premium | did, psm, psm_did, iv(beta), robustness |

rd 为 planned（尚未实现），probit/logit/PCA 等不在能力范围内。

## 护栏

1. 数字必须来自 engine 输出，禁止心算或编造
2. 回归类方法（ols/panel/moderation/mediation/heterogeneity）跑之前必须经过变量映射确认和必要的样本构建确认
3. 解读前必须读对应的 interpretation checklist（在 `resources/` 中），按清单逐项核对
4. 不支持的方法明确告知"当前版本暂不支持"，不强行用近似方法替代
5. 所有结论标注可信度标签 [VERIFIED]/[INFERRED]/[SPECULATIVE]
6. [SPECULATIVE] 标签结论不得进入论文正文建议
7. 输出格式统一按 `protocols/reporting.md` 的三线表标准

## 文件结构

```
empirical-research-agent/
├── SKILL.md                      # 本文件：总入口 + 场景路由 + 模式切换
├── method_capability.json        # 机器可读能力注册表 + 定价层级
├── modes/                        # 研究阶段识别层
│   ├── research_explore.md       # 研究探索模式
│   ├── model_execute.md          # 模型执行模式
│   └── result_iterate.md         # 结果迭代模式
├── protocols/                    # 阻断型协议层
│   ├── protocol_order.md         # 执行顺序与阻断规则
│   ├── anti_hallucination.md     # 反幻觉协议（横切约束）
│   ├── data_audit.md             # 数据质检协议（前置阻断）
│   ├── method_selection.md       # 方法选择决策树（路由决策）
│   ├── variable_mapping.md       # 变量映射确认协议
│   ├── panel_build_plan.md       # 样本构建确认协议
│   ├── model_spec.md             # 模型设定记录协议
│   ├── result_diff.md            # 结果迭代差异协议
│   ├── result_validation.md      # 结果验证与可信度评级（后置阻断）
│   └── reporting.md              # 输出规范（三线表+解读格式）
├── workflows/                    # 编排层（调用engine，不直接计算）
│   ├── descriptive.md            # 描述性分析
│   ├── hypothesis.md             # 假设检验（OLS/面板）
│   ├── causal.md                 # 因果推断（DID/PSM/IV/RD）
│   ├── mechanism.md              # 机制分析（中介/调节）
│   ├── heterogeneity.md          # 异质性分析
│   ├── robustness.md             # 稳健性检验
│   └── visualization.md          # 可视化
├── engine/                       # 确定性Python计算引擎
│   ├── lib/                      # 核心库（stats_core, data_loader, cleaner）
│   ├── data_audit.py             # 数据质检
│   ├── preprocess.py             # 数据预处理
│   ├── descriptive.py            # 描述性统计
│   ├── correlation.py            # 相关系数矩阵
│   ├── ols.py                    # OLS回归
│   ├── panel.py                  # 面板回归（FE/RE+Hausman）
│   ├── did.py                    # 双重差分
│   ├── psm.py                    # 倾向得分匹配
│   ├── iv.py                     # 工具变量 [beta]
│   ├── rd.py                     # 断点回归 [planned]
│   ├── mediation.py              # 中介效应
│   ├── moderation.py             # 调节效应
│   ├── heterogeneity.py          # 异质性分析
│   ├── diagnostics.py            # 回归诊断
│   ├── robustness.py             # 稳健性检验编排器
│   ├── visualization.py          # 可视化
│   └── export.py                 # 导出（Word/Excel/LaTeX）
├── templates/                    # 输出模板
│   ├── thesis.md                 # 学位论文附录
│   ├── paper.md                  # 期刊投稿
│   └── report.md                 # 内部汇报
└── resources/                    # 参考知识
    ├── stata_reference.md        # Stata等价命令对照
    ├── python_reference.md       # Python依赖与接口规范
    └── methodology.md            # 计量方法参考
```

## 示例

### 示例1：标准OLS分析

用户：我有data.csv，想看leverage对roa的影响，控制size和age。

Agent流程：
1. 读 `protocols/protocol_order.md` → 确认标准流水线
2. Step 0 识别为模型执行模式，读 `modes/model_execute.md` + `protocols/model_spec.md`
3. 运行 `engine/data_audit.py data.csv` → 质检通过
4. 读 `protocols/method_selection.md` → 截面数据+影响因素 → hypothesis → ols
5. 查 `method_capability.json` → ols: available, tier=pro
6. Step 4A 变量映射确认，等用户确认
7. Step 4B 如涉及多表/面板构建则样本构建确认，等用户确认
8. 跑 baseline（descriptive + correlation）
9. 跑 `engine/ols.py` → 获得回归结果JSON
10. 读 `protocols/result_validation.md` → 标注可信度标签
11. 读 `protocols/reporting.md` + `templates/paper.md` → 生成任务卡 + 三线表 + 解读

### 示例2：方法咨询

用户：我有企业面板数据，想看某项政策的效果，该用什么方法？

Agent流程：
1. 识别为"方法咨询"模式
2. 读 `protocols/method_selection.md` 决策树 → "有面板+政策时间点" → causal
3. 进一步确认：处理组选择是否随机？→ 分别建议DID或PSM-DID
4. 查 `method_capability.json` → 确认两个方法都available
5. 返回建议：推荐DID（若处理组外生）或PSM-DID（若处理组选择非随机）
6. 不执行任何计算，不输出数字
