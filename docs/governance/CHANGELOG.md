# Changelog

## 2026-07-02 README added

### Added

- 新增根目录 `README.md`，作为 GitHub 首页入口，概述项目定位、核心原则、支持能力、快速开始、项目结构和验证命令。

### Verification

- `D:/anaconda/python.exe -m compileall engine tests`

## 2026-07-02 Tax innovation empirical analysis output

### Added

- 在 `AI_Output/Codex/` 生成“避税与企业创新”实证分析数据集、engine 原始 JSON 输出和论文格式 Markdown 报告。
- 新增一次性数据准备脚本 `AI_Output/Codex/prepare_tax_innovation_dataset.py`，用于从 `tests/测试数据/` 合并税项名义税率、专利申请、研发投入、分析师关注度和现金流数据。
- 新增报告生成脚本 `AI_Output/Codex/generate_tax_innovation_report.py`，仅编排 `engine/descriptive.py`、`engine/correlation.py`、`engine/panel.py` 和 `engine/diagnostics.py` 输出，不手写统计计算。

### Notes

- 当前数据无法构造 ETR/BTD 类严格避税指标，报告将 `tax_saving_rate = 0.25 - tax_rate` 解释为低名义所得税率/税收优惠强度代理。
- 数据质检为 WARN，主要风险为部分变量异常值和高缺失治理变量；正式报告已在结论可信度中降级标注。

### Verification

- `D:/anaconda/python.exe AI_Output/Codex/prepare_tax_innovation_dataset.py`
- `D:/anaconda/python.exe engine/data_audit.py AI_Output/Codex/tax_innovation_panel.parquet --method panel`
- `D:/anaconda/python.exe AI_Output/Codex/generate_tax_innovation_report.py`

## 2026-07-01 Root context cleanup

### Changed

- Moved governance documents from the repository root to `docs/governance/`.
- Moved validation records from the repository root to `docs/validation/`.
- Moved active test fixtures from `test-data/` to `tests/fixtures/`.
- Moved regression evidence from `golden_outputs/` to `tests/golden_outputs/`.
- Moved legacy analysis scripts, logs, HTML reports, and derived result files to `docs/archive/legacy-test-data/`.
- Rewrote `AGENTS.md` as a concise new-session index to reduce default context loading.

### Verification

- `python tests/regression_p0_p1.py`
- `python -m compileall engine tests`

本文件记录 Empirical Research Agent v2 的重要变更。

## 2026-07-01 Config file CLI support

### Added

- 新增 `parse_config_arg()`，所有 config 型 engine 支持直接传入 JSON 字符串或 `--config-file <json_path>`。
- 新增 OLS `--config-file` 回归测试，覆盖 PowerShell 复杂 JSON 参数体验。

### Changed

- 配置文件按 `utf-8-sig` 读取，兼容 PowerShell `Set-Content -Encoding UTF8` 生成的 BOM 文件。

### Verification

- `python tests/regression_p0_p1.py`
- `python -m compileall engine tests`
- `python engine/panel.py tests/fixtures/panel_data.parquet --config-file <temp_panel_config.json>`

## 2026-07-01 Final P1/P2 validation cleanup

### Added

- `engine/export.py` 新增 paper Markdown 回归表生成能力，可合并 OLS 与 Panel JSON 输出。
- `tests/regression_p0_p1.py` 新增期刊回归表链路测试和 golden 输出乱码扫描测试。
- `tests/llm_behavior_redteam.md` 新增本轮真实会话红队验收记录。

### Changed

- `tests/golden_outputs/ols_corrected.json` 与 `tests/golden_outputs/panel_corrected.json` 转为 UTF-8 无 BOM，并修复中文 `notes`、Hausman `conclusion` 乱码。
- `engine/export.py` 输出 Markdown 时使用 UTF-8 stdout，避免 Windows 控制台编码阻断 `R²` 等报告文本。

### Verification

- `python tests/regression_p0_p1.py`
- `python -m compileall engine tests`
- `python engine/export.py tests/golden_outputs/ols_corrected.json --config-file <temp_export_config.json>`
- `robocopy D:\00_Workspace\05_empirical-research-agent D:\02_Assets\agent-skills\empirical-research-agent /E ...`

## 2026-07-01

### Added

- 新增 `engine/lib/cli_utils.py`，统一处理多格式数据读取、JSON config 解析、顶层 `{error}` 对应非零退出码。
- 新增 `tests/regression_p0_p1.py`，覆盖 P0/P1 回归测试。
- 新增 `tests/llm_behavior_redteam.md`，记录 LLM 绕过 engine 的红队测试用例。
- 新增 `tests/regression_table_format_p1.md`，记录论文期刊回归表格式验收标准。
- 新增 `docs/validation/P0P1修复记录.md`，记录本轮 P0/P1 修复内容和验证结果。
- 新增治理文档：`docs/governance/STATUS.md`、`docs/governance/CHANGELOG.md`、`docs/governance/DEBT.md`、`docs/governance/MIGRATION_FROM_V1.md`。
- 新增 `AGENTS.md`，作为项目级启动索引，帮助新会话快速了解项目定位、架构、规则、验证命令和治理文档。
- 新增正式工作区迁移说明，确定 v2 正式路径为 `D:\00_Workspace\05_empirical-research-agent`。

### Changed

- `engine/descriptive.py` 改为默认自动选择数值列，并传入 `stats_core.run_descriptive(df, numeric_cols)`。
- `engine/correlation.py` 改为默认自动选择数值列，并传入 `stats_core.run_correlation(df, numeric_cols)`。
- `engine/data_audit.py` 改为使用统一 loader，支持 `.csv/.xlsx/.xls/.parquet/.dta`。
- `engine/data_audit.py` 的面板识别候选扩展为 `entity/id/firm_id/code/company_id/stock_code` 和 `time/year/date/period`。
- 所有 `engine/*.py` 的 config 入口改为结构化 JSON 错误处理。
- `engine/psm.py` 和 `engine/did.py` 在返回顶层 `{error}` 时退出码改为 1。
- `protocols/reporting.md` 和 `templates/paper.md` 改为默认不输出 Tab 分隔复制块。
- `protocols/anti_hallucination.md` 增加“绕过引擎型”禁止行为。
- `requirements.txt` 增加 `linearmodels>=5.0`。
- 旧项目 `D:\00_Workspace\05_EmpiricalAssistant` 已归档到 `D:\99_Archive\05_EmpiricalAssistant_v1_20260701`。
- 治理类 Markdown 文档统一重写为 UTF-8 无 BOM，修复中文乱码问题。

### Fixed

- 修复描述统计和相关矩阵 baseline CLI 无法运行的问题。
- 修复 CSV 传给 `data_audit.py` 会被当成 parquet 读取的问题。
- 修复 `code/year` 面板数据被误判为缺少 entity 的问题。
- 修复非法 JSON config 暴露 Python traceback 的问题。
- 修复 PSM/DID 业务错误退出码为 0 的问题。
- 修复报告协议默认要求 Tab 分隔复制块与当前输出标准冲突的问题。
- 修复 `docs/governance/STATUS.md`、`docs/governance/CHANGELOG.md`、`docs/governance/DEBT.md`、`docs/governance/MIGRATION_FROM_V1.md` 等治理文档中文乱码问题。

### Verification

已通过：

```powershell
python tests/regression_p0_p1.py
python -m compileall engine tests
```

## 2026-06-29 至 2026-06-30

### Added

- 完成 v2 skill 包初始封装：`SKILL.md`、`method_capability.json`、`protocols/`、`workflows/`、`engine/`、`resources/`、`templates/`、`test-data/`。

### Notes

- v2 相比 v1 从 `SKILL.md + scripts/` 单层工具包，升级为 `protocols + workflows + engine` 三层结构。
- v1 项目 `D:\00_Workspace\05_EmpiricalAssistant` 保留为历史参考，并已归档到 `D:\99_Archive\05_EmpiricalAssistant_v1_20260701`。
