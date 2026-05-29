# Superuser Setup Guide

## ⚠️ Issue: Admin Login Not Working

If you cannot login to the admin panel after deployment, follow these steps:

---

## ✅ Solution 1: Manual Superuser Creation (GUARANTEED TO WORK)

### Step 1: Login to Railway CLI

```bash
railway login
```

### Step 2: Link to Your Project

```bash
cd "/Users/zawwaisoe/Desktop/Personal Projects/S2Exchange/s2_exchange_backend"
railway link
```

Select:
- Project: `acceptable-victory`
- Environment: `production`
- Service: `s2-exchange-backend` (NOT Postgres)

### Step 3: Run Manual Setup Script

```bash
railway run python setup_superuser.py
```

This will:
- Delete any existing user with email `odleyadolesc@hostdjong.com`
- Create fresh superuser
- Set password to: `DTIJk^u|"w38Z3`:{HCtA{lO`
- Show success message

### Step 4: Login

```
URL: https://s2-exchange-backend-production.up.railway.app/admin/
Email: odleyadolesc@hostdjong.com
Password: DTIJk^u|"w38Z3`:{HCtA{lO
```

---

## ✅ Solution 2: Via Railway Dashboard Shell (Alternative)

1. Go to Railway Dashboard
2. Click on your backend service
3. Click "Deployments" tab
4. Find "Shell" or "Run Command" option
5. Run:

```bash
python setup_superuser.py
```

---

## ✅ Solution 3: Direct Database SQL (Last Resort)

If Railway CLI doesn't work, you can create superuser directly in database:

### Step 1: Get Database Connection

Railway Dashboard → PostgreSQL service → Connect → Copy connection string

### Step 2: Connect to Database

```bash
psql "<your-database-url>"
```

### Step 3: Create Superuser with SQL

```sql
-- First, delete existing user if any
DELETE FROM exchange_user WHERE email = 'odleyadolesc@hostdjong.com';

-- Create superuser (password is already hashed)
-- Hash for password: DTIJk^u|"w38Z3`:{HCtA{lO
-- You need to generate this hash using Django's make_password
```

**Note:** For SQL method, you need to hash the password first using Django shell.

---

## 🔍 Verify Superuser Exists

### Check via Railway CLI:

```bash
railway run python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's2exchange_api.settings')
django.setup()
from exchange.models import User
print('Total users:', User.objects.count())
print('Superusers:', User.objects.filter(is_superuser=True).count())
for u in User.objects.filter(is_superuser=True):
    print(f'  - {u.email} (staff={u.is_staff}, active={u.is_active})')
"
```

---

## 📋 Troubleshooting

### Issue: Railway CLI "No such file or directory"

This means Railway can't find Python. Use the Railway dashboard shell instead.

### Issue: "User matching query does not exist"

Superuser wasn't created. Run `setup_superuser.py` again.

### Issue: "Password incorrect"

Password might be wrong. Run `setup_superuser.py` to reset it.

### Issue: CSRF error

Add to Railway environment variables:
```
DJANGO_ALLOWED_HOSTS=s2-exchange-backend-production.up.railway.app
```

---

## 🎯 After Successful Login

1. Change your password immediately in admin panel
2. Add your real email address
3. Create additional staff users if needed
4. Test creating/editing exchange rates

---

## 🆘 Still Not Working?

Check Railway deployment logs for errors:
1. Railway Dashboard → Your Service → Deployments
2. Click latest deployment → View Logs
3. Look for errors in preDeployCommand section
4. Share the error message for further debugging
