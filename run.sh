#!/bin/bash

# Telegram Trading Bot Setup & Run Script
# This script sets up the environment, installs dependencies, and runs the bot

set -e  # Exit on error

echo "=========================================="
echo "  🤖 Telegram Trading Bot Setup & Run    "
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $PYTHON_VERSION"

# Navigate to the bot directory (assuming script is in the project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created."
else
    echo "✅ Virtual environment already exists."
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip (bypass externally-managed-environment)
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet --break-system-packages 2>/dev/null || pip install --upgrade pip --quiet

# Install requirements
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet --break-system-packages 2>/dev/null || pip install -r requirements.txt --quiet
echo "✅ Dependencies installed."

# Install Playwright browsers if api_quotex is installed
if pip show api_quotex &> /dev/null || grep -q "api_quotex" requirements.txt 2>/dev/null; then
    echo ""
    echo "🌐 Installing Playwright browsers (required for QX Broker login)..."
    python -m playwright install chromium --quiet 2>/dev/null || echo "⚠️ Playwright browser installation skipped (may need manual installation)"
fi

# Setup .env file
echo ""
echo "=========================================="
echo "  🔐 Bot Token Configuration             "
echo "=========================================="
echo ""

if [ -f ".env" ]; then
    echo "⚠️  A .env file already exists."
    read -p "Do you want to overwrite it? (y/n): " OVERWRITE
    if [[ "$OVERWRITE" =~ ^[Yy]$ ]]; then
        rm .env
        echo "🗑️  Old .env file removed."
    else
        echo "ℹ️  Keeping existing .env file."
    fi
fi

if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Please enter your Telegram Bot Token:"
    echo "   (Get it from @BotFather on Telegram)"
    echo ""
    read -p "Bot Token: " BOT_TOKEN
    
    if [ -z "$BOT_TOKEN" ]; then
        echo "❌ Error: Bot token cannot be empty."
        exit 1
    fi
    
    # Start creating .env file
    cat > .env << EOF
# Telegram Bot Token
BOT_TOKEN=$BOT_TOKEN

# Optional: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Optional: Trade logging enabled (true/false)
ENABLE_TRADE_LOGGING=false
EOF
    
    echo ""
    echo "✅ Bot token saved!"
fi

# QX Broker Configuration
echo ""
echo "=========================================="
echo "  📊 QX Broker Configuration             "
echo "=========================================="
echo ""
echo "To use QX Broker as primary data source, enter your credentials."
echo "Leave blank to use Yahoo Finance/Binance only."
echo ""

# Check if QX credentials already exist in .env
QX_EMAIL_EXISTING=""
QX_PASS_EXISTING=""
if [ -f ".env" ]; then
    QX_EMAIL_EXISTING=$(grep "^QX_EMAIL=" .env 2>/dev/null | cut -d'=' -f2)
    QX_PASS_EXISTING=$(grep "^QX_PASSWORD=" .env 2>/dev/null | cut -d'=' -f2)
fi

if [ -n "$QX_EMAIL_EXISTING" ]; then
    echo "⚠️  QX Broker credentials already configured."
    echo "   Email: ${QX_EMAIL_EXISTING:0:3}***@${QX_EMAIL_EXISTING#*@}"
    read -p "Do you want to update them? (y/n): " UPDATE_QX
    if [[ ! "$UPDATE_QX" =~ ^[Yy]$ ]]; then
        echo "ℹ️  Keeping existing QX Broker credentials."
    else
        # Remove old credentials
        sed -i '/^QX_EMAIL=/d' .env 2>/dev/null || true
        sed -i '/^QX_PASSWORD=/d' .env 2>/dev/null || true
    fi
fi

# Check if we need to ask for QX credentials
QX_NEEDS_CONFIG=true
if [ -f ".env" ] && grep -q "^QX_EMAIL=" .env 2>/dev/null && grep -q "^QX_PASSWORD=" .env 2>/dev/null; then
    QX_NEEDS_CONFIG=false
fi

if [ "$QX_NEEDS_CONFIG" = true ]; then
    echo ""
    echo "📝 Enter your QX Broker credentials:"
    echo "   (These are used to fetch real-time market data)"
    echo ""
    read -p "QX Broker Email: " QX_EMAIL
    read -sp "QX Broker Password: " QX_PASSWORD
    echo ""
    
    if [ -n "$QX_EMAIL" ] && [ -n "$QX_PASSWORD" ]; then
        # Append QX credentials to .env
        cat >> .env << EOF

# QX Broker Credentials (Primary Data Source)
QX_EMAIL=$QX_EMAIL
QX_PASSWORD=$QX_PASSWORD

# Primary data source: "qxbroker" or "yfinance"
PRIMARY_DATA_SOURCE=qxbroker

# QX Broker connection timeout (seconds)
QX_TIMEOUT=5
EOF
        echo ""
        echo "✅ QX Broker credentials saved!"
        echo "ℹ️  First run will open a browser window for authentication."
    else
        echo ""
        echo "ℹ️  QX Broker credentials skipped. Using Yahoo Finance/Binance as data source."
        echo "   You can add credentials later by editing .env file."
        
        # Add fallback config
        if ! grep -q "^PRIMARY_DATA_SOURCE=" .env 2>/dev/null; then
            cat >> .env << EOF

# Primary data source: "qxbroker" or "yfinance"
PRIMARY_DATA_SOURCE=yfinance
EOF
        fi
    fi
fi

# Verify .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found after setup."
    exit 1
fi

echo ""
echo "=========================================="
echo "  🚀 Starting the Bot                    "
echo "=========================================="
echo ""
echo "ℹ️  The bot is now starting..."
echo "ℹ️  Press Ctrl+C to stop the bot."
echo ""
echo "⚠️  NOTE: On first run, a browser window may open for QX Broker authentication."
echo "    Complete the login, then close the browser to continue."
echo ""

# Run the bot
python bot.py
