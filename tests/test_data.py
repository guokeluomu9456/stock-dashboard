"""
data 模块单元测试
"""

import pytest
from pathlib import Path
import pandas as pd
import numpy as np


class TestGetTickerSymbol:
    """测试股票代码转换"""

    def test_美股直接返回(self):
        """美股代码直接返回"""
        from src.data import get_ticker_symbol

        assert get_ticker_symbol("AAPL", "美股") == "AAPL"
        assert get_ticker_symbol("TSLA", "美股") == "TSLA"

    def test_港股添加后缀(self):
        """港股代码添加 .HK 后缀"""
        from src.data import get_ticker_symbol

        assert get_ticker_symbol("0700", "港股") == "0700.HK"
        assert get_ticker_symbol("9988", "港股") == "9988.HK"
        assert get_ticker_symbol("0700.HK", "港股") == "0700.HK"  # 已有后缀不重复添加

    def test_A股判断深沪(self):
        """A股判断深沪市场"""
        from src.data import get_ticker_symbol

        # 6开头是上海
        assert get_ticker_symbol("600000", "A股") == "600000.SS"
        assert get_ticker_symbol("600036", "A股") == "600036.SS"

        # 非6开头是深圳
        assert get_ticker_symbol("000001", "A股") == "000001.SZ"
        assert get_ticker_symbol("000858", "A股") == "000858.SZ"

        # 已有后缀不重复添加
        assert get_ticker_symbol("000001.SZ", "A股") == "000001.SZ"
        assert get_ticker_symbol("600000.SH", "A股") == "600000.SH"

    def test_大小写处理(self):
        """测试大小写处理"""
        from src.data import get_ticker_symbol

        assert get_ticker_symbol("aapl", "美股") == "AAPL"
        assert get_ticker_symbol("  0700  ", "港股") == "0700.HK"


class TestCacheKey:
    """测试缓存键生成"""

    def test_cache_key_consistency(self):
        """相同输入产生相同缓存键"""
        from src.data import read_cache, write_cache, _cache_key

        key1 = _cache_key("AAPL", "1y")
        key2 = _cache_key("AAPL", "1y")

        assert key1 == key2

    def test_cache_key_different_params(self):
        """不同参数产生不同缓存键"""
        from src.data import _cache_key

        key1 = _cache_key("AAPL", "1y")
        key2 = _cache_key("AAPL", "6mo")
        key3 = _cache_key("TSLA", "1y")

        assert key1 != key2
        assert key1 != key3


class TestReadWriteCache:
    """测试缓存读写"""

    def test_cache_roundtrip(self, tmp_path):
        """测试缓存写入和读取"""
        import sys
        from src.data import CACHE_DIR

        # 使用临时目录进行测试
        test_cache_dir = tmp_path / "cache"
        original_cache_dir = CACHE_DIR

        # 临时修改缓存目录
        import src.data
        src.data.CACHE_DIR = test_cache_dir

        try:
            from src.data import write_cache, read_cache

            # 创建测试数据
            test_df = pd.DataFrame(
                {"Open": [1, 2, 3], "Close": [1.1, 2.2, 3.3]},
                index=pd.date_range("2023-01-01", periods=3),
            )

            # 写入缓存
            write_cache("TEST", "1y", test_df)

            # 读取缓存
            cached = read_cache("TEST", "1y")

            assert cached is not None
            assert len(cached) == 3
            assert cached["Close"].iloc[-1] == 3.3
        finally:
            # 恢复原始缓存目录
            src.data.CACHE_DIR = original_cache_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

class TestInputValidation:
    """测试股票代码输入验证"""

    def test_empty_code_raises(self):
        """空代码应该报错"""
        from src.data import get_ticker_symbol

        with pytest.raises(ValueError, match="不能为空"):
            get_ticker_symbol("", "A股")

        with pytest.raises(ValueError, match="不能为空"):
            get_ticker_symbol("   ", "港股")

    def test_a_stock_wrong_length(self):
        """A股代码必须是6位"""
        from src.data import get_ticker_symbol

        with pytest.raises(ValueError, match="6 位数字"):
            get_ticker_symbol("12345", "A股")

        with pytest.raises(ValueError, match="6 位数字"):
            get_ticker_symbol("1234567", "A股")

    def test_a_stock_nondigit(self):
        """A股代码必须全是数字"""
        from src.data import get_ticker_symbol

        with pytest.raises(ValueError, match="6 位数字"):
            get_ticker_symbol("600ABC", "A股")
