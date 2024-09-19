import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import yfinance as yf
import numpy as np
import ta

# Streamlit configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Load custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Graduate&display=swap');

    body {
        font-family: 'Graduate', sans-serif;
    }

    .stButton > button {
        background-color: red !important;
        color: white;
        border-radius: 10px;
        border: none;
        box-shadow: 0px 0px 15px red;
        transition: 0.3s;
    }

    .stButton > button:hover {
        box-shadow: 0px 0px 25px 10px red;
        transform: scale(1.05);
    }

    .title-block {
        background-color: red;
        color: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 2px 2px 20px red;
        text-align: center;
        transition: all 0.3s ease-in-out;
    }

    .title-block:hover {
        box-shadow: 0px 0px 30px 10px red;
        transform: scale(1.05);
    }

    /* Add Glowing Button Styling */

.glow-button {
    background-color: #4C1616;
    color: white;
    border: bold;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    font-family: 'Graduate', sans-serif;
    margin: 4px 2px;
    border-radius: 12px;
    box-shadow: 0 0 7px #ff3c3c, 0 0 17px #ff3c3c, 0 0 27px #ff3c3c;
    transition: all 0.3s ease-in-out;
}

    .glow-button:hover {
        box-shadow: 0 0 20px #ff4b4b, 0 0 30px #ff4b4b, 0 0 40px #ff4b4b;
        transform: scale(1.15);
    }

    /* Style for Company Name */
    .company-name {
        font-size: 35px;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        margin-bottom: 20px;
        font-family: 'Graduate', sans-serif;
        text-shadow: 2px 2px #ff4b4b;
    }

    /* Style for Company Name Box */
    .company-name-box {
        background-color: #000000
        padding: 15px;
        border-radius: 25px;
        box-shadow: 15px 15px 50px #f44336;
        text-align: center;
        font-size: 35px;
        font-weight: bold;
        text-shadow: 2px 2px #ff4b4b;
        transition: all 0.3s ease-in-out;
        margin-bottom: 20px;
        cursor: pointer;
    }

    .company-name-box:hover {
        box-shadow: 0px 0px 30px 10px #ff4b4b;
        transform: scale(1.05);
    }

    /* Ensure Global Font Family */
    body, .sidebar-content, h1, h2, h3, h4, h5, h6, .metric-title, .metric-value, .dataframe th, .dataframe td, .stButton > button, .title-block, .company-name-box, .glow-button {
        font-family: 'Graduate', sans-serif !important;
    }

    /* Remove or update any existing .company-name styles if present */
    .company-name {
        /* Optional: Remove styles or keep if needed differently */
        /* For consistency, you can remove this if not used elsewhere */
    }

    </style>
""", unsafe_allow_html=True)

# Sidebar content
st.sidebar.markdown("""
    <button class='glow-button'>Stocks Dashboard</button>
    <button class='glow-button'>Made by Engineer</button>
    """, unsafe_allow_html=True)

# Fetch stock codes (Using yfinance symbols and manually adding NIFTY and SENSEX stocks)
stock_codes = {
    # Nifty 50 Stocks
    'RELIANCE': 'Reliance Industries Ltd',
    'TCS': 'Tata Consultancy Services Ltd',
    'INFY': 'Infosys Ltd',
    'SBIN': 'State Bank of India',
    'ICICIBANK': 'ICICI Bank Ltd',
    'LT': 'Larsen & Toubro Ltd',
    'HDFCBANK': 'HDFC Bank Ltd',
    'KOTAKBANK': 'Kotak Mahindra Bank Ltd',
    'ITC': 'ITC Ltd',
    'HINDUNILVR': 'Hindustan Unilever Ltd',
    'HCLTECH': 'HCL Technologies Ltd',
    'AXISBANK': 'Axis Bank Ltd',
    'BAJFINANCE': 'Bajaj Finance Ltd',
    'BAJAJ-AUTO': 'Bajaj Auto Ltd',
    'ASIANPAINT': 'Asian Paints Ltd',
    'MARUTI': 'Maruti Suzuki India Ltd',
    'SUNPHARMA': 'Sun Pharmaceutical Industries Ltd',
    'ULTRACEMCO': 'UltraTech Cement Ltd',
    'NESTLEIND': 'Nestle India Ltd',
    'TITAN': 'Titan Company Ltd',
    'TECHM': 'Tech Mahindra Ltd',
    'WIPRO': 'Wipro Ltd',
    'POWERGRID': 'Power Grid Corporation of India Ltd',
    'NTPC': 'NTPC Ltd',
    'GAIL': 'GAIL (India) Ltd',
    'BHARTIARTL': 'Bharti Airtel Ltd',
    'SBILIFE': 'SBI Life Insurance Company Ltd',
    # Indices
    'NIFTY 50': '^NSEI',  # Nifty Index
    'SENSEX': '^BSESN',   # Sensex Index
}

# Create a DataFrame from the stock codes
qt = pd.DataFrame(stock_codes.items(), columns=['SYMBOL', 'NAME OF COMPANY'])

# Sidebar inputs
selectedstk = st.sidebar.selectbox('Select Stock', qt["SYMBOL"])

# Sidebar for time period and chart type
with st.sidebar:
    st.markdown("### Chart Parameters")
    
    # Time Period Selection
    time_interval = st.selectbox(
        "Select Time Interval",
        ["1m", "5m", "15m", "30m", "60m", "1d"],
        help="Choose the data interval."
    )
    
    if time_interval in ["1m", "5m", "15m", "30m", "60m"]:
        # For minute intervals, limit the date range to the past 7 days
        time_period = st.slider(
            "Select Time Period (Days)",
            min_value=1,
            max_value=30,
            value=1,
            help="Select the number of days for minute-level data."
        )
    else:
        # For daily intervals, allow up to 30 days
        time_period = st.slider(
            "Select Time Period (Days)",
            min_value=1,
            max_value=30,
            value=7,
            help="Select the number of days for daily data."
        )
    
    # Chart Type Selection
    chart_type = st.selectbox(
        "Select Chart Type",
        ["Candlestick", "Line", "OHLC", "Area", "Bar", "Heikin-Ashi", "Renko"],
        help="Choose the type of chart to display."
    )
    
    
    # Technical Indicators
    st.markdown("### Technical Indicators")
    show_ma = st.checkbox('Show Moving Averages')
    show_rsi = st.checkbox('Show RSI')
    show_macd = st.checkbox('Show MACD')
    show_bollinger = st.checkbox('Show Bollinger Bands')
    show_stochastic = st.checkbox('Show Stochastic Oscillator')
    show_adx = st.checkbox('Show ADX')
    show_ema = st.checkbox('Show Exponential Moving Average')
    ##show_bb = st.checkbox('Show Bollinger Bands')
    show_ichimoku = st.checkbox('Show Ichimoku Cloud')
    # Live Refresh Button
    if st.sidebar.button("Live Refresh"):
        # Fetch the latest data for the selected stock
        stock_symbol = selectedstk + '.NS' if selectedstk not in ['NIFTY 50', 'SENSEX'] else stock_codes[selectedstk]
        latest_data = yf.Ticker(stock_symbol).history(period="1d")
        
        # Update the displayed data
        st.rerun()
    
    # Calculate Metrics Button
    if st.sidebar.button("Calculate Metrics"):
        st.sidebar.write("Displaying essential metrics below:")
        
        # Fetch the latest data for the selected stock
        stock_symbol = selectedstk + '.NS' if selectedstk not in ['NIFTY 50', 'SENSEX'] else stock_codes[selectedstk]
        stock_data = yf.Ticker(stock_symbol).history(period="1mo")
        
        # Ensure there is enough data to compute indicators with window=14
        if len(stock_data) < 20:  # Increased minimum required data to support all indicators
            st.sidebar.error("Insufficient data to calculate technical indicators. Please select a longer time period.")
        else:
            # Initialize metrics dictionary
            metrics = {}
            
            # Calculate Return
            try:
                metrics['Return'] = ((stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[-7]) - 1) * 100 if len(stock_data) >= 7 else 'N/A'
            except:
                metrics['Return'] = 'N/A'
            
            # Calculate Volatility
            try:
                metrics['Volatility'] = stock_data['Close'].pct_change().std() * np.sqrt(252) * 100 if len(stock_data) > 1 else 'N/A'
            except:
                metrics['Volatility'] = 'N/A'
            
            # Calculate SMA50
            try:
                metrics['SMA50'] = stock_data['Close'].rolling(window=50).mean().iloc[-1] if len(stock_data) >= 50 else 'N/A'
            except:
                metrics['SMA50'] = 'N/A'
            
            # Calculate EMA20
            try:
                metrics['EMA20'] = stock_data['Close'].ewm(span=20, adjust=False).mean().iloc[-1] if len(stock_data) >= 20 else 'N/A'
            except:
                metrics['EMA20'] = 'N/A'
            
            # Calculate RSI
            try:
                metrics['RSI'] = ta.momentum.RSIIndicator(stock_data['Close'], window=14).rsi().iloc[-1] if len(stock_data) >= 14 else 'N/A'
            except:
                metrics['RSI'] = 'N/A'
            
            # Calculate ADX
            try:
                metrics['ADX'] = ta.trend.ADXIndicator(stock_data['High'], stock_data['Low'], stock_data['Close'], window=14).adx().iloc[-1] if len(stock_data) >= 14 else 'N/A'
            except:
                metrics['ADX'] = 'N/A'
            
            # Calculate MACD
            try:
                metrics['MACD'] = ta.trend.MACD(stock_data['Close']).macd().iloc[-1] if len(stock_data) >= 26 else 'N/A'
            except:
                metrics['MACD'] = 'N/A'
            
            # Calculate Bollinger Bands
            try:
                bollinger = ta.volatility.BollingerBands(stock_data['Close'], window=20)
                metrics['Bollinger_High'] = bollinger.bollinger_hband().iloc[-1] if len(stock_data) >= 20 else 'N/A'
                metrics['Bollinger_Low'] = bollinger.bollinger_lband().iloc[-1] if len(stock_data) >= 20 else 'N/A'
            except:
                metrics['Bollinger_High'] = 'N/A'
                metrics['Bollinger_Low'] = 'N/A'
            
            # Calculate Suggestion
            try:
                if (
                    len(stock_data) >= 50 and
                    len(stock_data) >= 20 and
                    stock_data['Close'].iloc[-1] > stock_data['Close'].rolling(window=50).mean().iloc[-1] and
                    stock_data['Close'].iloc[-1] > stock_data['Close'].ewm(span=20, adjust=False).mean().iloc[-1] and
                    stock_data['Close'].pct_change().tail(7).mean() > 0
                ):
                    metrics['Suggestion'] = "BUY"
                elif (
                    len(stock_data) >= 50 and
                    len(stock_data) >= 20 and
                    stock_data['Close'].iloc[-1] < stock_data['Close'].rolling(window=50).mean().iloc[-1] and
                    stock_data['Close'].iloc[-1] < stock_data['Close'].ewm(span=20, adjust=False).mean().iloc[-1] and
                    stock_data['Close'].pct_change().tail(7).mean() < 0
                ):
                    metrics['Suggestion'] = "NOT BUY"
                else:
                    metrics['Suggestion'] = "RISKY"
            except:
                metrics['Suggestion'] = "RISKY"
        
            # Display metrics in the sidebar with conditional formatting
            for metric, value in metrics.items():
                if isinstance(value, (int, float, np.float64)):
                    st.sidebar.metric(metric, f"{value:.2f}")
                else:
                    st.sidebar.metric(metric, value)
            
            # Plot dedicated graph in the dashboard
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price'))
            
            if len(stock_data) >= 50:
                fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'].rolling(window=50).mean(), mode='lines', name='50-day SMA'))
            if len(stock_data) >= 20:
                fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'].ewm(span=20, adjust=False).mean(), mode='lines', name='20-day EMA'))
            
            fig.update_layout(
                title=f'Stock Performance: {selectedstk}',
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_dark'
            )
            
            st.plotly_chart(fig)

# Fetch historical data for the selected stock
def fetch_historical_data(symbol, days):
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        stock_data = yf.download(symbol, start=start_date, end=end_date, interval="1d")
        return stock_data
    except Exception as e:
        st.error(f"Failed to fetch historical data: {e}")
        return pd.DataFrame()

# Plot candlestick chart with optional indicators
def plot_candlestick_chart(df, stock_name):
    fig = go.Figure()
    
    # Choose chart type
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick'
        ))
    elif chart_type == 'OHLC':
        fig.add_trace(go.Ohlc(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Line'
        ))

    # Add Moving Averages
    if show_ma:
        df['20_MA'] = df['Close'].rolling(window=20).mean()
        df['50_MA'] = df['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(x=df.index, y=df['20_MA'], mode='lines', name='20 Day MA'))
        fig.add_trace(go.Scatter(x=df.index, y=df['50_MA'], mode='lines', name='50 Day MA'))
    
    # Add RSI
    if show_rsi:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI'))

    # Add MACD
    if show_macd:
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD'))
        fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Signal Line'))

    # Chart layout
    fig.update_layout(
        title=f'{chart_type} Chart for {stock_name}',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark'
    )

    st.plotly_chart(fig)
    
# Fetch stock information using yfinance
def fetch_stock_info(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    return info

# Display additional stock metrics for technical analysis
def display_stock_metrics(info):
    st.markdown("""
        <button class='glow-button'>Fundamental Analysis</button>
        """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Market Cap", f"{info.get('marketCap', 'N/A'):,}")
    col2.metric("PE Ratio", info.get('trailingPE', 'N/A'))
    col3.metric("Dividend Yield", f"{info.get('dividendYield', 0) * 100:.2f}%")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("52 Week High", info.get('fiftyTwoWeekHigh', 'N/A'))
    col2.metric("52 Week Low", info.get('fiftyTwoWeekLow', 'N/A'))
    col3.metric("Volume", f"{info.get('volume', 0):,}")

# Display stock information and charts
try:
    stock_symbol = selectedstk + '.NS' if selectedstk not in ['NIFTY 50', 'SENSEX'] else stock_codes[selectedstk]
    stock_info = fetch_stock_info(stock_symbol)

    # Display company name inside a highlighted, glowing box
    compnm = stock_info.get('longName', selectedstk)
    st.markdown(f"""
        <div class='company-name-box'>{compnm}</div>
        """, unsafe_allow_html=True)

    # Display metrics
    currprice = stock_info.get('currentPrice', 0)
    stkchg = stock_info.get('regularMarketChangePercent', 0)
    dayHigh = stock_info.get('dayHigh', 0)
    dayLow = stock_info.get('dayLow', 0)

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", currprice, f"{stkchg:.2f}%")
    col2.metric("Day High", dayHigh)
    col3.metric("Day Low", dayLow)

    # Display additional metrics for technical and fundamental analysis
    try:
        display_stock_metrics(stock_info)
    except Exception as e:
        st.warning(f"Stock Details NA: {e}")

    # Fetch and plot historical data
    try:
        dfstk = fetch_historical_data(stock_symbol, days=time_period)
        if not dfstk.empty:
            plot_candlestick_chart(dfstk, compnm)
            st.markdown("""
                <button class='glow-button'>Summary</button>
                """, unsafe_allow_html=True)
            st.write(f"The **{chart_type}** chart for **{compnm}** displays the historical price movements over the selected period with the chosen technical indicators.")
        else:
            st.warning("No historical data available for this stock.")
    except Exception as e:
        st.error(f"Failed to fetch or plot historical data: {e}")

except Exception as e:
    st.error(f"Failed to fetch stock data: {str(e)}")
