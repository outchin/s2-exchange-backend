# Railway Quick Deploy Guide
## (You already have PostgreSQL database)

Since you already have a PostgreSQL database on Railway, follow these simplified steps:

---

## Step 1: Deploy Backend Service

1. **Go to your Railway project dashboard**
   - Where your PostgreSQL database is already running

2. **Add New Service**
   - Click **"+ New"** button
   - Select **"GitHub Repo"**
   - Choose **`outchin/s2-exchange-backend`**

3. **Railway will automatically**:
   - Detect it's a Django project
   - Install dependencies from `requirements.txt`
   - Use `Procfile` to start with Daphne
   - Generate a public URL

---

## Step 2: Connect to Your Existing Database

1. **Get Database URL**
   - Click on your PostgreSQL service
   - Go to **"Variables"** tab
   - Copy the `DATABASE_URL` value

2. **Add to Backend Service**
   - Click on your backend service
   - Go to **"Variables"** tab
   - Add variable: `DATABASE_URL` = (paste the URL from step 1)

   **OR** if Railway offers it:
   - Use **"Reference Variable"** to link directly to the database

---

## Step 3: Add Required Environment Variables

In your backend service → **Variables** tab, add:

### Required Variables

```bash
DJANGO_SECRET_KEY=<generate-this>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Generate Django Secret Key

Run this command locally and copy the output:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Optional Variables (if needed)

```bash
CORS_ALLOWED_ORIGINS=https://your-flutter-app.com
GOOGLE_OAUTH2_CLIENT_ID=your-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-secret
```

---

## Step 4: Wait for Deployment

Railway will automatically:
1. Build your Django app
2. Install all dependencies
3. Start Daphne server
4. Generate a public URL (e.g., `https://s2-exchange-backend-production.up.railway.app`)

Check the **"Deployments"** tab to see progress and logs.

---

## Step 5: Run Database Migrations

After the first deployment succeeds:

### Option A: Via Railway CLI (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Select your backend service (not database)
# Then run migrations:
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Seed exchange data
railway run python manage.py seed_exchange_data
```

### Option B: Via Railway Dashboard

1. Go to your service → **Settings** → **Deploys**
2. Add a **Deploy Trigger** or run commands manually in logs

---

## Step 6: Get Your Production URLs

After deployment, you'll have:

- **API Base URL**: `https://your-app.up.railway.app/api/`
- **WebSocket URL**: `wss://your-app.up.railway.app/ws/rates/`
- **Admin Panel**: `https://your-app.up.railway.app/admin/`

**Test your endpoints:**

```bash
# Health check
curl https://your-app.up.railway.app/api/health/

# Get exchange rates
curl https://your-app.up.railway.app/api/rates/
```

---

## Step 7: Update Flutter App

Update your Flutter app to use production URLs:

```dart
// lib/config/api_config.dart or wherever you configure
const String apiBaseUrl = 'https://your-app.up.railway.app/api';
const String wsUrl = 'wss://your-app.up.railway.app/ws/rates/';
```

Run your Flutter app:
```bash
flutter run --dart-define=S2EXCHANGE_API_BASE_URL=https://your-app.up.railway.app/api --dart-define=S2EXCHANGE_WS_URL=wss://your-app.up.railway.app/ws/rates/
```

---

## Troubleshooting

### Deployment Fails

Check logs in Railway → Deployments → View Logs

Common issues:
- **Missing `DJANGO_SECRET_KEY`**: Add it in Variables
- **Database connection error**: Check `DATABASE_URL` is correct
- **Port binding error**: Railway automatically sets `$PORT` - make sure Procfile uses it

### Migrations Not Run

```bash
railway run python manage.py migrate --check
railway run python manage.py showmigrations
```

### WebSocket Not Working

- Verify Daphne is running (check logs for "Starting server")
- Test with `wss://` not `ws://` in production
- Check CORS settings if connecting from browser

### Admin Login Not Working

Create superuser again:
```bash
railway run python manage.py createsuperuser
```

---

## Automatic Deployments

Every time you push to `master` branch on GitHub:
- Railway will automatically redeploy
- GitHub Actions will run tests first
- Deployment happens if tests pass

---

## Monitor Your App

- **Logs**: Railway Dashboard → Your Service → Deployments → View Logs
- **Metrics**: Railway Dashboard → Your Service → Metrics
- **Database**: Railway Dashboard → PostgreSQL Service → Metrics

---

## Cost

- PostgreSQL: ~$5/month (1GB)
- Backend Service: Based on usage (Railway Hobby Plan includes $5 credit)
- Total estimate: ~$5-10/month

---

## Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Repo: https://github.com/outchin/s2-exchange-backend

---

**That's it! Your backend will be live with WebSocket support over HTTPS/WSS!** 🚀
