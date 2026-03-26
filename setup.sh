#!/bin/bash
# One-time setup script for Analytics Platform
# Run this once to install dependencies and configure the tool

set -e

echo "🚀 Setting up Analytics Platform..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv already exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment already exists"
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate and install dependencies
echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Check if .env exists
echo ""
if [ -f ".env" ]; then
    echo "✅ Configuration file (.env) already exists"
else
    echo "⚙️  Creating configuration file..."
    cp .env.example .env
    echo "✅ Created .env from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your database credentials:"
    echo "   nano .env"
    echo ""
    echo "   Update these values:"
    echo "   - DB_HOST=your_database_ip"
    echo "   - DB_PORT=5432"
    echo "   - DB_NAME=litellm"
    echo "   - DB_USER=taasaa"
fi

# Test database connection
echo ""
echo "🔌 Testing database connection..."
if PYTHONPATH=src python -m analytics.cli --test-db 2>/dev/null; then
    echo "✅ Database connection successful!"
    echo ""
    echo "🎉 Setup complete! You're ready to analyze."
    echo ""
    echo "Usage:"
    echo "  ./analytics              # Last 14 days"
    echo "  ./analytics --days 7     # Last 7 days"
    echo "  ./analytics --help       # Show all options"
else
    echo "❌ Database connection failed"
    echo ""
    echo "Please check your .env configuration:"
    echo "   nano .env"
    echo ""
    echo "Then run: ./analytics --test-db"
fi

deactivate