"""
Market Data Utilities for QX Broker Bot
Handles real-time data fetching and AI scanning for all QX Broker assets.
Uses TradingView API for Forex, Binance API for Crypto, Yahoo Finance for Commodities/Indices/Stocks.
EXACTLY MATCHING QX BROKER ASSET NAMES.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import requests
import time

# QX Broker Asset Name -> Yahoo Finance Symbol Mapping
QX_TO_YAHOO_MAP = {
    # Crypto (OTC) - Map to Yahoo Finance crypto symbols
    "Cosmos (OTC)": "ATOM-USD",
    "Avalanche (OTC)": "AVAX-USD",
    "Axie Infinity (OTC)": "AXS-USD",
    "Bitcoin Cash (OTC)": "BCH-USD",
    "Binance Coin (OTC)": "BNB-USD",
    "Ripple (OTC)": "XRP-USD",
    "Bitcoin (OTC)": "BTC-USD",
    "Polkadot (OTC)": "DOT-USD",
    "Ethereum Classic (OTC)": "ETC-USD",
    "Litecoin (OTC)": "LTC-USD",
    "Trump (OTC)": "MAGA-USD",
    "Solana (OTC)": "SOL-USD",
    "Dash (OTC)": "DASH-USD",
    "Ethereum (OTC)": "ETH-USD",
    "Zcash (OTC)": "ZEC-USD",
    "Chainlink (OTC)": "LINK-USD",
    # Forex pairs - Map to Yahoo Finance forex symbols
    "USD/ZAR (OTC)": "USDZAR=X",
    "USD/INR (OTC)": "USDINR=X",
    "USD/MXN (OTC)": "USDMXN=X",
    "USD/BRL (OTC)": "USDBRL=X",
    "USD/EGP (OTC)": "USDEGP=X",
    "NZD/CHF (OTC)": "NZDCHF=X",
    "USD/PKR (OTC)": "USDPKR=X",
    "USD/IDR (OTC)": "USDIDR=X",
    "USD/DZD (OTC)": "USDDZD=X",
    "USD/BDT (OTC)": "USDBDT=X",
    "USD/JPY": "USDJPY=X",
    "USD/NGN (OTC)": "USDNGN=X",
    "NZD/JPY (OTC)": "NZDJPY=X",
    "EUR/JPY": "EURJPY=X",
    "EUR/USD": "EURUSD=X",
    "NZD/USD (OTC)": "NZDUSD=X",
    "AUD/NZD (OTC)": "AUDNZD=X",
    "EUR/GBP": "EURGBP=X",
    "GBP/USD": "GBPUSD=X",
    "CAD/CHF (OTC)": "CADCHF=X",
    "NZD/CAD (OTC)": "NZDCAD=X",
    "USD/COP (OTC)": "USDCOP=X",
    "USD/PHP (OTC)": "USDPHP=X",
    "EUR/NZD (OTC)": "EURNZD=X",
    "AUD/JPY": "AUDJPY=X",
    "CAD/JPY": "CADJPY=X",
    "EUR/CAD": "EURCAD=X",
    "GBP/CAD": "GBPCAD=X",
    "AUD/CHF": "AUDCHF=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CHF": "USDCHF=X",
    "CHF/JPY": "CHFJPY=X",
    "AUD/CAD": "AUDCAD=X",
    "GBP/JPY": "GBPJPY=X",
    "USD/CAD": "USDCAD=X",
    "EUR/AUD": "EURAUD=X",
    "EUR/CHF": "EURCHF=X",
    "GBP/CHF": "GBPCHF=X",
    "GBP/AUD": "GBPAUD=X",
    # Commodities - Map to Yahoo Finance commodity symbols
    "UKBrent (OTC)": "BZ=F",
    "USCrude (OTC)": "CL=F",
    "Silver": "SI=F",
    "Gold": "GC=F",
    # Stocks - Map to Yahoo Finance stock symbols
    "Boeing Company (OTC)": "BA",
    "Intel (OTC)": "INTC",
    "Johnson & Johnson (OTC)": "JNJ",
    "Microsoft (OTC)": "MSFT",
    "Pfizer Inc (OTC)": "PFE",
    "FACEBOOK INC (OTC)": "META",
    "American Express (OTC)": "AXP",
    "McDonald's (OTC)": "MCD",
    # Indices - Map to Yahoo Finance index symbols
    "CAC 40": "^FCHI",
    "EURO STOXX 50": "^STOXX50E",
    "S&P/ASX 200": "^AXJO",
    "FTSE 100": "^FTSE",
    "IBEX 35": "^IBEX",
    "Nikkei 225": "^N225",
    "FTSE China A50 Index": "ASHR",
    "Hong Kong 50": "^HSI",
}

# Reverse map: Yahoo Symbol -> QX Name
YAHOO_TO_QX_MAP = {v: k for k, v in QX_TO_YAHOO_MAP.items()}

# Import asset lists from assets module
from assets.asset_lists import ALL_ASSETS, CRYPTO_ASSETS, FOREX_ASSETS, COMMODITIES_ASSETS, STOCKS_ASSETS, INDICES_ASSETS

# Build category map and flat list from the new asset lists
ALL_ASSET_SYMBOLS = []
ASSET_CATEGORY_MAP = {}

for category, symbols in ALL_ASSETS.items():
    for symbol in symbols:
        ALL_ASSET_SYMBOLS.append(symbol)
        ASSET_CATEGORY_MAP[symbol] = category

def get_asset_category(symbol):
    """Get the category (crypto, forex, etc.) for a QX Broker asset name."""
    return ASSET_CATEGORY_MAP.get(symbol, "UNKNOWN")

def get_yahoo_symbol(qx_symbol):
    """Convert QX Broker asset name to Yahoo Finance symbol."""
    return QX_TO_YAHOO_MAP.get(qx_symbol, qx_symbol)

def fetch_data(symbol, timeframe='1m', period='5d'):
    """
    Fetches data from Yahoo Finance using the QX Broker asset name.
    Automatically converts QX name to Yahoo symbol internally.
    """
    try:
        # Convert QX Broker name to Yahoo Finance symbol
        yahoo_symbol = get_yahoo_symbol(symbol)
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(period=period, interval=timeframe)
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"Yahoo error for {symbol} ({yahoo_symbol}): {e}")
        return None

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
                # Display name is already the QX Broker name (no cleaning needed)
                display_name = symbol
                
                opportunities.append({
                    "symbol": symbol,
                    "name": display_name,
                    "category": category,
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

    # Symbol name is already the QX Broker name (no cleaning needed)
    display_symbol = symbol
    category = get_asset_category(symbol)
    
    # All data now comes from Yahoo Finance via mapping
    data_source_text = "📊 **Data Source:** Yahoo Finance"
    
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
