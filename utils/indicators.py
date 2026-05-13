"""Technical indicators calculation utilities."""

import numpy as np
from typing import List, Optional
from config import RSI_PERIOD, SMA_PERIOD


def calculate_rsi(prices: List[float], period: int = RSI_PERIOD) -> Optional[float]:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        prices: List of closing prices
        period: RSI period (default: 14)
        
    Returns:
        RSI value or None if insufficient data
    """
    if len(prices) < period + 1:
        return None
    
    # Calculate price changes
    deltas = np.diff(prices)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gains and losses
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    # Calculate RS and RSI
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def calculate_sma(prices: List[float], period: int = SMA_PERIOD) -> Optional[float]:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        prices: List of closing prices
        period: SMA period (default: 20)
        
    Returns:
        SMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    sma = sum(prices[-period:]) / period
    return round(sma, 2)


def calculate_ema(prices: List[float], period: int = 20) -> Optional[float]:
    """
    Calculate Exponential Moving Average (EMA).
    
    Args:
        prices: List of closing prices
        period: EMA period
        
    Returns:
        EMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period  # Start with SMA
    
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return round(ema, 2)


def determine_trend(prices: List[float], sma: Optional[float]) -> str:
    """
    Determine the current trend based on price and SMA.
    
    Args:
        prices: List of closing prices
        sma: Simple Moving Average value
        
    Returns:
        Trend string: "Up", "Down", or "Sideways"
    """
    if sma is None or len(prices) < 2:
        return "Unknown"
    
    current_price = prices[-1]
    previous_price = prices[-2] if len(prices) > 1 else current_price
    
    # Check price position relative to SMA
    if current_price > sma * 1.01:  # 1% above SMA
        if current_price > previous_price:
            return "Up 📈"
        else:
            return "Sideways ➡️"
    elif current_price < sma * 0.99:  # 1% below SMA
        if current_price < previous_price:
            return "Down 📉"
        else:
            return "Sideways ➡️"
    else:
        return "Sideways ➡️"


def get_trading_signal(rsi: Optional[float], price: float, sma: Optional[float]) -> tuple:
    """
    Generate trading signal based on RSI and SMA.
    
    Args:
        rsi: RSI value
        price: Current price
        sma: Simple Moving Average value
        
    Returns:
        Tuple of (signal, confidence, reason)
        signal: "BUY", "SELL", or "WAIT"
        confidence: "HIGH", "MEDIUM", "LOW", or "NONE"
        reason: Explanation string
    """
    if rsi is None or sma is None:
        return "WAIT", "NONE", "Insufficient data"
    
    # BUY signal: RSI oversold AND price above SMA
    if rsi < 30 and price > sma:
        confidence = "HIGH" if rsi < 25 else "MEDIUM"
        return "BUY", confidence, f"RSI {rsi} (oversold) + Price above SMA"
    
    # SELL signal: RSI overbought AND price below SMA
    if rsi > 70 and price < sma:
        confidence = "HIGH" if rsi > 75 else "MEDIUM"
        return "SELL", confidence, f"RSI {rsi} (overbought) + Price below SMA"
    
    # Weak signals
    if rsi < 30:
        return "BUY", "LOW", f"RSI {rsi} (oversold) but price below SMA"
    
    if rsi > 70:
        return "SELL", "LOW", f"RSI {rsi} (overbought) but price above SMA"
    
    return "WAIT", "NONE", "No strong signal"
