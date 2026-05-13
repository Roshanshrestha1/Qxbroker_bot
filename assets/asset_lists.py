"""Asset lists for trading analysis - Synced with QX Broker and market_data.py."""

# Crypto assets (Yahoo Finance symbols matching market_data.py)
CRYPTO_ASSETS = [
    "BTC-USD",
    "ETH-USD",
    "BNB-USD",
    "SOL-USD",
    "XRP-USD",
    "ADA-USD",
    "DOGE-USD",
    "AVAX-USD",
    "LINK-USD",
    "MATIC-USD",
    "LTC-USD",
    "DOT-USD",
    "ATOM-USD",
    "UNI-USD",
    "ETC-USD",
]

# Forex pairs (Simple names - will be mapped to TradingView OANDA in market_data.py)
FOREX_ASSETS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "USDCHF",
    "NZDUSD",
    "EURGBP",
    "EURJPY",
    "GBPJPY",
    "USDZAR",
    "USDMXN",
    "USDTRY",
    "EURTRY",
]

# Indices (Yahoo Finance symbols)
INDICES_ASSETS = [
    "^GSPC",    # S&P 500 Index
    "^DJI",     # Dow Jones
    "^IXIC",    # NASDAQ Composite
    "^NYA",     # NYSE
    "^RUT",     # Russell 2000
    "^VIX",     # Volatility Index
    "^FTSE",    # FTSE 100
    "^GDAXI",   # DAX
    "^FCHI",    # CAC 40
    "^N225",    # Nikkei 225
    "^HSI",     # Hang Seng
    "^AXJO",    # ASX 200
]

# Commodities (Yahoo Finance symbols)
COMMODITIES_ASSETS = [
    "GC=F",     # Gold
    "SI=F",     # Silver
    "PL=F",     # Platinum
    "PA=F",     # Palladium
    "CL=F",     # Crude Oil WTI
    "BZ=F",     # Brent Oil
    "NG=F",     # Natural Gas
    "HG=F",     # Copper
    "ZC=F",     # Corn
    "ZW=F",     # Wheat
]

# Stocks (Yahoo Finance symbols)
STOCKS_ASSETS = [
    "AAPL",     # Apple
    "TSLA",     # Tesla
    "NVDA",     # NVIDIA
    "MSFT",     # Microsoft
    "AMZN",     # Amazon
    "GOOGL",    # Google
    "META",     # Meta
    "AMD",      # AMD
    "NFLX",     # Netflix
    "COIN",     # Coinbase
    "BA",       # Boeing
    "DIS",      # Disney
    "V",        # Visa
    "JPM",      # JPMorgan
    "WMT",      # Walmart
]

# Combined asset list for AI Best Trade Finder
ALL_ASSETS = {
    "crypto": CRYPTO_ASSETS,
    "forex": FOREX_ASSETS,
    "indices": INDICES_ASSETS,
    "commodities": COMMODITIES_ASSETS,
    "stocks": STOCKS_ASSETS,
}

# Display names for categories
CATEGORY_NAMES = {
    "crypto": "🪙 Crypto",
    "forex": "💱 Forex",
    "indices": "📈 Indices",
    "commodities": "🏆 Commodities",
    "stocks": "📊 Stocks",
}

# Asset display name mapping (symbol -> friendly name)
ASSET_NAMES = {
    # Crypto
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "BNB-USD": "Binance Coin",
    "SOL-USD": "Solana",
    "XRP-USD": "Ripple",
    "ADA-USD": "Cardano",
    "DOGE-USD": "Dogecoin",
    "AVAX-USD": "Avalanche",
    "LINK-USD": "Chainlink",
    "MATIC-USD": "Polygon",
    "LTC-USD": "Litecoin",
    "DOT-USD": "Polkadot",
    "ATOM-USD": "Cosmos",
    "UNI-USD": "Uniswap",
    "ETC-USD": "Ethereum Classic",
    # Forex
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDJPY": "USD/JPY",
    "AUDUSD": "AUD/USD",
    "USDCAD": "USD/CAD",
    "USDCHF": "USD/CHF",
    "NZDUSD": "NZD/USD",
    "EURGBP": "EUR/GBP",
    "EURJPY": "EUR/JPY",
    "GBPJPY": "GBP/JPY",
    "USDZAR": "USD/ZAR",
    "USDMXN": "USD/MXN",
    "USDTRY": "USD/TRY",
    "EURTRY": "EUR/TRY",
    # Indices
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "NASDAQ",
    "^NYA": "NYSE",
    "^RUT": "Russell 2000",
    "^VIX": "VIX",
    "^FTSE": "FTSE 100",
    "^GDAXI": "DAX",
    "^FCHI": "CAC 40",
    "^N225": "Nikkei 225",
    "^HSI": "Hang Seng",
    "^AXJO": "ASX 200",
    # Commodities
    "GC=F": "Gold",
    "SI=F": "Silver",
    "PL=F": "Platinum",
    "PA=F": "Palladium",
    "CL=F": "Crude Oil WTI",
    "BZ=F": "Brent Oil",
    "NG=F": "Natural Gas",
    "HG=F": "Copper",
    "ZC=F": "Corn",
    "ZW=F": "Wheat",
    # Stocks
    "AAPL": "Apple",
    "TSLA": "Tesla",
    "NVDA": "NVIDIA",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "GOOGL": "Google",
    "META": "Meta",
    "AMD": "AMD",
    "NFLX": "Netflix",
    "COIN": "Coinbase",
    "BA": "Boeing",
    "DIS": "Disney",
    "V": "Visa",
    "JPM": "JPMorgan",
    "WMT": "Walmart",
}
