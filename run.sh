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

# Install/upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed."

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
    
    # Create .env file with the token
    cat > .env << EOF
# Telegram Bot Token
BOT_TOKEN=$BOT_TOKEN

# Optional: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Optional: Trade logging enabled (true/false)
ENABLE_TRADE_LOGGING=false
EOF
    
    echo ""
    echo "✅ .env file created successfully!"
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

# Run the bot
python bot.py
