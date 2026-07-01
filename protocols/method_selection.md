# Method Selection Protocol — 方法选择决策树

## 位置

路由决策 [P2]：在 protocol_order.md 中位于 data_audit 之后、workflow 执行之前。

## 决策树

```
用户研究问题
│
├─ "我想看看数据长什么样"
│   └─ → descriptive workflow
│
├─ "X和Y有关系吗？"（相关/影响/因素）
│   │
│   ├─ 截面数据（无个体+时间维度）
│   │   └─ → hypothesis workflow → ols
│   │
│   └─ 面板数据（有个体+时间维度）
│       └─ → hypothesis workflow → panel (FE/RE + Hausman)
│
├─ "X导致Y吗？"（因果推断）
│   │
│   ├─ 有面板 + 处理/对照组 + 政策时间点
│   │   ├─ 处理组选择非随机 → causal workflow → psm_did
│   │   └─ 处理组选择外生 → causal workflow → did
│   │
│   ├─ 截面 + 处理/对照组
│   │   └─ → causal workflow → psm
│   │
│   ├─ 有内生性担忧 + 有工具变量
│   │   └─ → causal workflow → iv [beta]
│   │
│   └─ 有断点/阈值规则
│       └─ → causal workflow → rd [planned]
│
├─ "X通过什么渠道影响Y？"（机制分析）
│   │
│   ├─ X → M → Y（中介路径）
│   │   └─ → mechanism workflow → mediation
│   │
│   └─ X对Y的效应依赖于Z（调节效应）
│       └─ → mechanism workflow → moderation
│
├─ "X对Y的效应在不同组里一样吗？"（异质性）
│   └─ → heterogeneity workflow
│
├─ "结果稳不稳？"（稳健性检验）
│   └─ → robustness workflow（查 capability.json 中对应方法的 robustness_checks）
│
└─ "帮我画图"
    └─ → visualization workflow
```

## 决策后动作

1. 确定方法后，立即查询 `method_capability.json` 确认状态：
   - `available` → 继续
   - `beta` → 告知用户"该方法处于测试阶段，结果需谨慎解读"
   - `planned` → 告知用户"该方法尚未实现"，返回决策树重新选择
   - 不在 capability 中 → 告知"当前版本暂不支持该方法"
2. 确认 tier 层级，若用户 tier 不足，提示升级
3. 跳转到对应 workflow 文件执行

## 方法不支持时的处理

```
该方法暂不支持：
├─ capability 中有替代方法 → 建议替代方案
├─ capability 中无替代方法 → 告知"当前版本暂不支持，已记录需求"
└─ 用户坚持 → 不执行（anti_hallucination 协议禁止用近似方法替代）
```

## 与 capability.json 的关系

本文件是"给人看"的决策树（自然语言），method_capability.json 是"给机器看"的注册表（结构化数据）。
决策树叶子节点必须指向 capability.json 中存在的 method key。
