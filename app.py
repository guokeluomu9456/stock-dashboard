"""
Stock Technical Analysis Dashboard
Python + Streamlit
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from datetime import datetime, timedelta
import hashlib
import pickle
import os

# ======================
# Config
# ======================
MARKET_CONFIG = {
    'A股': {'suffix': '', 'prefixes': ['SZ', 'SH']},
    '港股': {'suffix': '.HK', 'prefixes': []},
    '美股': {'suffix': '', 'prefixes': []},
}

CACHE_DIR = os.path.expanduser('~/.stock_dashboard_cache')

# ======================
# Cache
# ======================
def get_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)
    return CACHE_DIR

def cache_key(symbol: str, period: str) -> str:
    key_str = f"{symbol}_{period}"
    return hashlib.md5(key_str.encode()).hexdigest()

def read_cache(symbol: str, period: str) -> pd.DataFrame | None:
    key = cache_key(symbol, period)
    path = os.path.join(get_cache_dir(), f"{key}.pkl")
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    return None

def write_cache(symbol: str, period: str, df: pd.DataFrame):
    key = cache_key(symbol, period)
    path = os.path.join(get_cache_dir(), f"{key}.pkl")
    try:
        with open(path, 'wb') as f:
            pickle.dump(df, f)
    except Exception:
        pass

# ======================
# Data
# ======================
def get_ticker_symbol(raw: str, market: str) -> str:
    raw = raw.strip().upper()
    if market == '美股':
        return raw
    if market == '港股':
        if not raw.endswith('.HK'):
            return f"{raw}.HK"
        return raw
    # A股
    if raw.endswith('.SZ') or raw.endswith('.SH'):
        return raw
    # 自动判断深沪
    if raw.startswith('6'):
        return f"{raw}.SH"
    return f"{raw}.SZ"

def fetch_stock_data(symbol: str, period: str = '1y') -> pd.DataFrame | None:
    # 先读缓存
    df = read_cache(symbol, period)
    if df is not None:
        return df

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            return None
        write_cache(symbol, period, df)
        return df
    except Exception as e:
        return None

# ======================
# Indicators
# ======================
def calc_ma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window).mean()

def calc_ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def calc_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = calc_ema(close, fast)
    ema_slow = calc_ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calc_ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def calc_kdj(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 9, m1: int = 3, m2: int = 3):
    lowest_low = low.rolling(window=n).min()
    highest_high = high.rolling(window=n).max()
    rsv = (close - lowest_low) / (highest_high - lowest_low + 1e-9) * 100
    rsv = rsv.fillna(50)
    K = pd.Series(index=rsv.index, dtype=float)
    D = pd.Series(index=rsv.index, dtype=float)
    K.iloc[0] = 50
    D.iloc[0] = 50
    for i in range(1, len(rsv)):
        K.iloc[i] = (2/3) * K.iloc[i-1] + (1/3) * rsv.iloc[i]
        D.iloc[i] = (2/3) * D.iloc[i-1] + (1/3) * K.iloc[i]
    J = 3 * K - 2 * D
    return K, D, J

def calc_bollinger(series: pd.Series, window: int = 20, num_std: float = 2.0):
    ma = calc_ma(series, window)
    std = series.rolling(window=window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return upper, ma, lower

def calc_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def detect_cross(ma_fast: pd.Series, ma_slow: pd.Series):
    """检测金叉/死叉，返回交叉点索引列表"""
    crosses = []
    for i in range(1, len(ma_fast)):
        prev = ma_fast.iloc[i-1] - ma_slow.iloc[i-1]
        curr = ma_fast.iloc[i] - ma_slow.iloc[i]
        if prev < 0 and curr > 0:
            crosses.append(('gold', ma_fast.index[i]))
        elif prev > 0 and curr < 0:
            crosses.append(('death', ma_fast.index[i]))
    return crosses

# ======================
# Plot
# ======================
def plot_candlestick(ax, df: pd.DataFrame):
    width = 0.6
    for idx, (_, row) in enumerate(df.iterrows()):
        color = 'red' if row['Close'] >= row['Open'] else 'green'
        ax.plot([idx, idx], [row['Low'], row['High']], color=color, linewidth=0.8)
        ax.add_patch(plt.Rectangle((idx - width/2, row['Open']), width, row['Close'] - row['Open'],
                                    facecolor=color, edgecolor=color, linewidth=0.5))

def plot_kdj(df: pd.DataFrame, ax):
    high = df['High']
    low = df['Low']
    close = df['Close']
    K, D, J = calc_kdj(high, low, close)
    ax.plot(K.index, K.values, label='K', color='blue', linewidth=1)
    ax.plot(D.index, D.values, label='D', color='orange', linewidth=1)
    ax.plot(J.index, J.values, label='J', color='purple', linewidth=1)
    ax.axhline(y=80, color='gray', linestyle='--', linewidth=0.8)
    ax.axhline(y=20, color='gray', linestyle='--', linewidth=0.8)
    ax.fill_between(K.index, K.values, D.values, alpha=0.2, color='blue')
    ax.set_ylabel('KDJ')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

def plot_rsi(rsi: pd.Series, ax):
    ax.plot(rsi.index, rsi.values, color='purple', linewidth=1, label='RSI(14)')
    ax.axhline(y=70, color='red', linestyle='--', linewidth=0.8, label='Overbought (70)')
    ax.axhline(y=30, color='green', linestyle='--', linewidth=0.8, label='Oversold (30)')
    ax.fill_between(rsi.index, rsi.values, 70, where=rsi >= 70, color='red', alpha=0.2)
    ax.fill_between(rsi.index, rsi.values, 30, where=rsi <= 30, color='green', alpha=0.2)
    ax.set_ylabel('RSI')
    ax.set_ylim(0, 100)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

# ======================
# Streamlit UI
# ======================
st.set_page_config(page_title="股票技术分析", layout="wide")
st.title("📊 股票技术分析 Dashboard")

# 侧边栏
st.sidebar.header("设置")
market = st.sidebar.selectbox("市场", ['A股', '港股', '美股'])
default_symbol = '000001' if market == 'A股' else ('0700' if market == '港股' else 'AAPL')
symbol_input = st.sidebar.text_input("股票代码", value=default_symbol)
period = st.sidebar.selectbox("时间周期", ['6mo', '1y', '2y', '5y'], index=1)
show_ma = st.sidebar.checkbox("均线 (MA5/10/20)", value=True)
show_macd = st.sidebar.checkbox("MACD", value=True)
show_kdj = st.sidebar.checkbox("KDJ", value=True)
show_bollinger = st.sidebar.checkbox("布林带", value=True)
show_rsi = st.sidebar.checkbox("RSI", value=True)

if st.sidebar.button("🔍 分析", type="primary"):
    symbol = get_ticker_symbol(symbol_input, market)
    with st.spinner(f"正在获取 {symbol} 数据..."):
        df = fetch_stock_data(symbol, period)

    if df is None or df.empty:
        st.error("获取数据失败，请检查股票代码是否正确")
    else:
        # 信息
        latest = df.iloc[-1]
        change = latest['Close'] - df.iloc[-2]['Close']
        pct = change / df.iloc[-2]['Close'] * 100
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("最新价", f"{latest['Close']:.2f}", f"{change:+.2f} ({pct:+.2f}%)")
        col2.metric("最高", f"{latest['High']:.2f}")
        col3.metric("最低", f"{latest['Low']:.2f}")
        col4.metric("成交量", f"{latest['Volume']/1e6:.2f}M")

        st.subheader(f"{symbol} 行情 & 技术指标")

        # 主图：K线 + 布林带
        fig, axes = plt.subplots(4, 1, figsize=(14, 14), gridspec_kw={'height_ratios': [3, 1, 1, 1]})

        # K线
        ax_candle = axes[0]
        plot_candlestick(ax_candle, df)

        # 布林带
        if show_bollinger:
            upper, ma, lower = calc_bollinger(df['Close'])
            ax_candle.plot(ma.index, ma.values, label='MA20', color='orange', linewidth=1)
            ax_candle.fill_between(upper.index, lower.values, upper.values, alpha=0.1, color='gray')
            ax_candle.plot(upper.index, upper.values, color='gray', linewidth=0.8, linestyle='--')
            ax_candle.plot(lower.index, lower.values, color='gray', linewidth=0.8, linestyle='--')

        # 均线
        if show_ma:
            ma5 = calc_ma(df['Close'], 5)
            ma10 = calc_ma(df['Close'], 10)
            ma20 = calc_ma(df['Close'], 20)
            ax_candle.plot(ma5.index, ma5.values, label='MA5', linewidth=0.8)
            ax_candle.plot(ma10.index, ma10.values, label='MA10', linewidth=0.8)
            ax_candle.plot(ma20.index, ma20.values, label='MA20', linewidth=0.8)

        # 金叉/死叉标注
        if show_ma:
            crosses = detect_cross(ma5, ma20)
            for cross_type, date in crosses:
                price = df.loc[date, 'Close'] if date in df.index else None
                if price is not None:
                    color = 'green' if cross_type == 'gold' else 'red'
                    marker = '^' if cross_type == 'gold' else 'v'
                    ax_candle.scatter(date, price, color=color, marker=marker, s=100, zorder=5, label=f"{'金叉' if cross_type == 'gold' else '死叉'}")

        ax_candle.set_title(f"{symbol} K线走势", fontsize=12)
        ax_candle.legend(loc='upper left')
        ax_candle.grid(True, alpha=0.3)
        ax_candle.set_xlim(0, len(df)-1)

        # MACD
        if show_macd:
            ax_macd = axes[1]
            macd, signal, hist = calc_macid = calc_macd(df['Close'])
            colors = ['red' if h >= 0 else 'green' for h in hist]
            ax_macd.bar(hist.index, hist.values, color=colors, width=1.0, alpha=0.6)
            ax_macd.plot(macd.index, macd.values, color='blue', linewidth=1, label='MACD')
            ax_macd.plot(signal.index, signal.values, color='orange', linewidth=1, label='Signal')
            ax_macd.axhline(y=0, color='gray', linewidth=0.8)
            ax_macd.set_ylabel('MACD')
            ax_macd.legend(loc='upper left')
            ax_macd.grid(True, alpha=0.3)
            plt.setp(ax_macd.get_xticklabels(), visible=False)
        else:
            axes[1].axis('off')

        # KDJ
        if show_kdj:
            plot_kdj(df, axes[2])
        else:
            axes[2].axis('off')

        # RSI
        if show_rsi:
            rsi = calc_rsi(df['Close'])
            plot_rsi(rsi, axes[3])
        else:
            axes[3].axis('off')

        plt.tight_layout()
        st.pyplot(fig)

        st.success(f"数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")