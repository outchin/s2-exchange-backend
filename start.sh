#!/bin/bash

# S2Exchange Backend Startup Script
# This script sets up and runs the Django backend

set -e  # Exit on error

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting S2Exchange Backend..."
echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your actual configuration!"
    echo "   Required: FIREBASE_DATABASE_URL, FIREBASE_SERVICE_ACCOUNT_PATH"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit and configure .env first..."
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Collect static files (optional, mainly for production)
# python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo "🌐 Starting Django development server..."
echo ""

# Get port from .env or use default 8000
PORT=${DJANGO_PORT:-8000}

# Run the server
python manage.py runserver 0.0.0.0:$PORT
