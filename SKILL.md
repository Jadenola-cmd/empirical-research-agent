---
name: empirical-research-agent
description: 用于论文写作者快速跑计量分析。当用户提供CSV/Excel数据并提出OLS/面板回归/DID/PSM/调节效应/中介效应/异质性分析等计量需求时使用，自动诊断数据、检查方法适用性、运行分析并按检查清单生成论文可用的解读文字。所有数字来自确定性Python计算引擎，禁止Agent心算或编造。
---

# Empirical Research Agent — 论文实证分析Agent

## 核心原则（最先读）

本skill的架构哲学：**协议阻断 > 工作流编排 > 引擎计算**。

1. **所有数字必须来自 `engine/` 脚本输出或用户提供的数据文件。** 严禁Agent心算、推断、编造任何数字。
2. **protocols/ 层是阻断型的**：不通过的步骤终止执行或降级输出，不得跳过。
3. **结果解读必须标注可信度标签**：[VERIFIED] / [INFERRED] / [SPECULATIVE]。
4. **不支持的方法不能替代**：用户要求的方法不在 `method_capability.json` 中时，告知"当前版本暂不支持"，不得用近似方法替代。

## 场景路由

收到用户请求后，按以下逻辑分流：

| 用户输入特征 | 路由 | 读哪个文件 |
|---|---|---|
| 有数据文件 + 分析需求 | 标准流水线 | 先读 `protocols/protocol_order.md` |
| "帮我写XX方法的代码" | 代码生成模式 | 跳到对应 `workflows/` 的代码分支，只输出代码 |
| "帮我解读这个结果" | 结果解读模式 | 读 `protocols/result_validation.md` → `protocols/reporting.md` |
| "该用什么方法？" | 方法咨询 | 读 `protocols/method_selection.md` → 返回建议（不出数字） |
| "只看看数据" | 探索模式 | 读 `workflows/descriptive.md` |

## 操作模式

### 模式1：标准流水线（默认）

用户提供数据文件和分析需求时，按 `protocols/protocol_order.md` 的顺序执行：

```
[P0] anti_hallucination.md  ← 全程生效
  ↓
[P1] data_audit.md          ← 数据质检（不通过→终止）
  ↓
[P2] method_selection.md    ← 选方法 + 查 capability.json
  ↓
[workflow]                  ← 执行对应 workflow/*.md
  ↓
[P3] result_validation.md   ← 可信度评级
  ↓
[P4] reporting.md           ← 输出报告
```

### 模式2：代码生成模式

触发词："帮我写代码"、"只写代码"、"给我Python脚本"

Agent行为：
- 读对应 `workflows/*.md` 的代码生成分支
- 输出完整可运行的Python脚本
- **不执行脚本，不预判结果，不输出任何数字**

### 模式3：结果解读模式

触发词："帮我解读"、"看看这个结果"、"这个结果什么意思"

Agent行为：
- 读 `protocols/result_validation.md`
- 读对应的 `resources/` 参考文件
- 只解读用户提供的真实输出，标注可信度标签

### 模式4：方法咨询

触发词："该用什么方法"、"方法选择"、"这个数据适合什么方法"

Agent行为：
- 读 `protocols/method_selection.md` 决策树
- 返回方法建议和理由
- 不执行任何分析，不输出数字

## 标准流水线详细步骤

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

### Step 4: 变量确认（关键步骤，回归类方法不可跳过）
在跑回归之前，必须向用户展示结构化摘要并等待确认：

```
我准备这样跑分析，请确认：
- **方法**：{方法名称}
- **因变量(Y)**：{变量名}（{中文含义}）
- **核心自变量(X)**：{变量名}（{中文含义}）
- **控制变量**：{列表}
- **标准误类型**：{类型}

以上设置确认吗？需要调整请告诉我。
```

用户回复"可以/确认"后才继续。不确认不跑回归。

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
2. 回归类方法（ols/panel/moderation/mediation/heterogeneity）跑之前必须经过变量确认
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
├── protocols/                    # 阻断型协议层
│   ├── protocol_order.md         # 执行顺序与阻断规则
│   ├── anti_hallucination.md     # 反幻觉协议（横切约束）
│   ├── data_audit.md             # 数据质检协议（前置阻断）
│   ├── method_selection.md       # 方法选择决策树（路由决策）
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
2. 运行 `engine/data_audit.py data.csv` → 质检通过
3. 读 `protocols/method_selection.md` → 截面数据+影响因素 → hypothesis → ols
4. 查 `method_capability.json` → ols: available, tier=pro
5. 变量确认（展示摘要，等用户确认）
6. 跑 baseline（descriptive + correlation）
7. 跑 `engine/ols.py` → 获得回归结果JSON
8. 读 `protocols/result_validation.md` → 标注可信度标签
9. 读 `protocols/reporting.md` + `templates/paper.md` → 生成三线表+解读

### 示例2：方法咨询

用户：我有企业面板数据，想看某项政策的效果，该用什么方法？

Agent流程：
1. 识别为"方法咨询"模式
2. 读 `protocols/method_selection.md` 决策树 → "有面板+政策时间点" → causal
3. 进一步确认：处理组选择是否随机？→ 分别建议DID或PSM-DID
4. 查 `method_capability.json` → 确认两个方法都available
5. 返回建议：推荐DID（若处理组外生）或PSM-DID（若处理组选择非随机）
6. 不执行任何计算，不输出数字
