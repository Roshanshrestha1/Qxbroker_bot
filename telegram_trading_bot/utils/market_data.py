"""Market data fetching utilities."""

import asyncio
from typing import Dict, Optional, List, Any
import ccxt.async_support as ccxt_async
import yfinance as yf
from datetime import datetime
from utils.logger import logger
from config import BINANCE_RATE_LIMIT


async def fetch_crypto_data(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch cryptocurrency data from Binance.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        
    Returns:
        Dictionary with price data or None if failed
    """
    exchange = None
    try:
        exchange = ccxt_async.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        })
        
        # Fetch ticker
        ticker = await exchange.fetch_ticker(symbol)
        
        # Fetch OHLCV for indicators (1h timeframe, last 50 candles)
        ohlcv = await exchange.fetch_ohlcv(symbol, '1h', limit=50)
        closes = [candle[4] for candle in ohlcv]  # Close prices
        
        return {
            'symbol': symbol,
            'price': ticker['last'],
            'change_24h': ticker.get('percentage', 0),
            'volume': ticker.get('baseVolume', 0),
            'closes': closes,
            'timestamp': datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error fetching crypto data for {symbol}: {e}")
        return None
    finally:
        if exchange:
            await exchange.close()


def fetch_yfinance_data(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch forex/indices/commodities data from Yahoo Finance.
    
    Args:
        symbol: Yahoo Finance symbol (e.g., 'EURUSD=X', 'GC=F')
        
    Returns:
        Dictionary with price data or None if failed
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d', interval='1h')
        
        if hist.empty:
            logger.warning(f"No data found for {symbol}")
            return None
        
        closes = hist['Close'].tolist()
        current_price = closes[-1] if closes else None
        
        # Calculate 24h change
        if len(closes) >= 24:
            price_24h_ago = closes[-24]
            change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
        else:
            change_24h = 0
        
        # Get volume if available
        volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
        
        return {
            'symbol': symbol,
            'price': current_price,
            'change_24h': round(change_24h, 2),
            'volume': volume,
            'closes': closes,
            'timestamp': datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error fetching yfinance data for {symbol}: {e}")
        return None


async def get_market_data(symbol: str, asset_type: str = 'crypto') -> Optional[Dict[str, Any]]:
    """
    Get market data for any asset type.
    
    Args:
        symbol: Asset symbol
        asset_type: Type of asset ('crypto', 'forex', 'indices', 'commodities')
        
    Returns:
        Dictionary with price data or None if failed
    """
    if asset_type == 'crypto':
        return await fetch_crypto_data(symbol)
    else:
        # yfinance is synchronous, run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fetch_yfinance_data, symbol)


async def analyze_asset(symbol: str, asset_type: str = 'crypto') -> Optional[Dict[str, Any]]:
    """
    Fetch and analyze asset data.
    
    Args:
        symbol: Asset symbol
        asset_type: Type of asset
        
    Returns:
        Dictionary with analysis results or None if failed
    """
    from utils.indicators import calculate_rsi, calculate_sma, determine_trend, get_trading_signal
    
    data = await get_market_data(symbol, asset_type)
    
    if not data or not data.get('closes'):
        return None
    
    closes = data['closes']
    price = data['price']
    
    # Calculate indicators
    rsi = calculate_rsi(closes)
    sma = calculate_sma(closes)
    trend = determine_trend(closes, sma)
    signal, confidence, reason = get_trading_signal(rsi, price, sma)
    
    return {
        **data,
        'rsi': rsi,
        'sma': sma,
        'trend': trend,
        'signal': signal,
        'confidence': confidence,
        'reason': reason,
    }


async def scan_assets_for_best_trade(assets_by_category: Dict[str, List[str]]) -> Optional[Dict[str, Any]]:
    """
    Scan multiple assets to find the best trading opportunity.
    
    Args:
        assets_by_category: Dictionary of category -> list of symbols
        
    Returns:
        Best trade opportunity dictionary or None
    """
    best_trade = None
    best_score = -1
    
    # Priority order for signals
    signal_priority = {'BUY': 2, 'SELL': 1, 'WAIT': 0}
    confidence_scores = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'NONE': 0}
    
    tasks = []
    symbol_to_category = {}
    
    # Create tasks for all assets
    for category, symbols in assets_by_category.items():
        for symbol in symbols[:5]:  # Limit to top 5 per category for speed
            tasks.append(analyze_asset(symbol, category))
            symbol_to_category[symbol] = category
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception) or result is None:
                continue
            
            signal = result.get('signal', 'WAIT')
            confidence = result.get('confidence', 'NONE')
            
            # Calculate score
            score = (
                signal_priority.get(signal, 0) * 10 +
                confidence_scores.get(confidence, 0)
            )
            
            if score > best_score and signal in ['BUY', 'SELL']:
                best_score = score
                best_trade = {
                    **result,
                    'category': symbol_to_category.get(result['symbol'], 'unknown'),
                }
        
        return best_trade
        
    except Exception as e:
        logger.error(f"Error scanning assets: {e}")
        return None
