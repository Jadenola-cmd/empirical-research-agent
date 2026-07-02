# Empirical Research Agent

面向论文写作者的实证分析 Agent / Codex Skill，用于在有数据文件和研究问题时，辅助完成数据质检、方法选择、计量分析、结果验证和论文式解读。

本项目的核心目标不是让大模型“凭感觉算数”，而是让大模型负责流程编排和文字解释，所有统计数字都来自确定性 Python engine。

## 核心原则

- 所有数字必须来自 `engine/` 脚本输出或用户提供的数据文件。
- 不允许 Agent 绕过 `engine/` 手写 `statsmodels`、`sklearn`、`scipy` 分析并输出数字。
- 不支持的方法必须明确说明“当前版本暂不支持”，不能用近似方法替代。
- 回归类分析前必须确认变量、样本结构和方法适用性。
- 报告默认采用论文/期刊风格表述，结果解读标注可信度标签。

## 支持能力

当前 engine 覆盖以下分析场景：

| 类别 | 方法 |
|---|---|
| 数据探索 | 数据审计、描述性统计、相关系数矩阵 |
| 回归分析 | OLS、多控制变量回归、稳健标准误、面板固定效应/随机效应、Hausman 检验 |
| 因果推断 | DID、PSM、PSM-DID |
| 机制与扩展 | 调节效应、中介效应、异质性分析、稳健性检验 |
| 报告输出 | 基于 engine JSON 的论文式 Markdown 回归表和结果解读 |

具体方法可用性以 [`method_capability.json`](method_capability.json) 为准。

## 快速开始

1. 准备数据文件，推荐使用 `.csv`、`.xlsx`、`.xls`、`.parquet` 或 `.dta`。
2. 向 Agent 说明研究问题、被解释变量、核心解释变量、控制变量和期望方法。
3. Agent 会先执行数据质检和方法适用性判断，再调用对应 `engine/*.py` 计算。
4. 输出报告时，结论中的数值必须可追溯到 engine JSON 或用户原始数据。

常用命令示例：

```powershell
python engine/data_audit.py tests/fixtures/panel_data.parquet --method panel
python engine/descriptive.py tests/fixtures/panel_data.parquet
python engine/correlation.py tests/fixtures/panel_data.parquet
python engine/ols.py tests/fixtures/panel_data.parquet '{"dep_var":"LEV","indep_vars":["ROA"],"control_vars":["GROWTH","SIZE"],"robust_se":true}'
python engine/panel.py tests/fixtures/panel_data.parquet '{"dep_var":"LEV","indep_vars":["ROA"],"control_vars":["GROWTH","SIZE"],"entity_var":"code","time_var":"year","model_type":"fe","cluster_var":"code"}'
```

PowerShell 下也可以使用配置文件，避免复杂 JSON 转义：

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
tests/                  回归测试、红队用例、fixture 和 golden outputs
docs/                   治理文档、验收记录和历史归档
```

## 验证

核心回归验证命令：

```powershell
python tests/regression_p0_p1.py
python -m compileall engine tests
```

项目要求 Markdown 治理文档使用 UTF-8 无 BOM 编码；不要把 `AI_Output/`、临时分析产物或敏感数据提交进 Git。
