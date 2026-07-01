# Workflow: Descriptive Analysis — 描述性分析

## 触发条件

- 用户说"看看数据"、"描述性统计"、"数据长什么样"
- method_selection 决策树路由到 descriptive

## 前置检查

- [ ] data_audit 已通过（PASS 或 WARN+用户确认）
- [ ] 数据已加载为 parquet 格式

## 执行步骤

### Step 1: 数据诊断
```bash
python engine/data_audit.py <parquet_path>
```
读取输出，确认数据基本信息（行数、列数、列类型、缺失情况）。

### Step 2: 描述性统计
```bash
python engine/descriptive.py <parquet_path> [--columns col1,col2,...]
```
若用户指定了列，传 --columns；否则对所有数值列运行。

### Step 3: 相关性分析
```bash
python engine/correlation.py <parquet_path> [--columns col1,col2,...]
```
仅当用户要求或变量数≥2时执行。

### Step 4: 输出报告

按 reporting.md 的"描述统计表"和"相关系数矩阵"模板生成表格。

按 result_validation.md 对每条结论标注可信度标签。

若单独请求 descriptive（不依附回归请求），不使用完整"一~五"报告骨架，给一张表+一段解读即可。

## 输出模板

使用 `templates/report.md`（内部汇报格式，可视化优先）。

## 完成检查

- [ ] 描述统计表（三线表格式）
- [ ] 相关系数矩阵（下三角，含星号）
- [ ] Tab分隔复制块
- [ ] 解读文字 + 可信度标签
- [ ] 所有数字可溯源到 engine 输出
