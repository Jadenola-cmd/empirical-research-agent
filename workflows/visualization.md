# Workflow: Visualization — 可视化

## 触发条件

- 用户说"帮我画个图"、"可视化"、"做张图看看"
- method_selection 决策树路由到 visualization

## 前置检查

- [ ] 分析结果已存在（主回归或其他分析已完成）
- [ ] 用户 tier >= pro

## 支持的图表类型

| 图表类型 | 适用场景 | 引擎命令 |
|---------|---------|---------|
| 系数图（coefficient plot） | 展示回归系数及置信区间 | `engine/visualization.py --type coef` |
| 趋势图（trend plot） | 展示时间序列或面板趋势 | `engine/visualization.py --type trend` |
| 分布图（distribution plot） | 展示变量分布（直方图+密度） | `engine/visualization.py --type dist` |
| 散点图（scatter plot） | 展示两变量关系+拟合线 | `engine/visualization.py --type scatter` |
| 平行趋势图（event study） | DID的平行趋势检验 | `engine/visualization.py --type event_study` |
| 倾向得分分布图 | PSM的匹配前后对比 | `engine/visualization.py --type propensity` |

## 执行

```bash
python engine/visualization.py <parquet_path> --type <chart_type> [--columns <col1,col2,...>] [--group <group_var>] [--output <output_path>]
```

输出为 PNG 图片路径。

## 输出

- 嵌入 Markdown 图片语法显示图表：`![描述](图片路径)`
- 图表下方附一段简短解读（描述图表展示的核心信息）
- 图表中所有数字来自 engine 输出，标注 [VERIFIED]

## 风格规范

- 学术风格：简洁配色，无多余装饰
- 坐标轴标签清晰（中文或英文，统一）
- 显著性标注：***p<0.01, **p<0.05, *p<0.1
- 图表标题简明，图注完整

## 完成检查

- [ ] 图表已生成并嵌入
- [ ] 图表解读文字
- [ ] 图表风格符合学术规范
- [ ] 所有数字可溯源到 engine 输出
