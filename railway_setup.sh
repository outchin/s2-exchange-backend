#!/usr/bin/env bash
# Railway Setup Script
# Run this after deploying to Railway

set -e

echo "🚀 Setting up S2Exchange Backend on Railway..."
echo ""

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo "Install it with: npm install -g @railway/cli"
    exit 1
fi

echo "✓ Railway CLI found"
echo ""

# Login check
echo "Checking Railway authentication..."
railway whoami || {
    echo "Please login to Railway:"
    railway login
}

echo ""
echo "Please select your backend service (NOT the database)"
railway link

echo ""
echo "📦 Running migrations..."
railway run python manage.py migrate

echo ""
echo "👤 Creating superuser..."
echo "Please enter superuser details:"
railway run python manage.py createsuperuser

echo ""
echo "🌱 Seeding exchange data..."
railway run python manage.py seed_exchange_data

echo ""
echo "✅ Setup complete!"
echo ""
echo "Your backend is ready at:"
echo "https://s2-exchange-backend-production.up.railway.app"
echo ""
echo "API Endpoints:"
echo "  Health:  https://s2-exchange-backend-production.up.railway.app/api/health/"
echo "  Rates:   https://s2-exchange-backend-production.up.railway.app/api/rates/"
echo "  Admin:   https://s2-exchange-backend-production.up.railway.app/admin/"
echo ""
echo "WebSocket:"
echo "  wss://s2-exchange-backend-production.up.railway.app/ws/rates/"
echo ""
