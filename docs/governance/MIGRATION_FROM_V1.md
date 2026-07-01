# 从 v1 到 v2 的迁移说明

更新时间：2026-07-01

## 背景

v1 项目原路径：

```text
D:\00_Workspace\05_EmpiricalAssistant
```

v1 当前归档路径：

```text
D:\99_Archive\05_EmpiricalAssistant_v1_20260701
```

v2 正式项目路径：

```text
D:\00_Workspace\05_empirical-research-agent
```

v2 是 v1 的升级版，不是并行分支。后续只维护 v2，v1 作为历史档案和设计参考保留。

## v1 状态

v1 是早期 `SKILL.md + scripts/` 形态的论文实证分析助手。

已存在资产：

- `CLAUDE.md`
- `docs/PRD.md`
- `docs/STATUS.md`
- `docs/DEBT.md`
- `scripts/`
- `tests/`
- `test_data/`

v1 的价值：

- 保存早期产品定位和 MVP 范围。
- 保存从 `01_EmpiricalAgent` 迁移核心统计函数的设计依据。
- 保存早期技术债和取舍记录。

v1 后续处理：

- 不再新增功能。
- 不直接作为全局 skill 发布源。
- 如需引用历史决策，从 `docs/PRD.md`、`docs/STATUS.md`、`docs/DEBT.md` 查阅。

## v2 变化

v2 从单层 skill 工具包升级为三层结构：

```text
protocols/   阻断型协议层
workflows/   分析编排层
engine/      确定性计算层
```

关键增强：

- 反幻觉协议前置，全程禁止无来源数字。
- 数据质检、方法选择、结果验证、报告规范形成阻断链路。
- 支持更明确的方法能力注册表 `method_capability.json`。
- 所有数字必须来自 `engine/` 输出或用户数据。
- 增加 P0/P1 回归测试和 golden outputs。
- 增加 LLM 红队测试和回归表格式验收用例。

## 已迁移或继承的内容

- 继承 v1 的本地 skill 包定位。
- 继承 v1 对论文实证分析用户的目标场景。
- 继承核心统计 engine 的迁移方向。
- 继承 `docs/STATUS.md` / `docs/DEBT.md` 的项目治理习惯，并在 v2 中升级为根目录治理文件。

## v2 新增治理文件

v2 根目录现在包含：

- `AGENTS.md`：项目级启动索引。
- `docs/governance/STATUS.md`：当前状态、下一步、准入判断。
- `docs/governance/CHANGELOG.md`：重要变更记录。
- `docs/governance/DEBT.md`：技术债和待决策事项。
- `docs/governance/MIGRATION_FROM_V1.md`：本迁移说明。

## 推荐后续动作

1. 完成真实 LLM 红队测试。
2. 完成回归表期刊格式真实链路验收。
3. 全量验收通过后，同步到全局 skill 发布目录：

```text
D:\02_Assets\agent-skills\empirical-research-agent
```

4. 只在 v2 主线维护代码和协议，避免 v1/v2 双线分叉。