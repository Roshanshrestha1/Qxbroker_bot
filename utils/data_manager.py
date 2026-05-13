"""
Unified Data Manager with Fallback Logic
Handles data fetching from primary (QX Broker) and secondary (yfinance/Binance) sources.
Automatically falls back to secondary source when primary fails.
"""
import threading
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

import pandas as pd

from utils.logger import logger
from utils.qx_client import QXBrokerClient, PrimarySourceError, get_qx_client
from utils.market_data import (
    fetch_data as fetch_yahoo_data,
    get_asset_category,
    get_yahoo_symbol,
    calculate_rsi,
    get_ai_analysis as get_yahoo_ai_analysis,
)
from config import PRIMARY_DATA_SOURCE


class DataUnavailableError(Exception):
    """Raised when both primary and secondary data sources fail."""
    pass


class DataManager:
    """
    Unified data manager with automatic fallback from QX Broker to yfinance/Binance.
    
    Features:
    - Tries primary source (QX Broker) first
    - Automatically falls back to secondary (yfinance/Binance) on failure
    - Periodically attempts to reconnect to primary source
    - Tracks fallback state and notifies when status changes
    """
    
    def __init__(self):
        self.primary_available = False
        self.primary_failed_once = False  # Track if we've ever failed (for notifications)
        self._reconnect_thread: Optional[threading.Thread] = None
        self._stop_reconnect = False
        
        # Initialize primary client
        self.qx_client = get_qx_client()
        
        # Try initial connection to primary source
        self._try_primary_connection()
        
        # Start background reconnection thread
        self._start_reconnect_thread()
    
    def _try_primary_connection(self) -> bool:
        """
        Attempt to connect to primary source.
        Returns True if successful, False otherwise.
        """
        if PRIMARY_DATA_SOURCE != "qxbroker":
            logger.info("Primary data source disabled (set to 'yfinance')")
            self.primary_available = False
            return False
        
        try:
            success = self.qx_client.test_connection()
            if success:
                self.primary_available = True
                logger.info("✅ Primary data source (QX Broker) connected successfully")
            else:
                self.primary_available = False
                logger.warning("⚠️ Primary data source (QX Broker) connection failed")
            return success
        except Exception as e:
            self.primary_available = False
            logger.warning(f"⚠️ Primary data source error: {e}")
            return False
    
    def _start_reconnect_thread(self) -> None:
        """Start background thread for periodic reconnection attempts."""
        self._stop_reconnect = False
        self._reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self._reconnect_thread.start()
        logger.debug("Reconnection thread started")
    
    def _reconnect_loop(self) -> None:
        """Background loop that tries to reconnect to primary every 5 minutes."""
        while not self._stop_reconnect:
            time.sleep(300)  # Wait 5 minutes
            
            if not self.primary_available:
                logger.info("Attempting to reconnect to primary source...")
                was_available = False
                try:
                    success = self._try_primary_connection()
                    if success and not was_available:
                        logger.info("✅ Primary data source recovered!")
                        self.primary_failed_once = False  # Reset notification flag
                except Exception as e:
                    logger.debug(f"Reconnection attempt failed: {e}")
    
    def stop(self) -> None:
        """Stop the reconnection thread."""
        self._stop_reconnect = True
        if self._reconnect_thread:
            self._reconnect_thread.join(timeout=2)
            logger.debug("Reconnection thread stopped")
    
    def get_price(self, asset_type: str, symbol: str) -> float:
        """
        Get current price for an asset.
        
        Args:
            asset_type: Asset category ('crypto', 'forex', 'commodities', etc.)
            symbol: Asset name (QX Broker format)
            
        Returns:
            Current price
            
        Raises:
            DataUnavailableError: If both sources fail
        """
        # Try primary source first
        if self.primary_available:
            try:
                price = self.qx_client.get_price(symbol)
                return price
            except PrimarySourceError as e:
                logger.warning(f"Primary source failed for {symbol}: {e}")
                self.primary_available = False
                self.primary_failed_once = True
                # Fall through to secondary
        
        # Try secondary source (yfinance/Binance via market_data)
        try:
            yahoo_symbol = get_yahoo_symbol(symbol)
            df = fetch_yahoo_data(symbol, timeframe='1m', period='1d')
            if df is not None and not df.empty:
                price = df['Close'].iloc[-1]
                logger.debug(f"Secondary source fetched price for {symbol}: {price}")
                return price
            else:
                raise DataUnavailableError(f"No data available for {symbol}")
        except Exception as e:
            logger.error(f"Secondary source also failed for {symbol}: {e}")
            raise DataUnavailableError(f"Both sources failed for {symbol}: {e}")
    
    def get_candles(self, asset_type: str, symbol: str, timeframe: str = '5m', 
                    period: str = '2d') -> Optional[pd.DataFrame]:
        """
        Get candlestick data for an asset.
        
        Args:
            asset_type: Asset category
            symbol: Asset name (QX Broker format)
            timeframe: Chart timeframe (e.g., '5m', '1h')
            period: Data period (e.g., '2d', '5d')
            
        Returns:
            DataFrame with OHLCV data or None if unavailable
            
        Raises:
            DataUnavailableError: If both sources fail
        """
        # Note: QX Broker typically doesn't provide historical candles via unofficial API
        # So we primarily rely on secondary source for this
        if self.primary_available:
            try:
                df = self.qx_client.get_candles(symbol, period=timeframe, count=100)
                if df is not None and not df.empty:
                    logger.debug(f"Primary source fetched candles for {symbol}")
                    return df
            except PrimarySourceError as e:
                logger.debug(f"Primary source candles not available for {symbol}: {e}")
                # Don't mark primary as failed for candle requests - it's expected
        
        # Use secondary source (yfinance)
        try:
            df = fetch_yahoo_data(symbol, timeframe=timeframe, period=period)
            if df is not None and not df.empty:
                logger.debug(f"Secondary source fetched candles for {symbol}")
                return df
            else:
                raise DataUnavailableError(f"No candle data for {symbol}")
        except Exception as e:
            logger.error(f"Failed to fetch candles for {symbol}: {e}")
            raise DataUnavailableError(f"Candle data unavailable for {symbol}")
    
    def get_technical(self, asset_type: str, symbol: str, 
                      timeframe: str = '5m') -> Dict[str, Any]:
        """
        Get technical analysis data for an asset.
        
        Args:
            asset_type: Asset category
            symbol: Asset name (QX Broker format)
            timeframe: Chart timeframe
            
        Returns:
            Dict with RSI, SMA, trend, etc.
            
        Raises:
            DataUnavailableError: If data cannot be fetched
        """
        df = self.get_candles(asset_type, symbol, timeframe=timeframe)
        
        if df is None or len(df) < 20:
            raise DataUnavailableError(f"Insufficient data for {symbol}")
        
        current_price = df['Close'].iloc[-1]
        rsi = calculate_rsi(df).iloc[-1]
        sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
        
        trend = "Bullish" if current_price > sma_20 else "Bearish"
        
        return {
            "price": current_price,
            "rsi": float(rsi),
            "sma_20": float(sma_20),
            "sma_50": float(sma_50) if sma_50 else None,
            "trend": trend,
            "volume": float(df['Volume'].iloc[-1]) if 'Volume' in df.columns else 0,
        }
    
    def get_ai_analysis(self, symbol: str, chart_tf: str, trade_tf: str) -> Tuple[Optional[str], str]:
        """
        Get AI analysis for an asset.
        
        Args:
            symbol: Asset name (QX Broker format)
            chart_tf: Chart timeframe
            trade_tf: Trade duration
            
        Returns:
            Tuple of (analysis_text, signal)
            
        Raises:
            DataUnavailableError: If analysis cannot be generated
        """
        # Currently uses yfinance-based analysis (secondary source)
        # QX Broker doesn't provide AI analysis directly
        try:
            analysis, signal = get_yahoo_ai_analysis(symbol, chart_tf, trade_tf)
            return analysis, signal
        except Exception as e:
            logger.error(f"AI analysis failed for {symbol}: {e}")
            raise DataUnavailableError(f"Analysis unavailable for {symbol}")
    
    def scan_assets(self, limit: int = 10) -> list:
        """
        Scan assets for trading opportunities.
        Uses secondary source as primary doesn't support bulk scanning.
        
        Args:
            limit: Number of top opportunities to return
            
        Returns:
            List of opportunity dicts
        """
        # Import here to avoid circular imports
        from utils.market_data import scan_top_assets
        return scan_top_assets(limit=limit)
    
    def is_primary_available(self) -> bool:
        """Check if primary source is currently available."""
        return self.primary_available
    
    def has_fallback_occurred(self) -> bool:
        """Check if fallback has occurred at least once."""
        return self.primary_failed_once


# Singleton instance
_data_manager: Optional[DataManager] = None


def get_data_manager() -> DataManager:
    """Get or create singleton DataManager instance."""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager


def shutdown_data_manager() -> None:
    """Shutdown the data manager and stop background threads."""
    global _data_manager
    if _data_manager:
        _data_manager.stop()
        _data_manager = None
