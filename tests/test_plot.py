"""
plot 模块单元测试
"""
import pytest
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # 非交互式后端
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class TestCandlestickVectorized:
    """测试 K 线向量化绘制"""

    def test_candlestick_vectorized(self):
        """验证向量化实现存在且可调用"""
        from src.plot import plot_candlestick

        dates = pd.date_range("2024-01-01", periods=10)
        df = pd.DataFrame({
            "Open": [100] * 10,
            "High": [105] * 10,
            "Low": [95] * 10,
            "Close": [102] * 10,
        }, index=dates)

        fig, ax = plt.subplots()
        plot_candlestick(ax, df, dates)
        plt.close()

    def test_candlestick_performance(self):
        """验证向量化版本 365 天数据耗时 < 0.1s"""
        import time
        from src.plot import plot_candlestick

        # 生成 365 天假数据
        dates = pd.date_range("2024-01-01", periods=365)
        df = pd.DataFrame({
            "Open": np.random.uniform(90, 110, 365),
            "High": np.random.uniform(105, 115, 365),
            "Low": np.random.uniform(85, 95, 365),
            "Close": np.random.uniform(90, 110, 365),
        }, index=dates)

        fig, ax = plt.subplots()
        start = time.time()
        plot_candlestick(ax, df, dates)
        elapsed = time.time() - start
        plt.close()
        # 向量化版本应该在 0.1 秒内完成 365 条数据
        assert elapsed < 0.1, f"耗时 {elapsed:.2f}s，超过 0.1s 阈值，向量化未生效"

class TestKDJCalledOnce:
    """验证 KDJ 只计算一次"""

    def test_kdj_called_once_in_plot(self):
        """验证 plot_kdj 接受 K/D/J 序列，不在内部调 calc_kdj"""
        import src.plot as plot_module
        import src.indicators as ind
        
        # 检查 plot_kdj 源代码中不调用 calc_kdj
        import inspect
        source = inspect.getsource(plot_module.plot_kdj)
        assert "calc_kdj" not in source, "plot_kdj 不应在内部调用 calc_kdj"
        
    def test_plot_kdj_accepts_kdj_series(self):
        """验证 plot_kdj 新签名接受 K, D, J 序列"""
        from src.plot import plot_kdj
        import pandas as pd
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        
        dates = pd.date_range("2023-01-01", periods=30)
        K = pd.Series(range(30), index=dates)
        D = pd.Series(range(30, 60), index=dates)
        J = pd.Series(range(60, 90), index=dates)
        
        fig, ax = plt.subplots()
        # 新签名：直接传 K, D, J
        plot_kdj(ax, K, D, J)
        plt.close()
