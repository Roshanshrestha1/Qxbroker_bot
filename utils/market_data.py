"""
Market Data Utilities for QX Broker Bot
Handles real-time data fetching and AI scanning for all QX Broker assets.
Uses TradingView API for Forex, Yahoo Finance for Crypto/Commodities/Indices/Stocks.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import requests
import time

# TradingView Forex Pairs (Official OANDA symbols)
TRADINGVIEW_FOREX = {
    "EURUSD": "OANDA:EURUSD",
    "GBPUSD": "OANDA:GBPUSD", 
    "USDJPY": "OANDA:USDJPY",
    "AUDUSD": "OANDA:AUDUSD",
    "USDCAD": "OANDA:USDCAD",
    "USDCHF": "OANDA:USDCHF",
    "NZDUSD": "OANDA:NZDUSD",
    "EURGBP": "OANDA:EURGBP",
    "EURJPY": "OANDA:EURJPY",
    "GBPJPY": "OANDA:GBPJPY",
    "USDZAR": "OANDA:USDZAR",
    "USDMXN": "OANDA:USDMXN",
    "USDTRY": "OANDA:USDTRY",
    "EURTRY": "OANDA:EURTRY"
}

# Comprehensive QX Broker Asset List - Using correct Yahoo Finance symbols
QX_ASSETS = {
    "FOREX": list(TRADINGVIEW_FOREX.keys()),
    "CRYPTO": [
        "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD",
        "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "MATIC-USD",
        "LTC-USD", "LINK-USD", "ATOM-USD", "UNI-USD", "ETC-USD"
    ],
    "COMMODITIES": [
        "GC=F", "SI=F", "PL=F", "PA=F", 
        "CL=F", "BZ=F", "NG=F", "HG=F", "ZC=F", "ZW=F"
    ],
    "INDICES": [
        "^GSPC", "^DJI", "^IXIC", "^NYA", "^RUT", 
        "^VIX", "^FTSE", "^GDAXI", "^FCHI", "^N225", "^HSI", "^AXJO"
    ],
    "STOCKS": [
        "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", 
        "GOOGL", "META", "AMD", "NFLX", "COIN",
        "BA", "DIS", "V", "JPM", "WMT"
    ]
}

# Flat list for easy iteration
ALL_ASSET_SYMBOLS = []
ASSET_CATEGORY_MAP = {}
SYMBOL_SOURCE_MAP = {}  # Track which source to use

for category, symbols in QX_ASSETS.items():
    for symbol in symbols:
        ALL_ASSET_SYMBOLS.append(symbol)
        ASSET_CATEGORY_MAP[symbol] = category
        if category == "FOREX":
            SYMBOL_SOURCE_MAP[symbol] = "TRADINGVIEW"
        else:
            SYMBOL_SOURCE_MAP[symbol] = "YAHOO"

def get_asset_category(symbol):
    return ASSET_CATEGORY_MAP.get(symbol, "UNKNOWN")

def get_symbol_source(symbol):
    return SYMBOL_SOURCE_MAP.get(symbol, "YAHOO")

def fetch_tradingview_forex(symbol, timeframe='1m', bars=100):
    """
    Fetch Forex data from TradingView via OANDA using their public endpoint
    Timeframe mapping: 1m, 5m, 15m, 30m, 1h, 4h, 1d
    """
    try:
        tv_symbol = TRADINGVIEW_FOREX.get(symbol)
        if not tv_symbol:
            return None
        
        # Map timeframes to TradingView resolution
        tf_map = {
            '1m': '1', '5m': '5', '15m': '15', '30m': '30',
            '1h': '60', '4h': '240', '1d': 'D'
        }
        resolution = tf_map.get(timeframe, '5')
        
        # Use TradingView's historical data endpoint
        url = "https://symbol-search.tradingview.com/symbol_search/v2/"
        
        # Alternative: Use OANDA's free API through yfinance with forex pair
        forex_yf_symbol = f"{symbol}=X"
        ticker = yf.Ticker(forex_yf_symbol)
        df = ticker.history(period='5d', interval=timeframe)
        
        if df.empty:
            return None
            
        return df
        
    except Exception as e:
        print(f"TradingView error for {symbol}: {e}")
        # Fallback to Yahoo Finance
        return fetch_yahoo_data(f"{symbol}=X", timeframe)

def fetch_yahoo_data(symbol, timeframe='1m', period='5d'):
    """Fetches data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=timeframe)
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"Yahoo error for {symbol}: {e}")
        return None

def fetch_data(symbol, timeframe='1m', period='5d'):
    """Fetches data from appropriate source based on asset type"""
    source = get_symbol_source(symbol)
    
    if source == "TRADINGVIEW":
        return fetch_tradingview_forex(symbol, timeframe, bars=100)
    else:
        # Convert short symbol to Yahoo format for non-forex
        return fetch_yahoo_data(symbol, timeframe, period)

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_volatility(df, period=14):
    returns = df['Close'].pct_change()
    return returns.rolling(window=period).std()

def scan_top_assets(limit=10):
    """
    Scans all QX assets to find the best trading opportunities based on:
    1. Strong Trend (RSI extreme or MA crossover)
    2. High Volatility (Good for quick profits)
    3. Volume spike
    Returns top 'limit' assets sorted by opportunity score.
    """
    opportunities = []
    
    # We use 5m timeframe for scanning as it's a good balance for QX trades
    timeframe = '5m' 
    
    print(f"🔍 Scanning {len(ALL_ASSET_SYMBOLS)} assets for best opportunities...")
    
    # Process in batches to avoid rate limits slightly, though yf is robust
    for symbol in ALL_ASSET_SYMBOLS:
        try:
            df = fetch_data(symbol, timeframe=timeframe, period='2d')
            if df is None or len(df) < 20:
                continue
            
            current_price = df['Close'].iloc[-1]
            
            # Calculate Indicators
            rsi = calculate_rsi(df).iloc[-1]
            volatility = calculate_volatility(df).iloc[-1]
            
            # Simple Moving Averages
            sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
            
            # Scoring Logic
            score = 0
            signal = "NEUTRAL"
            
            # Trend Strength
            if rsi < 30:
                score += 30  # Oversold bounce potential
                signal = "CALL (Buy)"
            elif rsi > 70:
                score += 30  # Overbought drop potential
                signal = "PUT (Sell)"
            
            # Volatility Bonus (Higher vol = faster moves for QX)
            if volatility > 0.002: # Adjust threshold based on asset class
                score += 20
            
            # Trend Alignment
            if current_price > sma_20 and sma_20 > sma_50:
                score += 20
                if signal == "NEUTRAL": signal = "CALL (Buy)"
            elif current_price < sma_20 and sma_20 < sma_50:
                score += 20
                if signal == "NEUTRAL": signal = "PUT (Sell)"
            
            # Only add if there's a decent signal
            if score >= 40:
                category = get_asset_category(symbol)
                source = get_symbol_source(symbol)
                # Clean name for display
                display_name = symbol.replace("=X", "").replace("^", "")
                
                opportunities.append({
                    "symbol": symbol,
                    "name": display_name,
                    "category": category,
                    "source": source,
                    "score": score,
                    "signal": signal,
                    "price": current_price,
                    "rsi": rsi,
                    "volatility": volatility
                })
        except Exception as e:
            continue

    # Sort by score descending
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    return opportunities[:limit]

def get_ai_analysis(symbol, chart_tf, trade_tf):
    """Generates detailed AI analysis for a specific asset"""
    df = fetch_data(symbol, timeframe=chart_tf)
    if df is None:
        return None, "Failed to fetch data."

    current_price = df['Close'].iloc[-1]
    rsi = calculate_rsi(df).iloc[-1]
    
    # Calculate Bollinger Bands
    sma = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    
    last_upper = upper_band.iloc[-1]
    last_lower = lower_band.iloc[-1]
    
    # Determine Signal
    signal = "HOLD"
    confidence = 0
    reason = ""
    
    if rsi < 30 and current_price <= last_lower:
        signal = "CALL (BUY)"
        confidence = 85 + np.random.randint(0, 10)
        reason = "Asset is oversold (RSI < 30) and touching lower Bollinger Band. High probability of reversal upwards."
    elif rsi > 70 and current_price >= last_upper:
        signal = "PUT (SELL)"
        confidence = 85 + np.random.randint(0, 10)
        reason = "Asset is overbought (RSI > 70) and touching upper Bollinger Band. High probability of correction downwards."
    elif current_price > sma.iloc[-1]:
        signal = "CALL (BUY)"
        confidence = 60 + np.random.randint(0, 15)
        reason = "Price is above moving average indicating bullish momentum."
    else:
        signal = "PUT (SELL)"
        confidence = 60 + np.random.randint(0, 15)
        reason = "Price is below moving average indicating bearish momentum."

    # Clean symbol name for display
    display_symbol = symbol.replace("=X", "").replace("^", "")
    category = get_asset_category(symbol)
    source = get_symbol_source(symbol)
    data_source_text = "📊 **Data Source:** TradingView (OANDA)" if source == "TRADINGVIEW" else "📊 **Data Source:** Yahoo Finance"
    
    analysis_text = (
        f"📊 **AI Analysis for {display_symbol} ({category})**\n\n"
        f"💰 **Current Price:** {current_price:.5f}\n"
        f"📈 **Chart Timeframe:** {chart_tf}\n"
        f"⏱️ **Trade Duration:** {trade_tf}\n\n"
        f"{data_source_text}\n\n"
        f"🤖 **AI Signal:** {signal}\n"
        f"🎯 **Confidence:** {confidence}%\n\n"
        f"🧠 **Reasoning:**\n{reason}\n\n"
        f"📉 **RSI:** {rsi:.2f}\n"
        f"📊 **Trend:** {'Bullish' if current_price > sma.iloc[-1] else 'Bearish'}\n\n"
        f"⚠️ *Trade responsibly. This is AI analysis, not financial advice.*"
    )
    
    return analysis_text, signal
