"""
QX Broker Client - Primary Data Source
Handles connection to QX Broker using API-Quotex library with error handling and reconnection logic.
Based on: https://github.com/A11ksa/API-Quotex
"""
import asyncio
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
import threading

from utils.logger import logger
from config import QX_EMAIL, QX_PASSWORD, QX_TIMEOUT, SIMULATE_QX_FAILURE


class PrimarySourceError(Exception):
    """Custom exception for primary data source (QX Broker) failures."""
    pass


class QXBrokerClient:
    """
    QX Broker client for fetching market data.
    Uses the official API-Quotex library with Playwright login.
    
    Features:
    - Async WebSocket connection for real-time data
    - Playwright-based authentication (SSID extraction)
    - Automatic reconnection on failure
    - Support for both demo and live accounts
    """
    
    def __init__(self):
        self.client = None
        self.connected = False
        self.last_connect_time: Optional[datetime] = None
        self.balance: Optional[float] = None
        self._session_id: Optional[str] = None
        self._ssid: Optional[str] = None
        self._is_demo = True  # Use demo account by default
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._lock = threading.Lock()
        
    def _get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop for async operations."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
    
    def _connect(self) -> bool:
        """
        Establish connection to QX Broker using API-Quotex.
        Returns True if successful, False otherwise.
        """
        try:
            # Check if simulation mode is enabled
            if SIMULATE_QX_FAILURE:
                logger.warning("Simulation mode: QX Broker connection forced to fail")
                raise PrimarySourceError("Simulated QX Broker failure")
            
            # Validate credentials are configured
            if not QX_EMAIL or not QX_PASSWORD:
                logger.warning("QX Broker credentials not configured")
                raise PrimarySourceError("QX Broker credentials not configured")
            
            logger.info("Attempting to connect to QX Broker...")
            logger.info(f"Email: {QX_EMAIL[:3]}***@{QX_EMAIL.split('@')[1]}")
            
            # Import api_quotex dynamically
            try:
                from api_quotex import AsyncQuotexClient, get_ssid
            except ImportError:
                logger.error("api_quotex library not installed. Run: pip install api_quotex")
                raise PrimarySourceError("api_quotex library not installed")
            
            # Get SSID using Playwright (this will open a browser on first run)
            logger.info("Extracting SSID via Playwright (browser may open)...")
            try:
                ssid_info = get_ssid(email=QX_EMAIL, password=QX_PASSWORD)
                self._ssid = ssid_info.get("demo") if self._is_demo else ssid_info.get("live")
                
                if not self._ssid:
                    raise PrimarySourceError("Failed to extract SSID from QX Broker")
                
                logger.info("SSID extracted successfully")
            except Exception as e:
                logger.error(f"Playwright login failed: {e}")
                logger.info("Make sure you have completed the browser authentication")
                raise PrimarySourceError(f"Authentication failed: {e}")
            
            # Create async client
            self.client = AsyncQuotexClient(ssid=self._ssid, is_demo=self._is_demo)
            
            # Run async connect in a new thread
            def run_connect():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.client.connect())
                finally:
                    loop.close()
            
            with self._lock:
                success = run_connect()
            
            if not success:
                raise PrimarySourceError("Failed to establish WebSocket connection")
            
            logger.info("✅ QX Broker connection established successfully")
            self.connected = True
            self.last_connect_time = datetime.now()
            self._session_id = f"session_{int(time.time())}"
            
            return True
            
        except PrimarySourceError:
            raise
        except Exception as e:
            logger.error(f"QX Broker connection error: {e}")
            raise PrimarySourceError(f"Connection error: {e}")
    
    def _ensure_connected(self) -> None:
        """Ensure connection is active, reconnect if needed."""
        if not self.connected or self._is_session_expired():
            logger.info("Attempting to (re)connect to QX Broker...")
            self._connect()
    
    def _is_session_expired(self) -> bool:
        """Check if session has expired (older than 5 minutes)."""
        if not self.last_connect_time:
            return True
        return datetime.now() - self.last_connect_time > timedelta(minutes=5)
    
    def disconnect(self) -> None:
        """Disconnect from QX Broker."""
        if self.client:
            try:
                def run_disconnect():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(self.client.disconnect())
                    finally:
                        loop.close()
                
                with self._lock:
                    run_disconnect()
            except Exception as e:
                logger.debug(f"Disconnect error (ignored): {e}")
        
        self.connected = False
        self._session_id = None
        self.last_connect_time = None
        logger.info("Disconnected from QX Broker")
    
    def get_price(self, asset: str) -> float:
        """
        Get current price for an asset.
        
        Args:
            asset: Asset name in QX Broker format (e.g., "EURUSD_otc", "AUDCAD_otc")
            
        Returns:
            Current price as float
            
        Raises:
            PrimarySourceError: If fetch fails
        """
        try:
            self._ensure_connected()
            
            # Convert asset name to QX format if needed
            qx_asset = self._convert_to_qx_format(asset)
            
            logger.debug(f"Fetching price for {qx_asset} from QX Broker")
            
            # Run async get_quote in a new thread
            def run_get_quote():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.client.get_quote(qx_asset))
                finally:
                    loop.close()
            
            with self._lock:
                quote_data = run_get_quote()
            
            if not quote_data or 'value' not in quote_data:
                raise PrimarySourceError(f"No price data for {qx_asset}")
            
            price = float(quote_data['value'])
            logger.debug(f"Price for {asset}: {price}")
            return price
            
        except PrimarySourceError:
            raise
        except Exception as e:
            logger.error(f"Error fetching price for {asset}: {e}")
            raise PrimarySourceError(f"Failed to fetch price: {e}")
    
    def get_candles(self, asset: str, period: str = "1m", count: int = 100) -> pd.DataFrame:
        """
        Get candlestick data for an asset.
        
        Args:
            asset: Asset name
            period: Timeframe (e.g., "1m", "5m", "1h")
            count: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            PrimarySourceError: If fetch fails
        """
        try:
            self._ensure_connected()
            
            # Convert asset name to QX format
            qx_asset = self._convert_to_qx_format(asset)
            
            # Convert period to seconds
            timeframe_seconds = self._period_to_seconds(period)
            
            logger.debug(f"Fetching {count} candles for {qx_asset} ({period})")
            
            # Run async get_candles in a new thread
            def run_get_candles():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(
                        self.client.get_candles(qx_asset, timeframe_seconds, count)
                    )
                finally:
                    loop.close()
            
            with self._lock:
                candles_data = run_get_candles()
            
            if not candles_data:
                raise PrimarySourceError(f"No candle data for {asset}")
            
            # Convert to DataFrame
            df = pd.DataFrame(candles_data)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 
                              'close': 'Close', 'volume': 'Volume'}, inplace=True)
            
            logger.debug(f"Fetched {len(df)} candles for {asset}")
            return df
            
        except PrimarySourceError:
            raise
        except Exception as e:
            logger.error(f"Error fetching candles for {asset}: {e}")
            raise PrimarySourceError(f"Failed to fetch candles: {e}")
    
    def get_balance(self) -> Optional[float]:
        """
        Get account balance.
        
        Returns:
            Account balance or None if unavailable
            
        Raises:
            PrimarySourceError: If fetch fails
        """
        try:
            self._ensure_connected()
            
            def run_get_balance():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.client.get_balance())
                finally:
                    loop.close()
            
            with self._lock:
                balance_info = run_get_balance()
            
            if not balance_info:
                raise PrimarySourceError("No balance data available")
            
            self.balance = float(balance_info.balance)
            logger.info(f"Account balance: {self.balance} {balance_info.currency}")
            return self.balance
            
        except PrimarySourceError:
            raise
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise PrimarySourceError(f"Failed to fetch balance: {e}")
    
    def _convert_to_qx_format(self, asset: str) -> str:
        """
        Convert asset name to QX Broker format.
        
        Examples:
            "EUR/USD" -> "EURUSD_otc"
            "Bitcoin (OTC)" -> "BTCUSD_otc"
            "Gold" -> "GOLD"
        """
        # Remove common suffixes and clean up
        cleaned = asset.replace(" (OTC)", "").replace("(OTC)", "").strip()
        cleaned = cleaned.replace("/", "").replace(" ", "")
        
        # Common mappings
        mappings = {
            "EURUSD": "EURUSD_otc",
            "GBPUSD": "GBPUSD_otc",
            "USDJPY": "USDJPY_otc",
            "AUDUSD": "AUDUSD_otc",
            "USDCAD": "USDCAD_otc",
            "NZDUSD": "NZDUSD_otc",
            "USDCHF": "USDCHF_otc",
            "AUDCAD": "AUDCAD_otc",
            "AUDNZD": "AUDNZD_otc",
            "NZDCAD": "NZDCAD_otc",
            "GBPAUD": "GBPAUD_otc",
            "GBPCAD": "GBPCAD_otc",
            "GBPJPY": "GBPJPY_otc",
            "EURJPY": "EURJPY_otc",
            "EURGBP": "EURGBP_otc",
            "EURAUD": "EURAUD_otc",
            "EURCAD": "EURCAD_otc",
            "AUDJPY": "AUDJPY_otc",
            "CADJPY": "CADJPY_otc",
            "CHFJPY": "CHFJPY_otc",
            "NZDJPY": "NZDJPY_otc",
            "BTCUSD": "CRYPTOBTCUSD_otc",
            "ETHUSD": "CRYPTOETHUSD_otc",
            "XRPUSD": "CRYPTOXRPUSD_otc",
            "LTCUSD": "CRYPTOLTCUSD_otc",
            "BCHUSD": "CRYPTOBCHUSD_otc",
            "BNBUSD": "CRYPTOBNBUSD_otc",
            "ADAUSD": "CRYPTOADAUSD_otc",
            "SOLUSD": "CRYPTOSOLUSD_otc",
            "DOTUSD": "CRYPTODOTUSD_otc",
            "DOGEUSD": "CRYPTODOGEUSD_otc",
            "GOLD": "GOLD",
            "SILVER": "SILVER",
            "USCRUDE": "USCRUDE",
            "UKBRENT": "UKBRENT",
        }
        
        # Try direct mapping
        if cleaned.upper() in mappings:
            return mappings[cleaned.upper()]
        
        # Default: add _otc suffix if not already present
        if not cleaned.endswith("_otc"):
            return cleaned.upper() + "_otc"
        
        return cleaned.upper()
    
    def _period_to_seconds(self, period: str) -> int:
        """Convert period string to seconds."""
        mapping = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400,
        }
        return mapping.get(period.lower(), 60)
    
    def test_connection(self) -> bool:
        """
        Test if QX Broker connection is working.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._connect()
            return True
        except PrimarySourceError as e:
            logger.warning(f"QX Broker connection test failed: {e}")
            return False
        except Exception as e:
            logger.warning(f"QX Broker connection test error: {e}")
            return False


# Singleton instance
_qx_client: Optional[QXBrokerClient] = None


def get_qx_client() -> QXBrokerClient:
    """Get or create singleton QXBrokerClient instance."""
    global _qx_client
    if _qx_client is None:
        _qx_client = QXBrokerClient()
    return _qx_client
