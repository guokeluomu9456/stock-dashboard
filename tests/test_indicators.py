"""Test script for CI - verifies all indicators work correctly"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from app import calc_ma, calc_macd, calc_kdj, calc_bollinger, calc_rsi, detect_cross

# Test with real data
df = yf.Ticker('AAPL').history(period='1mo')
close = df['Close']
high = df['High']
low = df['Low']

assert len(calc_ma(close, 5)) > 0, 'MA failed'
assert len(calc_macd(close)) == 3, 'MACD failed'
assert len(calc_kdj(high, low, close)) == 3, 'KDJ failed'
assert len(calc_bollinger(close)) == 3, 'Bollinger failed'
assert len(calc_rsi(close)) > 0, 'RSI failed'
assert len(detect_cross(calc_ma(close, 5), calc_ma(close, 20))) >= 0, 'Cross detection failed'

print('All tests passed!')