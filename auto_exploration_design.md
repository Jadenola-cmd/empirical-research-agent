# 自动模型探索模式设计

## 功能定位

在现有三层架构基础上，新增**自动探索模式**，让系统能够根据用户约束条件，自动尝试多种模型组合，并按指定准则推荐最优模型。

## 核心原则

1. **不破坏阻断协议**：所有探索仍需通过 Step 4A/4B 确认
2. **探索空间可控**：由用户明确定义候选变量、模型类型、变换方式
3. **评价准则透明**：清楚告知选择最优模型的依据
4. **数字完全溯源**：所有候选结果都来自 `engine/` 输出
5. **结果可追溯**：保留探索过程记录，便于人工复核

## 架构位置

```
modes/
├── research_explore.md    # 现有：人工探索模式
├── model_execute.md       # 现有：执行指定模型
├── result_iterate.md      # 现有：基于结果迭代
└── auto_exploration.md    # 新增：自动探索模式 [新增]

protocols/
├── exploration_space.md   # 新增：探索空间定义协议 [新增]
├── model_selection.md     # 新增：模型选择评价协议 [新增]
└── exploration_report.md  # 新增：探索结果报告协议 [新增]

engine/
├── model_comparison.py    # 新增：模型对比评价 [新增]
└── exploration_runner.py  # 新增：自动化探索编排器 [新增]

resources/
└── exploration_guide.md   # 新增：自动探索使用指南 [新增]
```

## 触发条件

用户出现以下意图时进入自动探索模式：

1. "帮我找最好的模型组合"
2. "自动测试不同的控制变量组合"
3. "尝试多种模型并比较哪个效果最好"
4. "优化模型设定，提高解释力"
5. "探索可能的变量组合"

## 核心流程

### Step 0：探索意图识别
```
用户请求 → 意图判断 → 是否明确指定固定模型？
├─ 是 → 模型执行模式
└─ 否 → 探索空间构建 → 是否要求自动化？
    ├─ 是 → 自动探索模式
    └─ 否 → 研究探索模式
```

### Step 1：探索空间构建（新增）
读取 `protocols/exploration_space.md`，构建搜索空间：

**必须明确定义的维度：**
1. **候选核心变量**：Y 的备选、X 的备选
2. **候选控制变量池**：可选控制变量列表
3. **模型类型空间**：OLS/FE/RE 等
4. **固定效应配置**：entity/time/year FE 的开关组合
5. **变量变换空间**：log/标准化/缩尾等可选变换
6. **样本策略空间**：不同缩尾比例、异常值处理方式
7. **约束条件**：最大候选模型数、计算时间限制

### Step 2：探索执行编排
调用 `engine/exploration_runner.py`，按以下策略：

**搜索策略选择：**
1. **贪婪搜索**（默认）：按某种准则逐步优化
2. **网格搜索**：遍历所有组合（小空间）
3. **随机搜索**：大空间下随机采样
4. **贝叶斯优化**：基于已有结果智能采样（高级）

**执行约束：**
- 单次会话最多运行 N 个候选模型（默认10，用户可调整）
- 每个候选模型都走完整的标准流水线
- 失败的模型不阻塞整个探索

### Step 3：模型对比评价
调用 `engine/model_comparison.py`，对每个候选模型输出：

```json
{
  "model_id": "m1",
  "model_spec": {...},
  "metrics": {
    "r_squared": 0.45,
    "adj_r_squared": 0.43,
    "aic": -128.5,
    "bic": -115.2,
    "f_statistic": 12.3,
    "rmse": 0.023
  },
  "diagnostics": {
    "heteroskedasticity": "fail",
    "multicollinearity": "pass",
    "normality": "warn"
  },
  "ranking": {
    "by_adj_r2": 3,
    "by_aic": 1,
    "by_bic": 2
  }
}
```

### Step 4：最优推荐
基于用户指定的评价准则（默认 AIC），推荐前 K 个模型：

- 展示推荐理由：指标对比、统计显著性、经济含义
- 标注可信度：[VERIFIED] 若通过所有诊断，[WARN] 若部分失败
- 提供详细对比表：三线表格式，展示关键指标

### Step 5：探索过程报告
按 `protocols/exploration_report.md` 输出：

```markdown
# 自动模型探索报告

## 任务卡
- 探索模式：自动探索
- 搜索空间：3个Y备选 × 2个X备选 × 5个控制变量组合 × 2种模型 = 60个候选
- 实际执行：12个模型（8个通过诊断）
- 评价准则：AIC
- 计算耗时：45秒

## 探索空间定义
- Y 候选：Innovation_Patents, Innovation_R&D, Innovation_Quality
- X 候选：Tax_Avoidance_BTD, Tax_Avoidance_ETR
- 控制变量池：Size, Age, Lev, ROA, Growth, SOE, Board_Size, Indep_Ratio
- 模型类型：OLS, Panel FE
- 评价准则：AIC优先，兼顾R²调整后

## 最优模型推荐（Top 3）

### 模型1：[VERIFIED]
**Model Spec**: Y=Innovation_Patents, X=Tax_Avoidance_BTD, Controls=Size+Age+Lev+ROA, Model=Panel FE
**推荐理由**: AIC=-132.5（最优），R²调整后=0.42（第2），所有诊断通过

**回归结果**:
| 变量 | 系数 | 标准误 | t值 | p值 |
|---|---|---|---|---|
| Tax_Avoidance_BTD | -0.023*** | 0.007 | -3.28 | 0.001 |
| Size | 0.015** | 0.006 | 2.50 | 0.012 |
| Age | -0.008 | 0.005 | -1.60 | 0.110 |
| Lev | 0.012* | 0.007 | 1.71 | 0.087 |
| ROA | 0.021*** | 0.005 | 4.20 | 0.000 |

### 模型2：[WARN]
**Model Spec**: Y=Innovation_R&D, X=Tax_Avoidance_BTD, Controls=Size+ROA+Growth, Model=OLS
**推荐理由**: R²调整后=0.45（最高），但异方差检验未通过

### 模型3：[VERIFIED]
**Model Spec**: Y=Innovation_Patents, X=Tax_Avoidance_ETR, Controls=Size+Lev+ROA, Model=Panel FE
**推荐理由**: AIC=-128.2（第3），R²调整后=0.40，所有诊断通过

## 完整对比表
[省略...]

## 探索过程记录
- 总候选：60个
- 实际执行：12个
- 成功：8个
- 失败：4个（原因：数据缺失、奇异矩阵）
- 计算时间：45秒

## 下一步建议
1. 基于模型1生成完整论文表格
2. 对模型1进行稳健性检验
3. 尝试添加行业固定效应进一步优化
```

## 防护措施

### 1. 探索空间限制
- 默认最多100个候选组合，用户可调整
- 单个候选模型计算超时5分钟
- 总探索时间不超过10分钟

### 2. 阻断协议保持
- 每个候选模型仍需通过 Step 4A/4B 确认（首次确认后，同空间的后续模型可快进）
- 数据质检 [P1] 只执行一次
- 方法选择 [P2] 每个候选独立验证

### 3. 避免过拟合
- 强制输出 AIC/BIC 信息准则（含惩罚项）
- 要求样本量与参数比例检查
- 异质性检验识别过度优化风险

### 4. 经济含义保持
- 自动探索不得改变变量方向和含义
- X→Y 的因果方向必须明确
- 控制变量加入需有理论依据

## 与现有模式的关系

```
标准流水线
├─ Step 0: 研究阶段识别
│   ├─ 结果迭代模式（有上一轮 spec）
│   ├─ 模型执行模式（用户给明确 spec）
│   ├─ 研究探索模式（数据+主题，无 spec）
│   └─ 自动探索模式（数据+主题，要求自动化）[新增]
│
├─ [P0-P4] 核心流水线（共享）
│
└─ 输出分支
    ├─ 报告生成（现有）
    ├─ 代码生成（现有）
    └─ 探索报告（新增）
```

## 用户界面示例

### 激活自动探索
用户：我有数据，想看避税对企业创新的影响，帮我自动找最好的模型组合

Agent：进入自动探索模式。需要确认探索空间：

**探索空间构建：**
- Y 候选：有哪些创新指标可用？
- X 候选：用哪个避税指标？
- 控制变量池：提供可选控制变量列表
- 模型类型：OLS/Panel FE/Panel RE 都尝试吗？
- 评价准则：推荐 AIC，还是 R²调整后？

用户确认后，自动执行探索，输出对比报告。

### 细化探索
用户：只尝试不同的控制变量组合，其他保持不变

Agent：简化探索空间为：
- 固定：Y=Innovation_Patents, X=Tax_Avoidance_BTD, Model=Panel FE
- 探索：5个控制变量的所有子集组合（2^5=32个候选）
- 执行中...（显示进度）

### 人工干预
用户：暂停探索，我想看看目前的中间结果

Agent：输出当前已完成的候选模型对比表，允许用户：
- 调整搜索策略
- 收窄探索空间
- 选择特定候选继续

## 实现优先级

### P0（核心功能）
1. `protocols/exploration_space.md` - 探索空间定义协议
2. `engine/model_comparison.py` - 模型对比评价
3. `modes/auto_exploration.md` - 自动探索模式定义
4. 贪婪搜索实现

### P1（扩展功能）
1. `engine/exploration_runner.py` - 自动化探索编排器
2. 网格搜索实现
3. `protocols/model_selection.md` - 模型选择评价协议
4. `protocols/exploration_report.md` - 探索结果报告协议

### P2（高级功能）
1. 随机搜索实现
2. 贝叶斯优化集成
3. 交互式探索（用户可中途干预）
4. `resources/exploration_guide.md` - 使用指南

## 风险与限制

1. **计算成本**：大量模型耗时，需设置合理限制
2. **数据挖掘风险**：过度优化可能导致虚假结果
3. **理论缺失**：自动化可能忽视经济理论约束
4. **解释困难**：复杂搜索路径难以追溯

**对策**：
- 强制输出探索过程记录
- 要求用户明确探索空间边界
- 标注 [AUTO_EXPLORATION] 提醒人工复核
- 建议结合理论指导探索方向

## 文件依赖关系

```
modes/auto_exploration.md
├─ 依赖： protocols/protocol_order.md
├─ 依赖： protocols/exploration_space.md
├─ 依赖： protocols/model_spec.md
├─ 调用： engine/exploration_runner.py
└─ 输出： protocols/exploration_report.md

engine/exploration_runner.py
├─ 调用： engine/ols.py / engine/panel.py
├─ 调用： engine/model_comparison.py
└─ 依赖： method_capability.json

engine/model_comparison.py
├─ 输入：多个模型的 engine 输出 JSON
└─ 输出：对比指标 JSON
```

## 下一步行动

1. 确认此设计方案是否符合项目架构原则
2. 评审探索空间定义的合理性
3. 确定评价准则的优先级
4. 开始 P0 核心功能实现