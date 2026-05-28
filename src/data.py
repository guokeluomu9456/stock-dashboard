"""
数据获取与缓存模块
"""

import hashlib
import pickle
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

from .config import CACHE_DIR


def _ensure_cache_dir() -> Path:
    """确保缓存目录存在"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def _cache_key(symbol: str, period: str) -> str:
    """生成缓存键"""
    key_str = f"{symbol}_{period}"
    return hashlib.md5(key_str.encode()).hexdigest()


def read_cache(symbol: str, period: str) -> Optional[pd.DataFrame]:
    """
    读取缓存数据

    Args:
        symbol: 股票代码
        period: 时间周期

    Returns:
        缓存的 DataFrame 或 None
    """
    key = _cache_key(symbol, period)
    path = CACHE_DIR / f"{key}.pkl"
    if not path.exists():
        return None

    try:
        with open(path, "rb") as f:
            return pickle.load(f)  # noqa: S301
    except Exception:
        return None


def write_cache(symbol: str, period: str, df: pd.DataFrame) -> None:
    """
    写入缓存数据

    Args:
        symbol: 股票代码
        period: 时间周期
        df: 数据帧
    """
    key = _cache_key(symbol, period)
    path = CACHE_DIR / f"{key}.pkl"

    try:
        _ensure_cache_dir()
        with open(path, "wb") as f:
            pickle.dump(df, f)
    except PermissionError:
        raise
    except Exception:
        pass


def get_ticker_symbol(raw: str, market: str) -> str:
    """
    根据市场类型转换股票代码

    Args:
        raw: 原始股票代码
        market: 市场类型 ('A股', '港股', '美股')

    Returns:
        转换后的完整股票代码

    Raises:
        ValueError: 股票代码格式无效
    """
    raw = raw.strip().upper()

    if not raw:
        raise ValueError("股票代码不能为空")

    if market == "美股":
        return raw

    if market == "港股":
        if raw.endswith(".HK"):
            return raw
        return f"{raw}.HK"

    # A股
    if raw.endswith(".SZ") or raw.endswith(".SH"):
        return raw

    if len(raw) != 6 or not raw.isdigit():
        raise ValueError(f"A股代码必须是 6 位数字，当前: {raw}")

    if raw.startswith("6"):
        return f"{raw}.SS"

    return f"{raw}.SZ"


def fetch_stock_data(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """
    获取股票数据（带缓存）

    Args:
        symbol: 股票代码
        period: 时间周期 (如 '1y', '6mo', '2y', '5y')

    Returns:
        股票数据 DataFrame 或 None

    Raises:
        ValueError: 股票代码无效
        ConnectionError: 网络连接失败
    """
    # 尝试从缓存读取
    cached = read_cache(symbol, period)
    if cached is not None:
        return cached

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            return None

        write_cache(symbol, period, df)
        return df

    except ValueError as e:
        raise ValueError(f"无效的股票代码: {symbol}") from e
    except ConnectionError as e:
        raise ConnectionError(f"网络连接失败，无法获取 {symbol} 的数据") from e
    except Exception as e:
        raise RuntimeError(f"获取股票数据时发生未知错误: {e}") from e