"""Asset lists for trading analysis."""

# Crypto assets (Binance symbols)
CRYPTO_ASSETS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "MATICUSDT",
]

# Forex pairs (Yahoo Finance symbols)
FOREX_ASSETS = [
    "EURUSD=X",
    "GBPUSD=X",
    "USDJPY=X",
    "GBPJPY=X",
    "AUDUSD=X",
    "USDCAD=X",
]

# Indices (Yahoo Finance symbols)
INDICES_ASSETS = [
    "SPY",      # S&P 500 ETF
    "QQQ",      # NASDAQ ETF
    "DIA",      # Dow Jones ETF
    "IWM",      # Russell 2000 ETF
    "^GSPC",    # S&P 500 Index
    "^IXIC",    # NASDAQ Composite
]

# Commodities (Yahoo Finance symbols)
COMMODITIES_ASSETS = [
    "GC=F",     # Gold
    "SI=F",     # Silver
    "CL=F",     # Crude Oil
    "NG=F",     # Natural Gas
    "HG=F",     # Copper
]

# Combined asset list for AI Best Trade Finder
ALL_ASSETS = {
    "crypto": CRYPTO_ASSETS,
    "forex": FOREX_ASSETS,
    "indices": INDICES_ASSETS,
    "commodities": COMMODITIES_ASSETS,
}

# Display names for categories
CATEGORY_NAMES = {
    "crypto": "🪙 Crypto",
    "forex": "💱 Forex",
    "indices": "📈 Indices",
    "commodities": "🏆 Commodities",
}

# Asset display name mapping (symbol -> friendly name)
ASSET_NAMES = {
    # Crypto
    "BTCUSDT": "Bitcoin",
    "ETHUSDT": "Ethereum",
    "BNBUSDT": "Binance Coin",
    "SOLUSDT": "Solana",
    "XRPUSDT": "Ripple",
    "ADAUSDT": "Cardano",
    "DOGEUSDT": "Dogecoin",
    "AVAXUSDT": "Avalanche",
    "LINKUSDT": "Chainlink",
    "MATICUSDT": "Polygon",
    # Forex
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "USDJPY=X": "USD/JPY",
    "GBPJPY=X": "GBP/JPY",
    "AUDUSD=X": "AUD/USD",
    "USDCAD=X": "USD/CAD",
    # Indices
    "SPY": "S&P 500 ETF",
    "QQQ": "NASDAQ ETF",
    "DIA": "Dow Jones ETF",
    "IWM": "Russell 2000 ETF",
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ",
    # Commodities
    "GC=F": "Gold",
    "SI=F": "Silver",
    "CL=F": "Crude Oil",
    "NG=F": "Natural Gas",
    "HG=F": "Copper",
}
