# Workflow: Hypothesis Testing — 假设检验（OLS / 面板回归）

## 触发条件

- 用户问"X对Y有影响吗？"、"X和Y什么关系？"
- method_selection 决策树路由到 hypothesis → ols 或 panel

## 前置检查

- [ ] data_audit 已通过
- [ ] 方法在 method_capability.json 中 status=available
- [ ] 用户 tier >= 方法 tier（ols/panel 需要 pro）

## 执行步骤

### Step 1: 变量确认（关键步骤，不可跳过）

在跑回归之前，必须向用户展示结构化摘要并等待确认：

> 我准备这样跑分析，请确认：
> - **方法**：{OLS / 面板FE + Hausman}
> - **因变量(Y)**：{变量名}（{中文含义}）
> - **核心自变量(X)**：{变量名}（{中文含义}）
> - **控制变量**：{列表}
> - **个体/时间变量**（面板）：{entity_col} / {time_col}
> - **标准误类型**：{HC1 / clustered / ...}
>
> 以上设置确认吗？需要调整请告诉我。

用户回复"可以/确认"后才继续。用户要求调整则更新摘要重新确认。

### Step 2: 描述性统计（基线表格）

```bash
 python engine/descriptive.py <parquet_path> <config>
```
生成描述统计表（三线表格式）。

### Step 3: 相关性分析（基线表格）

```bash
 python engine/correlation.py <parquet_path> <config>
```
生成相关系数矩阵（下三角，含星号）。

### Step 4: 执行回归

**OLS：**
```bash
 python engine/ols.py <parquet_path> <config>
```

**面板：**
```bash
 python engine/panel.py <parquet_path> <config>
```

### Step 5: 回归诊断

```bash
python engine/diagnostics.py <model_output>
```
检查：VIF（多重共线性）、异方差检验、模型设定检验。

### Step 6: 输出报告

按 reporting.md 生成完整报告（一~五章节结构）：
- 一、数据概况 + 变量定义表
- 二、描述性统计
- 三、相关性分析
- 四、回归结果（三线表 + Hausman/诊断）
- 五、结果解读 + 可信度标签

### Step 7（面板专属）: Hausman检验解读

- 若 Hausman p < 0.05 → 使用FE，报告FE结果
- 若 Hausman p >= 0.05 → 使用RE，报告RE结果
- 若 Hausman 结果为负 → 保守选择FE，标注 [INFERRED]

## 输出模板

使用 `templates/paper.md`（期刊投稿格式）。

## 完成检查

- [ ] 变量确认步骤已执行且获用户确认
- [ ] 描述统计 + 相关矩阵已作为基线表格输出
- [ ] 回归系数表（三线表格式，系数+星号+括号t值）
- [ ] 面板：Hausman检验结果（不通过时有说明）
- [ ] 诊断结果（VIF/异方差）
- [ ] 解读文字 + 可信度标签
- [ ] 所有数字可溯源到 engine 输出
