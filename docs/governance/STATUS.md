# Empirical Research Agent v2 - 项目状态

更新时间：2026-07-01

## 当前定位

本项目是 `D:\00_Workspace\05_EmpiricalAssistant` 的升级版，定位为可复用的论文实证分析 skill 包。

当前版本采用三层结构：

- `protocols/`：阻断型协议层，负责反幻觉、数据质检、方法边界、结果可信度和报告格式。
- `workflows/`：分析编排层，负责描述统计、假设检验、因果推断、机制分析、异质性、稳健性和可视化流程。
- `engine/`：确定性 Python 计算层，所有数字必须来自 engine 输出或用户数据。

旧项目 `D:\00_Workspace\05_EmpiricalAssistant` 已归档到 `D:\99_Archive\05_EmpiricalAssistant_v1_20260701`，保留为 v1 历史参考，不再作为新功能主线开发。

## 当前状态

P0/P1 已完成修复并通过本地回归测试。

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

## 核心验证命令

```powershell
python tests/regression_p0_p1.py
python -m compileall engine tests
```

最近一次验证结果：通过。

## 下一步优先级

1. 执行真实 Agent 会话红队测试，验证不会绕过 `engine/` 手写 Python 计算。
2. 执行真实报告生成链路，验证回归表稳定符合论文期刊格式。
3. 处理 P2 易用性问题：PowerShell `--config-file` 支持、中文 notes 编码治理。
4. 全量验收通过后，同步到全局 skill 发布目录 `D:\02_Assets\agent-skills\empirical-research-agent`。

## 当前准入判断

当前版本已具备进入下一轮全量验收的条件，但不建议直接视为最终稳定版。

进入全局 skill 库前，至少需要完成：

- 真实 LLM 红队测试通过。
- 真实报告格式验收通过。
- P2 中影响用户体验的命令行配置问题有明确处理方案。

## 正式工作区

正式项目路径：

```text
D:\00_Workspace\05_empirical-research-agent
```

旧 v1 项目归档路径：

```text
D:\99_Archive\05_EmpiricalAssistant_v1_20260701
```