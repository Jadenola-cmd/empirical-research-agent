# Empirical Research Agent

面向论文写作者的实证分析 Agent Skill。它负责数据质检、方法选择、计量分析编排、结果验证和论文式解释；
LLM负责方法选择和解释，计算由脚本统计，所有统计数字必须来自确定性的 `engine/` 输出或用户提供的数据文件，不能由 Agent 心算、推断或手写临时统计脚本生成。

## 核心原则

- 所有数字必须来自 `engine/` 脚本输出或用户提供的数据文件。
- 不允许 Agent 绕过 `engine/` 手写 `statsmodels`、`sklearn`、`scipy` 分析并输出数字。
- 不支持的方法必须明确说明“当前版本暂不支持”，不能用近似方法替代。
- 回归类分析前必须确认变量映射、样本结构和方法适用性。
- 报告默认使用论文/期刊三线表格式，并为结论标注可信度标签。

## 支持能力

| 类别 | 方法 |
|---|---|
| 数据探索 | 数据审计、描述性统计、相关系数矩阵 |
| 回归分析 | OLS、多控制变量回归、稳健标准误、面板固定效应/随机效应、Hausman 检验 |
| 因果推断 | DID、PSM、PSM-DID |
| 机制与扩展 | 调节效应、中介效应、异质性分析、稳健性检验 |
| 报告输出 | 基于 engine JSON 的论文式 Markdown 回归表和结果解读 |

具体方法可用性以 [`method_capability.json`](method_capability.json) 为准。

## 安装教程

推荐设定一个文件夹作为单一源目录，然后在 Claude Code、Codex 和 WorkBuddy 的 skills 目录中建立 Junction/符号链接。这样后续只需要维护一份源文件，三个客户端会同时生效。

### 1. 安装到 Claude Code、Codex、WorkBuddy

- 如果你的环境不能创建 Junction，可以把源目录复制到对应 skills 目录；但复制安装会产生多份副本，后续需要分别同步。
Claude Code：C:\Users\.claude\skills
Codex：C:\Users\.codex\skills
WorkBuddy：C:\Users\.workbuddy\skills


### 2. 客户端使用方式

| 客户端 | 安装路径 | 触发方式 |
|---|---|---|
| Claude Code | `%USERPROFILE%/.claude/skills/empirical-research-agent` | 新会话后直接说明“使用 empirical-research-agent 做实证分析”，或在项目目录中打开并依赖 `CLAUDE.md`/`AGENTS.md` 规则 |
| Codex | `%USERPROFILE%/.codex/skills/empirical-research-agent` | 提供数据文件和计量需求；当请求涉及 OLS、面板、DID、PSM、调节/中介等方法时应自动触发 |
| WorkBuddy | `%USERPROFILE%/.workbuddy/skills/empirical-research-agent` | 新会话后说明使用该 skill，并让它读取项目根目录 `AGENTS.md`、`SKILL.md` 和必要协议文件 |

建议每次安装或更新后重启对应客户端的新会话，确保 skill 元数据重新加载。

## 使用教程

### 1. 最小输入

给 Agent 的请求至少包含：

- 数据文件路径：支持 `.csv`、`.xlsx`、`.xls`、`.parquet`、`.dta`
- 研究问题：例如“税收优惠是否促进企业创新”
- 被解释变量 Y、核心解释变量 X、控制变量
- 期望方法：如 OLS、面板 FE、DID、PSM、调节效应、中介效应
- 样本口径：年份、行业、公司范围、是否需要固定效应或聚类标准误

### 2. 推荐提示词模板

```text
使用 empirical-research-agent。

数据文件：D:/path/to/data.parquet
研究问题：税收优惠是否促进企业创新。
被解释变量 Y：patent_count，表示企业创新产出。
核心解释变量 X：tax_saving_rate，数值越大表示税收优惠越强。
控制变量：size、roa、growth、cashflow。
方法：面板固定效应回归，企业和年份固定效应，按企业聚类稳健标准误。

请先做数据质检和变量映射确认；我确认后再执行回归，并输出论文三线表和结果解读。
```

### 3. 标准执行流程

1. 读取 `SKILL.md`，按操作意图判断是否进入标准流水线。
2. 执行 `engine/data_audit.py` 做数据质检。
3. 按 `protocols/method_selection.md` 和 `method_capability.json` 确认方法可用性。
4. 回归前输出变量映射和样本构建方案，等待用户确认。
5. 调用对应 `engine/*.py` 计算，不手写临时统计分析。
6. 按 `protocols/result_validation.md` 标注结论可信度。
7. 按 `protocols/reporting.md` 和 `templates/` 输出论文式报告。

### 4. 常用 engine 命令

```powershell
python engine/data_audit.py tests/fixtures/panel_data.parquet --method panel
python engine/descriptive.py tests/fixtures/panel_data.parquet
python engine/correlation.py tests/fixtures/panel_data.parquet
python engine/ols.py tests/fixtures/panel_data.parquet '{"dep_var":"LEV","indep_vars":["ROA"],"control_vars":["GROWTH","SIZE"],"robust_se":true}'
python engine/panel.py tests/fixtures/panel_data.parquet '{"dep_var":"LEV","indep_vars":["ROA"],"control_vars":["GROWTH","SIZE"],"entity_var":"code","time_var":"year","model_type":"fe","cluster_var":"code"}'
```

PowerShell 下建议使用配置文件，避免复杂 JSON 转义：

```powershell
python engine/ols.py tests/fixtures/panel_data.parquet --config-file ols_config.json
```

## 项目结构

```text
protocols/              阻断型协议层：反幻觉、数据质检、方法边界、结果验证、报告规范
workflows/              分析编排层：描述统计、假设检验、因果推断、机制、异质性、稳健性
engine/                 确定性 Python 计算层
resources/              方法解释和结果解读 checklist
templates/              论文、报告、学位论文输出模板
docs/                   治理文档、验收记录和历史归档
```

## 验证

核心回归验证命令：

```powershell
python tests/regression_p0_p1.py
python -m compileall engine tests
```

Markdown 治理文档统一使用 UTF-8 无 BOM 编码；不要把 `AI_Output/`、临时分析产物、敏感数据、`.env` 或 token 提交到 Git。
