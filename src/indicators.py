"""
技术指标计算模块 - 向量化实现
"""

from typing import Tuple

import pandas as pd
import numpy as np

from .config import (
    KDJ_N,
    KDJ_M1,
    KDJ_M2,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    RSI_WINDOW,
    BB_WINDOW,
    BB_NUM_STD,
)


def calc_ma(series: pd.Series, window: int) -> pd.Series:
    """
    计算简单移动平均

    Args:
        series: 价格序列
        window: 窗口大小

    Returns:
        MA 序列
    """
    return series.rolling(window=window, min_periods=1).mean()


def calc_ema(series: pd.Series, span: int) -> pd.Series:
    """
    计算指数移动平均

    Args:
        series: 价格序列
        span: 跨度

    Returns:
        EMA 序列
    """
    return series.ewm(span=span, adjust=False, min_periods=1).mean()


def calc_macd(
    close: pd.Series,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算 MACD 指标

    Args:
        close: 收盘价序列
        fast: 快线周期
        slow: 慢线周期
        signal: 信号线周期

    Returns:
        (MACD线, 信号线, 柱状图)
    """
    ema_fast = calc_ema(close, fast)
    ema_slow = calc_ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calc_ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def calc_kdj(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    n: int = KDJ_N,
    m1: int = KDJ_M1,
    m2: int = KDJ_M2,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算 KDJ 指标（向量化实现）

    Args:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        n: RSV 周期
        m1: K 周期
        m2: D 周期

    Returns:
        (K, D, J) 序列
    """
    # 计算 RSV（未成熟随机值）
    lowest_low = low.rolling(window=n, min_periods=1).min()
    highest_high = high.rolling(window=n, min_periods=1).max()
    rsv = (close - lowest_low) / (highest_high - lowest_low + 1e-9) * 100
    rsv = rsv.fillna(50)

    # 使用 ewm 向量化计算 K 和 D
    # K_t = (1 - 1/3) * K_{t-1} + 1/3 * RSV_t  =>  alpha = 1/3
    # D_t = (1 - 1/3) * D_{t-1} + 1/3 * K_t    =>  alpha = 1/3
    k_series = rsv.ewm(alpha=1 / m1, adjust=False).mean()
    d_series = k_series.ewm(alpha=1 / m2, adjust=False).mean()

    # 计算 J 值
    j_series = m1 * k_series - (m1 - 1) * d_series

    return k_series, d_series, j_series


def calc_bollinger(
    series: pd.Series,
    window: int = BB_WINDOW,
    num_std: float = BB_NUM_STD,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算布林带

    Args:
        series: 价格序列
        window: 窗口大小
        num_std: 标准差倍数

    Returns:
        (上轨, 中轨, 下轨)
    """
    ma = calc_ma(series, window)
    std = series.rolling(window=window, min_periods=1).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return upper, ma, lower


def calc_rsi(close: pd.Series, window: int = RSI_WINDOW) -> pd.Series:
    """
    计算 RSI 相对强弱指标（向量化实现）

    Args:
        close: 收盘价序列
        window: RSI 周期

    Returns:
        RSI 序列
    """
    delta = close.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    # 使用 ewm 计算指数移动平均
    avg_gain = gain.ewm(alpha=1 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))

    return rsi


def detect_cross(
    ma_fast: pd.Series,
    ma_slow: pd.Series,
) -> list[tuple[str, pd.Timestamp]]:
    """
    检测均线金叉/死叉（向量化实现）

    Args:
        ma_fast: 快线序列
        ma_slow: 慢线序列

    Returns:
        [(交叉类型, 日期), ...]，交叉类型为 'gold' 或 'death'
    """
    diff = ma_fast - ma_slow

    # 检测符号变化
    prev_diff = diff.shift(1)
    curr_diff = diff

    gold_cross = (prev_diff < 0) & (curr_diff > 0)
    death_cross = (prev_diff > 0) & (curr_diff < 0)

    gold_dates = gold_cross[gold_cross].index.tolist()
    death_dates = death_cross[death_cross].index.tolist()

    # 合并并按日期排序
    all_crosses: list[tuple[str, pd.Timestamp]] = (
        [("gold", date) for date in gold_dates]
        + [("death", date) for date in death_dates]
    )
    all_crosses.sort(key=lambda x: x[1])

    return all_crosses