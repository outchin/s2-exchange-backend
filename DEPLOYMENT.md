# S2Exchange Backend - Railway Deployment Guide

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. GitHub repository connected
3. Railway CLI (optional): `npm install -g @railway/cli`

## Deployment Steps

### 1. Create New Project on Railway

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `hninsunyein/s2-exchange-backend`
4. Railway will automatically detect Django and start deployment

### 2. Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provision a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically set

### 3. Configure Environment Variables

In Railway project settings, add these environment variables:

```bash
# Django Settings
DJANGO_SECRET_KEY=<generate-a-strong-secret-key>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=your-app.up.railway.app,your-custom-domain.com

# Database (automatically set by Railway PostgreSQL)
# DATABASE_URL=postgresql://...

# CORS Settings (add your Flutter app domains)
CORS_ALLOWED_ORIGINS=https://your-flutter-app.com,http://localhost:3000

# Google OAuth2 (optional)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH2_REDIRECT_URI=https://your-app.up.railway.app/api/auth/google/callback/

# Firebase (optional)
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
FIREBASE_RATES_PATH=exchange_rates
```

### 4. Generate Django Secret Key

Run this command to generate a secure secret key:

```python
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run Migrations

After deployment, run migrations:

Option 1 - Via Railway CLI:
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py seed_exchange_data
```

Option 2 - Via Railway Dashboard:
1. Go to your service settings
2. Click "Variables" tab
3. Add a one-time script in the deployment settings

### 6. Collect Static Files

Railway will automatically run `collectstatic` during deployment if configured.
Verify in your deployment logs.

## Testing the Deployment

### Test HTTP Endpoints

```bash
# Health check
curl https://your-app.up.railway.app/api/health/

# Get exchange rates
curl https://your-app.up.railway.app/api/rates/

# Get specific rate
curl https://your-app.up.railway.app/api/rates/THB/
```

### Test WebSocket Connection

Use a WebSocket testing tool:

```javascript
const ws = new WebSocket('wss://your-app.up.railway.app/ws/rates/');

ws.onopen = () => {
  console.log('Connected!');
  ws.send(JSON.stringify({ type: 'request_rates' }));
};

ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};
```

## Custom Domain Setup (Optional)

1. Go to your Railway service settings
2. Click "Settings" → "Domains"
3. Click "Add Domain"
4. Follow the instructions to configure your DNS

## CI/CD with GitHub Actions

Every push to the `main`/`master` branch will automatically trigger a deployment on Railway.

To disable auto-deploy:
1. Go to service settings
2. Find "Deploy Triggers"
3. Configure as needed

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | Yes | - | Django secret key for security |
| `DJANGO_DEBUG` | No | `false` | Debug mode (set to `false` in production) |
| `DJANGO_ALLOWED_HOSTS` | Yes | - | Comma-separated list of allowed hosts |
| `DATABASE_URL` | Yes | Auto-set | PostgreSQL connection URL |
| `CORS_ALLOWED_ORIGINS` | No | - | Comma-separated list of CORS origins |
| `PORT` | No | Auto-set | Port number (set by Railway) |

## Monitoring and Logs

View logs in Railway dashboard:
1. Go to your service
2. Click "Deployments"
3. Select a deployment to view logs

## Troubleshooting

### Database Connection Issues

Check if `DATABASE_URL` is set:
```bash
railway run env | grep DATABASE_URL
```

### WebSocket Connection Fails

1. Verify Daphne is running (check deployment logs)
2. Test WSS connection (not WS) in production
3. Check CORS settings if connecting from browser

### Static Files Not Loading

Ensure `collectstatic` runs during deployment:
```bash
railway run python manage.py collectstatic --noinput
```

### Migration Issues

Run migrations manually:
```bash
railway run python manage.py migrate
```

## Security Checklist

- [ ] `DJANGO_DEBUG=false` in production
- [ ] Strong `DJANGO_SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] CORS origins restricted to your domains
- [ ] PostgreSQL database enabled
- [ ] Environment variables secured (not in code)
- [ ] HTTPS/WSS enabled (automatic on Railway)

## Scaling

Railway supports automatic scaling. Configure in:
1. Service Settings → "Resources"
2. Adjust memory and CPU as needed

## Cost Estimation

Railway pricing:
- Hobby Plan: $5/month (includes $5 credit)
- PostgreSQL: ~$5/month for 1GB
- Estimated total: ~$5-10/month for small applications

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project GitHub: https://github.com/hninsunyein/s2-exchange-backend
