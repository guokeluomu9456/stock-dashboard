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

# 启动面板
streamlit run app.py
```

启动后，**在浏览器打开 `http://localhost:8501`**，即可看到 Dashboard 界面。

## 使用方法

1. **打开浏览器** — 地址栏输入 `http://localhost:8501`
2. **输入股票代码** — 在左侧输入框填入股票代码（见下表）
3. **选择时间范围** — 默认近 6 个月，支持自定义
4. **查看指标** — 页面自动渲染 K线、MACD、KDJ、RSI、布林带
5. **金叉/死叉** — 均线交叉点自动标注（绿色↑金叉，红色↓死叉）

### 股票代码示例

| 市场 | 代码示例 | 说明 |
|------|----------|------|
| A股 | `000001.SZ`, `600519.SH` | 深市 / 沪市（茅台） |
| 港股 | `0700.HK` | 腾讯 |
| 美股 | `AAPL`, `TSLA`, `NVDA` | 苹果、特斯拉、英伟达 |

## 测试

```bash
pytest tests/ -v
```

## 技术栈

- **数据源**: [yfinance](https://github.com/ranaroussi/yfinance)
- **可视化**: matplotlib
- **Web 框架**: [Streamlit](https://streamlit.io/)
- **语言**: Python 3.9+

## License

MIT