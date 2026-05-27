# Stock Dashboard

🛠️ 股票技术分析 Dashboard | Python + Streamlit

输入股票代码，自动计算并可视化 MACD、KDJ、布林带等常用技术指标。

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 功能

- 🔍 股票数据查询（Yahoo Finance）
- 📊 MACD 指标
- 📊 KDJ 指标
- 📊 布林带指标
- 💾 数据缓存，无重复请求

## 快速开始

```bash
pip install -r requirements.txt
streamlit run app.py
```

然后在浏览器打开 `http://localhost:8501`

## 截图

![Dashboard Screenshot](screenshot.png)

## 支持的股票市场

- A股（沪深）: `000001.SZ`, `600519.SH`
- 港股: `0700.HK`
- 美股: `AAPL`, `TSLA`

## License

MIT