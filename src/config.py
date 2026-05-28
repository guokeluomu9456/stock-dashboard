"""
配置常量模块
"""

from pathlib import Path

# 缓存目录
CACHE_DIR = Path.home() / ".stock_dashboard_cache"

# 市场配置
MARKET_CONFIG: dict[str, dict[str, list[str] | str]] = {
    "A股": {"suffix": "", "prefixes": ["SZ", "SH"]},
    "港股": {"suffix": ".HK", "prefixes": []},
    "美股": {"suffix": "", "prefixes": []},
}

# KDJ 默认参数
KDJ_N = 9
KDJ_M1 = 3
KDJ_M2 = 3

# MACD 默认参数
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# RSI 默认参数
RSI_WINDOW = 14

# 布林带默认参数
BB_WINDOW = 20
BB_NUM_STD = 2.0

# MA 默认参数
MA_WINDOWS = [5, 10, 20]

# 指标名称映射（用于显示）
INDICATOR_NAMES: dict[str, str] = {
    "ma": "均线",
    "macd": "MACD",
    "kdj": "KDJ",
    "rsi": "RSI",
    "bollinger": "布林带",
}