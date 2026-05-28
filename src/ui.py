"""
Streamlit UI 模块
"""

from datetime import datetime
from typing import Optional

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from .data import get_ticker_symbol, fetch_stock_data
from .indicators import (
    calc_ma,
    calc_bollinger,
    calc_kdj,
    calc_macd,
    calc_rsi,
    detect_cross,
)
from .plot import plot_candlestick, plot_kdj, plot_rsi, plot_macd
from .config import MARKET_CONFIG


def render_sidebar() -> tuple[str, str, dict[str, bool]]:
    """
    渲染侧边栏并返回用户配置

    Returns:
        (市场类型, 股票代码, 指标显示选项字典)
    """
    st.sidebar.header("设置")

    market = st.sidebar.selectbox("市场", ["A股", "港股", "美股"])

    default_symbol = "000001" if market == "A股" else ("0700" if market == "港股" else "AAPL")
    symbol_input = st.sidebar.text_input("股票代码", value=default_symbol)

    period = st.sidebar.selectbox("时间周期", ["6mo", "1y", "2y", "5y"], index=1)

    show_ma = st.sidebar.checkbox("均线 (MA5/10/20)", value=True)
    show_macd = st.sidebar.checkbox("MACD", value=True)
    show_kdj = st.sidebar.checkbox("KDJ", value=True)
    show_bollinger = st.sidebar.checkbox("布林带", value=True)
    show_rsi = st.sidebar.checkbox("RSI", value=True)

    options = {
        "ma": show_ma,
        "macd": show_macd,
        "kdj": show_kdj,
        "bollinger": show_bollinger,
        "rsi": show_rsi,
    }

    return market, symbol_input, period, options


def render_stock_info(df: pd.DataFrame) -> None:
    """
    渲染股票信息指标卡片

    Args:
        df: 股票数据 DataFrame
    """
    latest = df.iloc[-1]
    prev_close = df.iloc[-2]["Close"]
    change = latest["Close"] - prev_close
    pct = change / prev_close * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("最新价", f"{latest['Close']:.2f}", f"{change:+.2f} ({pct:+.2f}%)")
    col2.metric("最高", f"{latest['High']:.2f}")
    col3.metric("最低", f"{latest['Low']:.2f}")
    col4.metric("成交量", f"{latest['Volume'] / 1e6:.2f}M")


def render_main_chart(
    ax: plt.Axes,
    df: pd.DataFrame,
    show_ma: bool,
    show_bollinger: bool,
) -> None:
    """
    渲染主图（K线 + 布林带 + 均线）

    Args:
        ax: matplotlib Axes 对象
        df: 股票数据 DataFrame
        show_ma: 是否显示均线
        show_bollinger: 是否显示布林带
    """
    plot_candlestick(ax, df, df.index)

    # 布林带
    if show_bollinger:
        upper, ma, lower = calc_bollinger(df["Close"])
        ax.fill_between(upper.index, lower.values, upper.values, alpha=0.1, color="gray")
        ax.plot(upper.index, upper.values, color="gray", linewidth=0.8, linestyle="--", label="BB Upper")
        ax.plot(lower.index, lower.values, color="gray", linewidth=0.8, linestyle="--", label="BB Lower")

    # 均线
    if show_ma:
        ma5 = calc_ma(df["Close"], 5)
        ma10 = calc_ma(df["Close"], 10)
        ma20 = calc_ma(df["Close"], 20)

        ax.plot(ma5.index, ma5.values, label="MA5", linewidth=0.8)
        ax.plot(ma10.index, ma10.values, label="MA10", linewidth=0.8)
        ax.plot(ma20.index, ma20.values, label="MA20", linewidth=0.8)

        # 金叉/死叉标注
        crosses = detect_cross(ma5, ma20)
        for cross_type, date in crosses:
            if date in df.index:
                price = df.loc[date, "Close"]
                color = "green" if cross_type == "gold" else "red"
                marker = "^" if cross_type == "gold" else "v"
                label = "金叉" if cross_type == "gold" else "死叉"
                ax.scatter(date, price, color=color, marker=marker, s=100, zorder=5, label=label)

    ax.set_title("K线走势", fontsize=12)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper left")
    ax.grid(True, alpha=0.3)


def render_charts(
    df: pd.DataFrame,
    options: dict[str, bool],
    symbol: str,
) -> None:
    """
    渲染所有图表

    Args:
        df: 股票数据 DataFrame
        options: 指标显示选项
        symbol: 股票代码
    """
    show_ma = options.get("ma", True)
    show_macd = options.get("macd", True)
    show_kdj = options.get("kdj", True)
    show_bollinger = options.get("bollinger", True)
    show_rsi = options.get("rsi", True)

    # 统计显示的子图数量
    subplot_count = 1 + sum(1 for opt in [show_macd, show_kdj, show_rsi] if opt)
    height_ratios = [3] + [1] * (subplot_count - 1)

    fig, axes = plt.subplots(subplot_count, 1, figsize=(14, 3 + 3 * subplot_count), gridspec_kw={"height_ratios": height_ratios})

    if subplot_count == 1:
        axes = [axes]

    ax_idx = 0

    # 主图：K线
    render_main_chart(axes[ax_idx], df, show_ma, show_bollinger)
    ax_idx += 1

    # MACD
    if show_macd:
        macd, signal, hist = calc_macd(df["Close"])
        plot_macd(axes[ax_idx], macd, signal, hist)
        plt.setp(axes[ax_idx].get_xticklabels(), visible=False)
        ax_idx += 1

    # KDJ
    if show_kdj:
        K, D, J = calc_kdj(df["High"], df["Low"], df["Close"])
        plot_kdj(axes[ax_idx], K, D, J)
        plt.setp(axes[ax_idx].get_xticklabels(), visible=False)
        ax_idx += 1

    # RSI
    if show_rsi:
        rsi = calc_rsi(df["Close"])
        plot_rsi(axes[ax_idx], rsi)

    plt.tight_layout()
    st.pyplot(fig)


def run_app() -> None:
    """
    运行 Streamlit 应用主逻辑
    """
    st.set_page_config(page_title="股票技术分析", layout="wide")
    st.title("📊 股票技术分析 Dashboard")

    market, symbol_input, period, options = render_sidebar()

    if st.sidebar.button("🔍 分析", type="primary"):
        try:
            symbol = get_ticker_symbol(symbol_input, market)

            with st.spinner(f"正在获取 {symbol} 数据..."):
                df = fetch_stock_data(symbol, period)

            if df is None or df.empty:
                st.error("获取数据失败，请检查股票代码是否正确")
            else:
                st.subheader(f"{symbol} 行情 & 技术指标")

                render_stock_info(df)
                render_charts(df, options, symbol)

                st.success(f"数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except ValueError as e:
            st.error(str(e))
        except ConnectionError as e:
            st.error(str(e))
        except RuntimeError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"发生未知错误: {e}")