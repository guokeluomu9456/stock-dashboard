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