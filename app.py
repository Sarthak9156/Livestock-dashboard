# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(page_title="📈 Stock Dashboard", layout="wide")
st.title("📊 Stock Market Dashboard")

#sidebar
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

#fetch data from y finance
@st.cache_data
def load_data(ticker, start, end):
    return yf.download(ticker, start=start, end=end)

if st.sidebar.button("Get Data"):
    with st.spinner("Fetching data..."):
        data = load_data(ticker, start_date, end_date)
        st.success("Data Loaded Successfully!")
# raw data
        st.subheader(f"Raw Data for {ticker}")
        st.dataframe(data.tail())

# moving averages
        data["MA20"] = data["Close"].rolling(window=20).mean()
        data["MA50"] = data["Close"].rolling(window=50).mean()

#RSI calculations

        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        data['RSI'] = 100 - (100 / (1 + rs))

# MAD calculations
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

########### Data visualization ####### 
# price chart by plotly
        st.subheader("Price Chart with Moving Averages")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close"))
        fig1.add_trace(go.Scatter(x=data.index, y=data["MA20"], name="MA20"))
        fig1.add_trace(go.Scatter(x=data.index, y=data["MA50"], name="MA50"))
        fig1.update_layout(title="Stock Price", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig1, use_container_width=True)

#RSI chart 
        st.subheader("RSI (Relative Strength Index)")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=data.index, y=data["RSI"], name="RSI"))
        fig2.update_layout(yaxis=dict(range=[0, 100]), shapes=[
            dict(type="line", x0=data.index[0], x1=data.index[-1], y0=70, y1=70, line=dict(color="red", dash="dash")),
            dict(type="line", x0=data.index[0], x1=data.index[-1], y0=30, y1=30, line=dict(color="green", dash="dash")),
        ])
        st.plotly_chart(fig2, use_container_width=True)

#MACD chart
        st.subheader("MACD")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=data.index, y=data["MACD"], name="MACD"))
        fig3.add_trace(go.Scatter(x=data.index, y=data["Signal"], name="Signal"))
        st.plotly_chart(fig3, use_container_width=True)
