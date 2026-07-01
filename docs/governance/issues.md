# Empirical Research Agent Skill 测试问题清单

## 当前状态

P0/P1 已完成修复并通过回归测试。P2 仍保留为后续优化项。

验证命令：

```powershell
python tests/regression_p0_p1.py
```

## P0 阻断问题

### P0-1 标准流水线的 baseline 步骤无法跑通（已修复）

- 现象：`engine/descriptive.py` 和 `engine/correlation.py` 退出码均为 1。
- 证据：
  - `tests/golden_outputs/descriptive_all.json`：`run_descriptive() got an unexpected keyword argument 'columns'`
  - `tests/golden_outputs/correlation_all.json`：`run_correlation() got an unexpected keyword argument 'columns'`
- 影响：`SKILL.md` Step 5 要求回归前默认执行描述统计和相关矩阵，因此标准流水线无法完整通过。
- 修复：`descriptive.py` / `correlation.py` 已自动选择数值列并传入 `stats_core` 的 `numeric_cols` 参数。
- 证据：`tests/golden_outputs/core_summary_after_fix.json`

## P1 高优先级问题

### P1-1 数据格式承诺与实现不一致（已修复）

- 现象：`SKILL.md` 声明支持 `.csv/.xlsx/.parquet/.dta`，但 `data_audit.py` 只调用 `pd.read_parquet`。
- 证据：`tests/golden_outputs/negative_csv_to_data_audit.json`
- 影响：用户按文档传 CSV 会失败。
- 修复：新增 `engine/lib/cli_utils.py::load_dataframe()`，支持 `.csv/.xlsx/.xls/.parquet/.dta`。

### P1-2 Panel 数据识别规则过窄（已修复）

- 现象：`data_audit.py --method panel` 对包含 `code/year` 的面板数据返回 `method_match.ready=false`，提示缺少个体标识列。
- 证据：`tests/golden_outputs/data_audit_panel.json`
- 影响：真实面板数据会被错误降级为 WARN 或阻断。
- 修复：entity/time 候选已扩展，`method_match.detected` 会返回识别到的列。

### P1-3 非法 JSON config 暴露 traceback（已修复）

- 现象：`python engine/ols.py ... '{bad json}'` 输出 Python traceback，未返回结构化 `{error: ...}`。
- 证据：`tests/golden_outputs/negative_ols_invalid_json.err.txt`
- 影响：违反“失败应返回可理解错误，不应输出 Python traceback 给最终用户”的验收标准。
- 修复：所有 `engine/*.py` 的 config 入口已改用 `parse_json_config()`；非法 JSON 返回结构化错误且无 traceback。

### P1-4 报告协议仍要求 Tab 分隔复制块（已修复）

- 现象：`protocols/reporting.md` 和 `templates/paper.md` 仍写明每张表后附 Tab 分隔复制块。
- 证据：静态检查命中 `protocols/reporting.md`、`templates/paper.md`
- 影响：与当前验收标准和既有输出偏好冲突，会诱导 Agent 输出冗余复制块。
- 修复：`protocols/reporting.md` 和 `templates/paper.md` 已改为默认不输出 Tab 分隔复制块。

### P1-5 requirements 未声明 panel 必需依赖（已修复）

- 现象：`engine/lib/stats_core.py` 的 `run_panel` 依赖 `linearmodels`，但 `requirements.txt` 未列为必需依赖。
- 证据：当前环境 `linearmodels==7.0` 可导入；`requirements.txt` 只把 linearmodels 注释为 future/optional。
- 影响：新环境按 requirements 安装后，Panel 功能可能直接失败。
- 修复：`requirements.txt` 已加入 `linearmodels>=5.0`。

## P2 中优先级问题

### P2-1 PSM/DID 业务错误退出码为 0（已修复，原 P2 上提处理）

- 现象：PSM 非二值处理变量、PSM 样本不足、DID 缺少 time 参数都返回 JSON error，但进程退出码为 0。
- 证据：`tests/golden_outputs/negative_summary.json`
- 影响：自动化测试或上层 Agent 仅看退出码时会误判为成功。
- 修复：PSM/DID 顶层 `error` 时退出码改为 1。

### P2-2 PowerShell JSON 参数易用性不足

- 现象：普通 PowerShell 传 JSON 参数时，双引号可能被原生命令参数解析移除；需要额外转义为 `{\"...\"}`。
- 影响：用户照抄文档命令容易得到 `JSONDecodeError`。
- 建议：文档增加 Windows PowerShell 示例，或支持 `--config-file config.json`。

### P2-3 引擎输出中文说明存在编码乱码

- 现象：OLS/Panel 输出的 `notes`、Hausman `conclusion` 出现乱码。
- 证据：`tests/golden_outputs/ols_corrected.json`、`tests/golden_outputs/panel_corrected.json`
- 影响：报告生成时若直接引用 notes，会影响论文文本质量。
- 建议：统一源码文件编码为 UTF-8，并检查历史迁移文件的中文字符串。

## 准入判断

当前不建议进入全局 skill 库作为稳定版本。至少需要先修复 P0-1，并处理 P1-1/P1-3/P1-4/P1-5 后，再做一轮完整回归测试。
