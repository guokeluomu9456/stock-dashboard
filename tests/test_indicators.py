"""
indicators 模块单元测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TestCalcMA:
    """测试 MA 计算"""

    def test_calc_ma_normal(self):
        """测试正常数据"""
        from src.indicators import calc_ma

        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        result = calc_ma(data, 5)

        # MA5 for index 4 should be (1+2+3+4+5)/5 = 3
        assert abs(result.iloc[4] - 3.0) < 0.01
        # MA5 for last index should be (6+7+8+9+10)/5 = 8
        assert abs(result.iloc[-1] - 8.0) < 0.01

    def test_calc_ma_small_window(self):
        """测试窗口大于数据长度"""
        from src.indicators import calc_ma

        data = pd.Series([1, 2, 3])
        result = calc_ma(data, 5)

        # 应该返回所有数据的平均值
        assert result.iloc[-1] == 2.0


class TestCalcEMA:
    """测试 EMA 计算"""

    def test_calc_ema_normal(self):
        """测试正常数据"""
        from src.indicators import calc_ema

        data = pd.Series([1, 2, 3, 4, 5])
        result = calc_ema(data, 3)

        assert len(result) == len(data)
        assert result.iloc[-1] > result.iloc[0]  # 价格上涨，EMA 应该上涨


class TestCalcMACD:
    """测试 MACD 计算"""

    def test_macd_returns_three_series(self):
        """测试返回三个序列"""
        from src.indicators import calc_macd

        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 5)
        macd, signal, hist = calc_macd(data)

        assert len(macd) == len(data)
        assert len(signal) == len(data)
        assert len(hist) == len(data)

    def test_macd_signal_line_smoother(self):
        """测试信号线比 MACD 线更平滑"""
        from src.indicators import calc_macd

        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 5)
        macd, signal, hist = calc_macd(data)

        # 信号线应该比 MACD 线变化更慢（更平滑）
        macd_diff = macd.diff().abs().mean()
        signal_diff = signal.diff().abs().mean()

        assert signal_diff < macd_diff


class TestCalcKDJ:
    """测试 KDJ 计算"""

    def test_kdj_returns_three_series(self):
        """测试返回 K, D, J 三个序列"""
        from src.indicators import calc_kdj

        dates = pd.date_range(start="2023-01-01", periods=20)
        high = pd.Series([100 + i * 0.1 for i in range(20)], index=dates)
        low = pd.Series([99 - i * 0.1 for i in range(20)], index=dates)
        close = pd.Series([99.5 + i * 0.1 for i in range(20)], index=dates)

        K, D, J = calc_kdj(high, low, close)

        assert len(K) == len(dates)
        assert len(D) == len(dates)
        assert len(J) == len(dates)

    def test_kdj_values_in_range(self):
        """测试 KDJ 值在合理范围内"""
        from src.indicators import calc_kdj

        dates = pd.date_range(start="2023-01-01", periods=30)
        high = pd.Series([100 + i * 0.1 for i in range(30)], index=dates)
        low = pd.Series([99 - i * 0.1 for i in range(30)], index=dates)
        close = pd.Series([99.5 + i * 0.05 for i in range(30)], index=dates)

        K, D, J = calc_kdj(high, low, close)

        # K 和 D 应该在 0-100 之间
        assert K.min() >= 0
        assert K.max() <= 100
        assert D.min() >= 0
        assert D.max() <= 100


class TestCalcBollinger:
    """测试布林带计算"""

    def test_bollinger_returns_three_series(self):
        """测试返回上轨、中轨、下轨"""
        from src.indicators import calc_bollinger

        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        upper, ma, lower = calc_bollinger(data, window=5)

        assert len(upper) == len(data)
        assert len(ma) == len(data)
        assert len(lower) == len(data)

    def test_bollinger_upper_greater_than_lower(self):
        """测试上轨大于下轨"""
        from src.indicators import calc_bollinger

        # 用更长数据确保 dropna 后长度一致
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        upper, ma, lower = calc_bollinger(data, window=5)

        # dropna 后截齐，取最短的长度
        valid_upper = upper.dropna().reset_index(drop=True)
        valid_ma = ma.dropna().reset_index(drop=True)
        valid_lower = lower.dropna().reset_index(drop=True)
        n = min(len(valid_upper), len(valid_ma), len(valid_lower))

        assert all(valid_upper.iloc[:n].values > valid_ma.iloc[:n].values)
        assert all(valid_ma.iloc[:n].values > valid_lower.iloc[:n].values)


class TestCalcRSI:
    """测试 RSI 计算"""

    def test_rsi_returns_series(self):
        """测试返回 RSI 序列"""
        from src.indicators import calc_rsi

        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        rsi = calc_rsi(data, window=5)

        assert len(rsi) == len(data)

    def test_rsi_values_in_range(self):
        """测试 RSI 值在 0-100 范围内"""
        from src.indicators import calc_rsi

        # 单调上涨的数据
        up_data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        rsi_up = calc_rsi(up_data, window=5)

        # 单调下跌的数据
        down_data = pd.Series([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        rsi_down = calc_rsi(down_data, window=5)

        # RSI 应该在 0-100 范围内
        assert rsi_up.min() >= 0
        assert rsi_up.max() <= 100
        assert rsi_down.min() >= 0
        assert rsi_down.max() <= 100


class TestDetectCross:
    """测试金叉死叉检测"""

    def test_detect_gold_cross(self):
        """测试金叉检测"""
        from src.indicators import detect_cross

        # 金叉：diff 从负变正（需要前一个差<0，后一个差>0）
        fast = pd.Series([1, 2, 2.5, 4, 5, 6, 7])   # diff: -2, -1, -0.5, 1, 2, 3, 4  → 在 i=3 从负变正
        slow = pd.Series([3, 3, 3, 3, 3, 3, 3])

        crosses = detect_cross(fast, slow)
        gold_crosses = [c for c in crosses if c[0] == "gold"]
        assert len(gold_crosses) >= 1, f"期望检测到金叉，实际: {gold_crosses}"

    def test_detect_death_cross(self):
        """测试死叉检测"""
        from src.indicators import detect_cross

        # 死叉：diff 从正变负（需要前一个差>0，后一个差<0）
        fast = pd.Series([7, 6, 4.5, 2, 1, 0, -1])  # diff: 4, 3, 1.5, -1, -2, -3, -4  → 在 i=3 从正变负
        slow = pd.Series([3, 3, 3, 3, 3, 3, 3])

        crosses = detect_cross(fast, slow)
        death_crosses = [c for c in crosses if c[0] == "death"]
        assert len(death_crosses) >= 1, f"期望检测到死叉，实际: {death_crosses}"

    def test_no_cross_when_parallel(self):
        """测试平行线无交叉"""
        from src.indicators import detect_cross

        fast = pd.Series([1, 2, 3, 4, 5])
        slow = pd.Series([1, 2, 3, 4, 5])  # 完全同步

        crosses = detect_cross(fast, slow)

        assert len(crosses) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])