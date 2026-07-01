# Python Reference — Python依赖与实现参考

## 计算引擎依赖

engine/ 层使用以下Python库：

### 核心依赖（所有方法必需）
```
pandas >= 2.0.0
numpy >= 1.24.0
pyarrow >= 12.0.0  # parquet读写
```

### 统计建模（回归/面板/DID/IV）
```
statsmodels >= 0.14.0
linearmodels >= 5.0   # 面板回归 + IV
scipy >= 1.10.0
```

### 因果推断
```
scikit-learn >= 1.3.0  # PSM倾向得分估计
```

### 可视化
```
matplotlib >= 3.7.0
```

### 数据清洗
```
openpyxl >= 3.1.0  # Excel读取
```

## 引擎脚本接口规范

所有 engine/*.py 文件遵循统一接口：

```python
# 用法统一
python engine/<script>.py <parquet_path> '<config_json>'

# 输出统一
# stdout: JSON格式结果，{"status": "success", ...} 或 {"error": "..."}
# exit code: 0=成功, 1=失败
```

### config_json 通用字段
| 字段 | 类型 | 说明 |
|------|------|------|
| dv | str | 因变量列名 |
| iv | list | 自变量列名列表 |
| controls | list | 控制变量列名列表 |
| se_type | str | 标准误类型（HC0/HC1/HC2/HC3/clustered） |
| cluster | str | 聚类变量（se_type=clustered时必需） |

### 结果JSON通用字段
| 字段 | 类型 | 说明 |
|------|------|------|
| coefficients | dict | 系数字典 {var: {coef, se, t_stat, p_value}} |
| n | int | 有效样本量 |
| r2 | float | R²（面板为r2_within） |
| f_stat | float | F统计量 |
| f_pvalue | float | F检验p值 |

## 添加新方法的步骤

1. 在 `engine/` 下创建 `new_method.py`
2. 实现 `run_new_method(df, **config) -> dict` 函数
3. 在 `method_capability.json` 中注册
4. 在 `protocols/method_selection.md` 决策树中添加分支
5. 在 `workflows/` 中创建对应编排文件（如适用现有分类则复用）
6. 在 `resources/stata_reference.md` 中添加Stata对照
