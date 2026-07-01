# Changelog

本文件记录 Empirical Research Agent v2 的重要变更。

## 2026-07-01

### Added

- 新增 `engine/lib/cli_utils.py`，统一处理多格式数据读取、JSON config 解析、顶层 `{error}` 对应非零退出码。
- 新增 `tests/regression_p0_p1.py`，覆盖 P0/P1 回归测试。
- 新增 `tests/llm_behavior_redteam.md`，记录 LLM 绕过 engine 的红队测试用例。
- 新增 `tests/regression_table_format_p1.md`，记录论文期刊回归表格式验收标准。
- 新增 `P0P1修复记录.md`，记录本轮 P0/P1 修复内容和验证结果。
- 新增治理文档：`STATUS.md`、`CHANGELOG.md`、`DEBT.md`、`MIGRATION_FROM_V1.md`。
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
- 修复 `STATUS.md`、`CHANGELOG.md`、`DEBT.md`、`MIGRATION_FROM_V1.md` 等治理文档中文乱码问题。

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