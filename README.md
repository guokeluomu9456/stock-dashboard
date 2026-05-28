# Stock Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
[![CI](https://github.com/guokeluomu9456/stock-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/guokeluomu9456/stock-dashboard/actions)

股票技术分析 Dashboard | Python + Streamlit

输入股票代码，自动计算并可视化 MACD、KDJ、布林带、RSI 等常用技术指标，支持 A股、港股、美股。

## 功能

- 📊 **MACD** — 指数平滑异同移动平均线
- 📊 **KDJ** — 随机指标
- 📊 **RSI** — 相对强弱指数
- 📊 **布林带** — Bollinger Bands
- 📊 **均线系统** — MA5 / MA10 / MA20
- ✅ **金叉/死叉标注** — 自动标注均线交叉信号
- 🔍 **多市场支持** — A股（沪深）、港股、美股
- 💾 **数据缓存** — 本地缓存避免重复请求

## 项目结构

```
stock_dashboard/
├── src/
│   ├── __init__.py      # 包初始化
│   ├── config.py        # 配置常量
│   ├── data.py          # 数据获取、缓存
│   ├── indicators.py    # 技术指标计算（向量化）
│   ├── plot.py          # 绑图逻辑
│   └── ui.py            # Streamlit UI
├── tests/
│   ├── test_indicators.py
│   └── test_data.py
├── app.py               # 入口文件
├── requirements.txt
└── README.md
```

## 快速开始

```bash
# 克隆项目
git clone https://github.com/guokeluomu9456/stock-dashboard.git
cd stock-dashboard

# 安装依赖
pip install -r requirements.txt

# 启动
streamlit run app.py
```

然后在浏览器打开 `http://localhost:8501`

## 测试

```bash
# 运行单元测试
pytest tests/ -v
```

## 支持的股票市场

| 市场 | 代码示例 | 说明 |
|------|----------|------|
| A股 | `000001.SZ`, `600519.SH` | 深市/沪市 |
| 港股 | `0700.HK` | 腾讯等 |
| 美股 | `AAPL`, `TSLA` | 苹果、特斯拉 |

## 技术栈

- **数据源**: [yfinance](https://github.com/ranaroussi/yfinance)
- **可视化**: matplotlib
- **Web 框架**: [Streamlit](https://streamlit.io/)
- **语言**: Python 3.9+

## License

MIT