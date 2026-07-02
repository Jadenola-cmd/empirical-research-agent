# 技术债与待决策事项

更新时间：2026-07-01

## P1 待人工验收

当前无待处理 P1 人工验收项。

## P2 易用性与质量优化

当前无待处理 P2 易用性与质量优化项。

## 已解决债务

### R-001 Baseline engine 无法运行

状态：已解决

说明：`descriptive.py` 和 `correlation.py` 已修复函数签名不一致问题。

### R-002 数据读取格式不一致

状态：已解决

说明：新增 `load_dataframe()`，统一支持 `.csv/.xlsx/.xls/.parquet/.dta`。

### R-003 非法 JSON 暴露 traceback

状态：已解决

说明：所有 config 型 engine 已改用 `parse_json_config()`。

### R-004 PSM/DID 顶层 error 退出码为 0

状态：已解决

说明：顶层 `{error}` 现在返回退出码 1。

### R-005 v2 正式工作区迁移

状态：已解决

说明：正式项目路径确定为 `D:\00_Workspace\05_empirical-research-agent`，旧 v1 项目归档到 `D:\99_Archive\05_EmpiricalAssistant_v1_20260701`。

### R-006 治理文档中文乱码

状态：已解决

说明：`AGENTS.md`、`docs/governance/STATUS.md`、`docs/governance/CHANGELOG.md`、`docs/governance/DEBT.md`、`docs/governance/MIGRATION_FROM_V1.md` 已统一重写为 UTF-8 无 BOM。

### R-007 PowerShell JSON 参数体验

状态：已解决

说明：所有 config 型 engine 入口已支持 `--config-file <json_path>`，配置文件按 `utf-8-sig` 读取，兼容 PowerShell `Set-Content -Encoding UTF8` 生成的 BOM 文件。已补充 OLS 配置文件回归测试，并用 panel 配置文件完成冒烟验证。

### R-008 LLM 绕过 engine 的真实会话红队测试

状态：已解决

说明：`tests/llm_behavior_redteam.md` 已补充本轮执行记录。三类诱导用例均要求拒绝绕过 `engine/`、拒绝近似替代 planned 方法、拒绝未运行 engine 前输出预期数字。

### R-009 回归表期刊格式真实链路验收

状态：已解决

说明：`engine/export.py` 已支持基于 OLS + Panel engine JSON 生成 paper Markdown 回归表，覆盖 `(1) 混合 OLS`、`(2) 固定效应 FE`、系数星号、t值、N、R²/Within R²、F、Hausman、标准误说明和 `[VERIFIED]` 解读。`tests/regression_p0_p1.py` 已加入可执行回归测试。

### R-010 中文 notes / Hausman conclusion 编码治理

状态：已解决

说明：`tests/golden_outputs/ols_corrected.json` 和 `tests/golden_outputs/panel_corrected.json` 已转为 UTF-8 无 BOM，并修复 `notes`、Hausman `conclusion` 中的乱码。已加入 golden 输出乱码扫描测试。
