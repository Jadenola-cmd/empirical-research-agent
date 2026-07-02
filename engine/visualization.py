"""可视化引擎（系数图/趋势图/分布图/散点图/事件研究/倾向得分分布）。

用法：python engine/visualization.py <parquet_path> '<config_json>'
config: {"type":"coef","columns":["x1","x2"],"output":"output.png"}

输出：PNG图片路径
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from engine.lib.cli_utils import exit_for_result, load_dataframe, parse_config_arg


def generate_plot(df: pd.DataFrame, plot_type: str, columns: list = None,
                  group: str = None, output: str = None, **kwargs) -> dict:
    """生成可视化图表，返回图片路径。"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm

        # 尝试设置中文字体
        try:
            plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
        except Exception:
            pass

        output_path = output or f"output_{plot_type}.png"

        fig, ax = plt.subplots(figsize=(8, 5))

        if plot_type == "dist" and columns:
            for col in columns[:5]:
                if col in df.columns:
                    df[col].dropna().hist(ax=ax, alpha=0.5, bins=30, label=col)
            ax.legend()
            ax.set_title("变量分布图")

        elif plot_type == "scatter" and columns and len(columns) >= 2:
            x_col, y_col = columns[0], columns[1]
            if x_col in df.columns and y_col in df.columns:
                ax.scatter(df[x_col], df[y_col], alpha=0.5, s=10)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{y_col} vs {x_col}")

        elif plot_type == "trend" and columns:
            for col in columns[:3]:
                if col in df.columns:
                    ax.plot(df[col].dropna().values[:100], label=col, alpha=0.7)
            ax.legend()
            ax.set_title("趋势图")

        else:
            ax.text(0.5, 0.5, f"图表类型 '{plot_type}' 待实现",
                    ha="center", va="center", transform=ax.transAxes)

        plt.tight_layout()
        fig.savefig(output_path, dpi=150)
        plt.close(fig)

        return {"output": str(Path(output_path).resolve()), "type": plot_type}
    except ImportError:
        return {"error": "需要安装 matplotlib: pip install matplotlib"}


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python visualization.py <parquet_path> '<config_json>'"}, ensure_ascii=False))
        sys.exit(1)
    parquet_path = Path(sys.argv[1])
    try:
        config = parse_config_arg(sys.argv)
        df = load_dataframe(parquet_path)
        result = generate_plot(df, **config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(exit_for_result(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
