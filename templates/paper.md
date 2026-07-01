# Paper Template — 期刊投稿格式

## 适用场景

学术期刊投稿（经济研究/管理世界/中国工业经济等中文期刊，或英文SSCI期刊）。

## 报告骨架

```
## 实证结果

### 1. 描述性统计

{三线表格式描述统计表，表号：Table 1}

### 2. 基准回归

**Table 2: Baseline Regression Results**

{三线表格式回归系数表}

Notes: t-statistics in parentheses. Standard errors are {se_type}. 
***p<0.01, **p<0.05, *p<0.1.

{解读段落，标注可信度标签}

### 3. 稳健性检验（如有）

**Table 3: Robustness Checks**

{稳健性检验汇总表}

Notes: {说明每个检验项的设置方式}
```

## 格式要求

- 表号用英文编号（Table 1, Table 2, ...）
- 变量名用英文缩写
- 表注用英文（投稿英文期刊）或中文（投稿中文期刊）
- 系数和t值分别保留3位小数
- 显著性标注：***p<0.01, **p<0.05, *p<0.1
- R²和调整R²均需报告
- 样本量N在表格底部报告
- 每张表下方有Notes段落说明标准误类型和控制变量
- 控制变量在表注中说明"All models include {controls_list}"

## Tab分隔复制块

默认不附 Tab 分隔复制块。仅当用户明确要求可复制表格时，才额外提供 TSV 代码块。
