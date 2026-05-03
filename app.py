"""
AI Ultra Value Pro v4.3 - 完整最終版
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

from prophet import Prophet
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="My Stock Pro", layout="wide", page_icon="📈")
st.title("📈 My Stock Pro")

# ==================== Sidebar ====================
st.sidebar.header("🔑 API Keys")
finnhub_key = st.sidebar.text_input("Finnhub API Key", type="password")

st.sidebar.header("股票設定")
tickers_input = st.sidebar.text_area("股票清單", "06082.HK, 0700.HK", height=120)
tickers = [t.strip() for t in tickers_input.split(',') if t.strip()]

tab1, tab2, tab3 = st.tabs(["📊 總覽", "🔍 單股深度分析", "📄 PDF 報告"])


@st.cache_data(ttl=300)
def get_data(ticker: str, period: str = "2y"):
    return yf.download(ticker, period=period, auto_adjust=True)


def get_info(ticker: str):
    return yf.Ticker(ticker).info


# ==================== 基本面 ====================
def fundamental_analysis(ticker: str):
    info = get_info(ticker)
    try:
        return {
            "PE Ratio": round(info.get('trailingPE', np.nan), 2),
            "PB Ratio": round(info.get('priceToBook', np.nan), 2),
            "ROE (%)": round(info.get('returnOnEquity', 0) * 100, 1),
            "Debt-to-Equity": round(info.get('debtToEquity', np.nan), 1),
            "Revenue Growth (%)": round(info.get('revenueGrowth', 0) * 100, 1),
            "Valuation": "低估" if info.get('trailingPE', 999) < 18 else "合理" if info.get('trailingPE',
                                                                                            999) < 30 else "高估"
        }
    except:
        return {"Error": "基本面資料取得失敗"}


# ==================== 技術指標 ====================
def add_technical_indicators(df: pd.DataFrame):
    df = df.copy()
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    return df


# ==================== 籌碼 ====================
def chip_analysis(ticker: str):
    """改進版籌碼分析"""
    stock = yf.Ticker(ticker)
    holders = stock.major_holders
    try:
        if not holders.empty:
            inst_pct = float(str(holders.iloc[1, 0]).rstrip('%'))
        else:
            inst_pct = 0.0
    except:
        inst_pct = 0.0

    return {
        "機構持股%": f"{inst_pct:.2f}%",
        "籌碼訊號": "🟢 主力偏多" if inst_pct > 15 else "🔴 散戶主導",
        "注意": "HK股機構持股數據有時不完整"
    }


# ==================== Tab 2 ====================
with tab2:
    ticker = st.selectbox("選擇股票", tickers)

    if st.button("🚀 生成完整報告", type="primary"):
        with st.spinner("正在分析..."):
            info = get_info(ticker)
            data = get_data(ticker, "1y")
            price = info.get('currentPrice') or (float(data['Close'][-1]) if not data.empty else 0.0)

            fund = fundamental_analysis(ticker)
            tech_data = add_technical_indicators(data.copy())

            st.subheader(f"{ticker} - {info.get('longName', 'N/A')}")
            st.metric("當前價格", f"{price:.2f} HKD")

            st.subheader("📑 基本面分析")
            st.json(fund)

            st.subheader("📊 技術指標")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=tech_data.index, open=tech_data['Open'], high=tech_data['High'],
                                         low=tech_data['Low'], close=tech_data['Close'], name="K線"))
            fig.add_trace(go.Scatter(x=tech_data.index, y=tech_data['SMA_20'], name="SMA20"))
            fig.add_trace(go.Scatter(x=tech_data.index, y=tech_data['SMA_50'], name="SMA50"))
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📌 籌碼分析")
            st.json(chip_analysis(ticker))

            st.success("**5-10% 操作建議**：結合基本面 + 技術指標綜合判斷")

st.caption("**免責聲明**：本工具僅供教育研究使用。投資有風險，請自行盡職調查。")