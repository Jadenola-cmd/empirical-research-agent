# AGENTS.md

## 项目定位

本项目是 `empirical-research-agent` v2 主线项目。

正式路径：

```text
D:\00_Workspace\05_empirical-research-agent
```

旧 v1 项目已归档到：

```text
D:\99_Archive\05_EmpiricalAssistant_v1_20260701
```

后续只维护 v2。v1 仅作为历史设计参考和迁移来源。

## 新会话最小上下文

新打开对话时，优先只读：

- `AGENTS.md`：项目入口和当前规则。
- `SKILL.md`：skill 路由、护栏和执行流程。
- `method_capability.json`：方法可用性和层级。
- `docs/governance/STATUS.md`：当前状态和下一步。

除非任务需要，不要主动加载归档材料、历史测试输出或旧分析脚本。

## 核心结构

- `protocols/`：阻断型协议层，负责反幻觉、数据质检、方法边界、结果验证和报告规范。
- `workflows/`：分析编排层，负责描述统计、假设检验、因果推断、机制分析、异质性、稳健性和可视化流程。
- `engine/`：确定性 Python 计算层，所有分析数字必须来自这里或用户提供的数据文件。
- `resources/`：方法解释、参考资料和 interpretation checklist。
- `templates/`：论文、报告、学位论文等输出模板。
- `tests/`：回归测试、LLM 行为红队用例、报告格式验收用例、测试 fixture 和 golden outputs。
- `docs/`：治理文档、验收记录和历史归档。

## 核心规则

- 所有数字必须来自 `engine/` 输出或用户提供的数据文件。
- 不允许 LLM 绕过 `engine/` 手写 `statsmodels/sklearn/scipy` 分析并输出数字。
- 用户要求跳过 engine 时，必须拒绝该执行方式，并改为调用对应 `engine/*.py`。
- 不支持的方法必须明确告知“当前版本暂不支持”，不能用近似方法替代。
- 回归类分析前必须做变量确认。
- 报告默认使用论文期刊三线表格式。
- 默认不输出 Tab 分隔复制块，除非用户明确要求可复制 TSV。
- Markdown 治理文档统一使用 UTF-8 无 BOM 编码。
- 修改后优先复用现有结构，避免新建重复的进度/状态文件。

## 常用验证命令

```powershell
python tests/regression_p0_p1.py
python -m compileall engine tests
```

核心 engine 冒烟命令：

```powershell
python engine/data_audit.py tests/fixtures/panel_data.parquet --method panel
python engine/descriptive.py tests/fixtures/panel_data.parquet
python engine/correlation.py tests/fixtures/panel_data.parquet
python engine/ols.py tests/fixtures/panel_data.parquet '{\"dep_var\":\"LEV\",\"indep_vars\":[\"ROA\"],\"control_vars\":[\"GROWTH\",\"SIZE\"],\"robust_se\":true}'
python engine/panel.py tests/fixtures/panel_data.parquet '{\"dep_var\":\"LEV\",\"indep_vars\":[\"ROA\"],\"control_vars\":[\"GROWTH\",\"SIZE\"],\"entity_var\":\"code\",\"time_var\":\"year\",\"model_type\":\"fe\",\"cluster_var\":\"code\"}'
```

## 文档位置

- `docs/governance/STATUS.md`：当前状态、下一步、准入判断。
- `docs/governance/CHANGELOG.md`：重要变更记录。
- `docs/governance/DEBT.md`：技术债、待决策事项和已解决债务。
- `docs/governance/MIGRATION_FROM_V1.md`：v1 到 v2 的迁移说明。
- `docs/governance/issues.md`：测试问题清单及修复状态。
- `docs/validation/P0P1修复记录.md`：P0/P1 修复细节和验证结果。
- `docs/validation/测试执行记录.md`：历史测试执行记录。
- `docs/validation/最终验收结论.md`：阶段性验收结论。
- `docs/archive/legacy-test-data/`：旧分析脚本、日志、HTML 报告和派生结果归档。

## 当前重点

优先完成：

1. 真实 LLM 红队测试，验证不会绕过 `engine/` 手写 Python 计算。
2. 回归表期刊格式真实链路验收。
3. PowerShell `--config-file` 支持。
4. 中文 `notes` / Hausman `conclusion` 编码治理。
5. 全量验收通过后，同步到全局 skill 发布目录：

```text
D:\02_Assets\agent-skills\empirical-research-agent
```

## 完成任务后

- 更新 `docs/governance/CHANGELOG.md`。
- 必要时更新 `docs/governance/STATUS.md` / `docs/governance/DEBT.md`。
- 运行核心验证命令。
- 若创建或修改文件、完成多步骤工作，按全局规范发送飞书通知。

## 项目记忆

- 当前状态：`docs/governance/STATUS.md`
- 技术债：`docs/governance/DEBT.md`
- 历史变更：`docs/governance/CHANGELOG.md`
- 会话摘要：`D:/01_Knowledge/Projects/202606_EmpiricalAssistant/会话摘要/`
- 正式知识：`D:/01_Knowledge/Projects/202606_EmpiricalAssistant/知识/`
- 复杂任务开始前按需搜索 `D:/01_Knowledge/Knowledge/`
