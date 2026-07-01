"""统一文件加载接口，支持 CSV / Excel。
从 01_EmpiricalAgent/api/services/data_loader.py 迁移，按 PRD 风险清单第2项移除了
pyreadstat / .dta 支持，降低安装失败率（MVP阶段不支持 Stata 文件直读）。
"""
import io
import pandas as pd


def load_file(content: bytes, filename: str) -> pd.DataFrame:
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "csv":
        # 注：gbk/gb2312 几乎能把任意字节序列解码成合法字符，遇到编码猜错但未触发
        # UnicodeDecodeError 的极端情况会静默产生乱码而非报错；该行为继承自迁移源
        # 文件（01_EmpiricalAgent/api/services/data_loader.py），未做改动。
        for encoding in ["utf-8", "gbk", "gb2312", "utf-8-sig"]:
            try:
                return pd.read_csv(io.BytesIO(content), encoding=encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"无法识别 {filename} 的编码格式")

    elif ext == "xlsx":
        return pd.read_excel(io.BytesIO(content))

    else:
        raise ValueError(f"不支持的文件格式：{ext}，本版本仅支持 .csv / .xlsx 文件")
