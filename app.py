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

# ==================== 介面優化設定 ====================
st.set_page_config(
    page_title="My Stock Pro",
    page_icon="📈",
    layout="centered",           # 手機友好
    initial_sidebar_state="expanded"
)

# 自訂顏色主題
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .css-1d391kg {background-color: #262730;}
</style>
""", unsafe_allow_html=True)

st.title("📈 My Stock Pro")
st.caption("你的專屬投資分析平台 | 基本面 + 技術 + 預測")

# ==================== Sidebar ====================
with st.sidebar:
    st.header("⚙️ 設定")
    finnhub_key = st.text_input("Finnhub API Key", type="password")
    tickers_input = st.text_area("股票清單", "06082.HK, 0700.HK", height=120)
    tickers = [t.strip() for t in tickers_input.split(',') if t.strip()]

# ==================== 主介面 ====================
tab1, tab2, tab3 = st.tabs(["🏠 總覽", "🔍 單股深度", "📊 風險回測"])

with tab2:
    ticker = st.selectbox("選擇股票", tickers)

    if st.button("🚀 開始分析", type="primary", use_container_width=True):
        with st.spinner("正在為你分析最新數據..."):
            info = yf.Ticker(ticker).info
            data = yf.download(ticker, period="1y")
            price = info.get('currentPrice') or float(data['Close'][-1])

            st.success(f"**{ticker}** 分析完成 - {datetime.now().strftime('%H:%M')}")

            st.metric("最新價格", f"{price:.2f} HKD", delta="計算中...")

            # 使用 expander 讓手機更好滑動
            with st.expander("📑 基本面分析", expanded=True):
                # 你的 fundamental_analysis 函數
                pass

            with st.expander("📊 技術指標", expanded=True):
                # 你的技術指標圖表
                pass

            with st.expander("🔮 價格預測", expanded=True):
                # Prophet 預測
                pass

st.caption("**手機友好優化版** | 投資有風險，請自行判斷")