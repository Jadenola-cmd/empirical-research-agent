# Empirical Research Agent v2 - 项目状态

更新时间：2026-07-02

## 当前定位

本项目是 `D:\00_Workspace\05_EmpiricalAssistant` 的升级版，定位为可复用的论文实证分析 skill 包。

当前版本采用三层结构：

- `protocols/`：阻断型协议层，负责反幻觉、数据质检、方法边界、结果可信度和报告格式。
- `workflows/`：分析编排层，负责描述统计、假设检验、因果推断、机制分析、异质性、稳健性和可视化流程。
- `engine/`：确定性 Python 计算层，所有数字必须来自 engine 输出或用户数据。

旧项目 `D:\00_Workspace\05_EmpiricalAssistant` 已归档到 `D:\99_Archive\05_EmpiricalAssistant_v1_20260701`，保留为 v1 历史参考，不再作为新功能主线开发。

## 当前状态

P0/P1 已完成修复并通过本地回归测试。

已完成一次真实论文实证分析链路输出：基于 `tests/测试数据/` 下的 CSMAR 风格 Excel 文件，构建“避税与企业创新”公司-年度面板数据，并在 `AI_Output/Codex/` 输出数据集、engine 原始 JSON 和论文格式 Markdown 报告。

已验证：

- 描述统计和相关矩阵 baseline 已恢复可运行。
- `data_audit.py` 支持 `.csv/.xlsx/.xls/.parquet/.dta` 读取。
- 面板数据可识别 `code/year` 结构。
- 非法 JSON config 返回结构化 `{error: ...}`，不再暴露 traceback。
- PSM/DID 顶层 error 退出码已改为 1。
- 报告协议默认不输出 Tab 分隔复制块。
- `requirements.txt` 已加入 `linearmodels>=5.0`。
- 已补充 LLM 绕过 engine 的红队测试说明。
- 已补充回归表期刊格式验收用例。
- 所有 config 型 engine 已支持 `--config-file <json_path>`，并兼容 UTF-8 BOM 配置文件。
- 真实报告生成链路已可基于 OLS + Panel engine JSON 输出期刊格式 Table 2 Markdown。
- 中文 `notes` / Hausman `conclusion` golden 输出已完成 UTF-8 无 BOM 编码治理。
- LLM 行为红队测试已完成本轮验收记录。
- 已同步到全局 skill 发布目录 `D:\02_Assets\agent-skills\empirical-research-agent`。
- 已生成 `AI_Output/Codex/避税与企业创新实证分析报告.md`，报告使用 `engine/descriptive.py`、`engine/correlation.py`、`engine/panel.py`、`engine/diagnostics.py` 的原始输出作为数字来源。
- 已新增 GitHub 首页说明文档 `README.md`。

## 核心验证命令

```powershell
python tests/regression_p0_p1.py
python -m compileall engine tests
```

最近一次验证结果：通过。

## 下一步优先级

1. 如继续完善该实证主题，优先补充所得税费用、利润总额等字段，以构造 ETR/BTD 类严格避税指标。
2. 如需提升报告稳健性，可加入缩尾处理、替代创新指标和年度固定效应模型。
3. 核对 Git diff，确认没有无关改动。
4. 如需发布版本快照，可创建 Git commit 或 tag。

## 当前准入判断

当前版本已完成进入全局 skill 库前的核心 P1/P2 清理，并已同步到全局 skill 发布目录。

后续如需发布版本快照，至少需要完成：

- 核对 Git diff。
- 创建 Git commit 或 tag。

## 正式工作区

正式项目路径：

```text
D:\00_Workspace\05_empirical-research-agent
```

旧 v1 项目归档路径：

```text
D:\99_Archive\05_EmpiricalAssistant_v1_20260701
```
