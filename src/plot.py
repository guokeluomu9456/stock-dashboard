"""
绑图逻辑模块
"""

from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_candlestick(
    ax: plt.Axes,
    df: pd.DataFrame,
    dates: pd.Index,
) -> None:
    """
    绘制K线图

    Args:
        ax: matplotlib Axes 对象
        df: 股票数据 DataFrame
        dates: 日期索引
    """
    width = 0.6
    colors = np.where(df["Close"] >= df["Open"], "red", "green")
    idx = np.arange(len(df))

    # 上下影线：用 vlines 一次画完（向量化）
    ax.vlines(idx, df["Low"].values, df["High"].values, color=colors, linewidth=0.8)

    # 实体柱：用 bar 一次画完（向量化）
    body_height = df["Close"].values - df["Open"].values
    # 处理开盘=收盘的扁平柱（高度为0时给一个最小高度）
    body_height = np.where(body_height == 0, 0.001, body_height)
    ax.bar(idx, body_height, width,
           bottom=df["Open"].values, color=colors, edgecolor=colors, linewidth=0.5)

    # 日期标签
    tick_step = max(1, len(dates) // 10)
    ax.set_xticks(idx[::tick_step])
    ax.set_xticklabels(
        [dates[i].strftime("%Y-%m-%d") for i in range(0, len(dates), tick_step)],
        rotation=45, ha="right", fontsize=8
    )
    ax.set_xlim(-0.5, len(df) - 0.5)


def plot_kdj(
    ax: plt.Axes,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
) -> None:
    """
    绘制KDJ指标图

    Args:
        ax: matplotlib Axes 对象
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
    """
    from .indicators import calc_kdj

    K, D, J = calc_kdj(high, low, close)

    ax.plot(K.index, K.values, label="K", color="blue", linewidth=1)
    ax.plot(D.index, D.values, label="D", color="orange", linewidth=1)
    ax.plot(J.index, J.values, label="J", color="purple", linewidth=1)

    ax.axhline(y=80, color="gray", linestyle="--", linewidth=0.8)
    ax.axhline(y=20, color="gray", linestyle="--", linewidth=0.8)

    ax.fill_between(K.index, K.values, D.values, alpha=0.2, color="blue")

    ax.set_ylabel("KDJ")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)


def plot_rsi(
    ax: plt.Axes,
    rsi: pd.Series,
) -> None:
    """
    绘制RSI指标图

    Args:
        ax: matplotlib Axes 对象
        rsi: RSI 序列
    """
    ax.plot(rsi.index, rsi.values, color="purple", linewidth=1, label="RSI(14)")

    ax.axhline(y=70, color="red", linestyle="--", linewidth=0.8, label="Overbought (70)")
    ax.axhline(y=30, color="green", linestyle="--", linewidth=0.8, label="Oversold (30)")

    ax.fill_between(rsi.index, rsi.values, 70, where=rsi >= 70, color="red", alpha=0.2)
    ax.fill_between(rsi.index, rsi.values, 30, where=rsi <= 30, color="green", alpha=0.2)

    ax.set_ylabel("RSI")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)


def plot_macd(
    ax: plt.Axes,
    macd: pd.Series,
    signal: pd.Series,
    hist: pd.Series,
) -> None:
    """
    绘制MACD指标图

    Args:
        ax: matplotlib Axes 对象
        macd: MACD 线
        signal: 信号线
        hist: 柱状图
    """
    colors = np.where(hist >= 0, "red", "green")
    ax.bar(hist.index, hist.values, color=colors, width=1.0, alpha=0.6)
    ax.plot(macd.index, macd.values, color="blue", linewidth=1, label="MACD")
    ax.plot(signal.index, signal.values, color="orange", linewidth=1, label="Signal")
    ax.axhline(y=0, color="gray", linewidth=0.8)
    ax.set_ylabel("MACD")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)