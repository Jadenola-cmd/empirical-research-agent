"""探索数据文件结构，输出到文件"""
import pandas as pd
import json
import sys
import io

# 重定向stdout为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

files = {
    'CG_Capchg': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/CG_Capchg.xlsx',
    'CG_Ybasic': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/CG_Ybasic.xlsx', 
    'FI_T1': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T1.xlsx',
    'FI_T4': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T4.xlsx',
    'FI_T5': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T5.xlsx',
    'FI_T8': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FI_T8.xlsx',
    'FS_Combas': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FS_Combas.xlsx',
    'FS_Comscfi': 'D:/99_Archive/bad genius/12.9资本结构影响因素/数据/FS_Comscfi.xlsx',
}

result = {}
for name, path in files.items():
    try:
        df = pd.read_excel(path)
        result[name] = {
            'rows': len(df),
            'cols': len(df.columns),
            'columns': list(df.columns),
            'dtypes': {c: str(df[c].dtype) for c in df.columns},
            'sample': df.head(3).to_dict(orient='records'),
            'null_counts': df.isnull().sum().to_dict(),
        }
    except Exception as e:
        result[name] = {'error': str(e)}

with open('D:/00_Workspace/99_Sandbox/empirical技能-test/test-data/data_structure.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print("完成，已写入 data_structure.json")
