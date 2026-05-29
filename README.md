# S2Exchange Backend API

Django REST API backend for S2Exchange mobile application with real-time WebSocket support for exchange rates.

## Features

- RESTful API for exchange rates
- Real-time WebSocket updates
- JWT authentication
- Google OAuth2 integration
- Admin panel for managing rates
- PostgreSQL database (production)
- SQLite database (development)
- Firebase Realtime Database sync (optional)

## Tech Stack

- **Framework**: Django 5.2
- **API**: Django REST Framework
- **WebSocket**: Django Channels + Daphne
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: JWT, Google OAuth2
- **Deployment**: Railway
- **CI/CD**: GitHub Actions

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/outchin/s2-exchange-backend.git
   cd s2-exchange-backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Seed initial data**
   ```bash
   python manage.py seed_exchange_data
   ```

8. **Start development server with WebSocket support**
   ```bash
   # Use Daphne for WebSocket support
   daphne -b 0.0.0.0 -p 8000 s2exchange_api.asgi:application

   # Or for HTTP-only development
   python manage.py runserver
   ```

9. **Access the application**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - Health: http://localhost:8000/api/health/

## API Endpoints

### Public Endpoints

- `GET /api/health/` - Health check
- `GET /api/rates/` - List all active exchange rates
- `GET /api/rates/<currency_code>/` - Get specific rate
- `GET /api/convert/?from=MMK&to=THB&amount=1000` - Convert currency
- `POST /api/orders/` - Create exchange order

### Authentication Endpoints

- `POST /api/auth/google/` - Google OAuth2 login
- `POST /api/auth/token/` - Get JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Admin Endpoints (Authentication Required)

- `POST /api/rates/<currency_code>/sync/` - Sync rate to Firebase

### WebSocket

- `ws://localhost:8000/ws/rates/` - Real-time exchange rates

**WebSocket Message Format:**

Client → Server:
```json
{
  "type": "request_rates"
}
```

Server → Client:
```json
{
  "type": "rates_update",
  "rates": [
    {
      "id": 1,
      "currency": "THB",
      "buy_rate": 90.5,
      "sell_rate": 91.0,
      "last_updated": "2026-05-29T10:00:00Z",
      "buy_tiers": [...],
      "sell_tiers": [...]
    }
  ]
}
```

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy to Railway

1. **Fork/Clone this repository**

2. **Sign up for Railway**: https://railway.app

3. **Create new project**
   - Connect GitHub repository
   - Add PostgreSQL database
   - Configure environment variables

4. **Set environment variables** (see DEPLOYMENT.md)

5. **Deploy**
   - Railway will automatically deploy
   - WebSocket will work over WSS (secure)

## Development

### Running Tests

```bash
python manage.py test
```

### Code Quality

```bash
# Install dev dependencies
pip install flake8 black

# Check code style
flake8 .

# Format code
black .
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations
```

## Project Structure

```
s2-exchange-backend/
├── exchange/               # Main app
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── consumers.py       # WebSocket consumers
│   ├── routing.py         # WebSocket routing
│   ├── admin.py           # Admin configurations
│   └── management/        # Management commands
├── s2exchange_api/        # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   ├── asgi.py            # ASGI config
│   └── wsgi.py            # WSGI config
├── website/               # Marketing website
├── .github/
│   └── workflows/         # CI/CD workflows
├── requirements.txt       # Python dependencies
├── Procfile              # Railway/Heroku config
├── railway.json          # Railway config
├── runtime.txt           # Python version
├── DEPLOYMENT.md         # Deployment guide
└── README.md             # This file
```

## Environment Variables

See `.env.example` for all available environment variables.

### Required for Production

- `DJANGO_SECRET_KEY` - Django secret key
- `DJANGO_ALLOWED_HOSTS` - Comma-separated allowed hosts
- `DATABASE_URL` - PostgreSQL connection URL
- `DJANGO_DEBUG=false` - Disable debug in production

### Optional

- `CORS_ALLOWED_ORIGINS` - CORS allowed origins
- `GOOGLE_OAUTH2_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_OAUTH2_CLIENT_SECRET` - Google OAuth secret
- `FIREBASE_DATABASE_URL` - Firebase database URL
- `FIREBASE_SERVICE_ACCOUNT_PATH` - Firebase credentials path

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary and confidential.

## Support

For issues and questions:
- GitHub Issues: https://github.com/outchin/s2-exchange-backend/issues
- Email: support@s2exchange.com

## Acknowledgments

- Built with Django and Django REST Framework
- WebSocket support powered by Django Channels
- Deployed on Railway
