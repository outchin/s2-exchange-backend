# Security Best Practices

## 🔒 Credentials Management

### ✅ DO:
- Store ALL credentials in Railway Environment Variables
- Use `os.environ.get()` to read credentials at runtime
- Use different credentials for development and production
- Rotate passwords regularly
- Use strong, randomly generated passwords

### ❌ DON'T:
- **NEVER** hardcode credentials in source code
- **NEVER** commit `.env` files to git
- **NEVER** use default/example passwords in production
- **NEVER** share credentials in documentation
- **NEVER** log passwords or secrets

---

## 🔐 Environment Variables (Railway)

All sensitive data MUST be stored in Railway Variables:

```bash
DJANGO_SECRET_KEY          # Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SUPERUSER_EMAIL     # Your admin email
DJANGO_SUPERUSER_PASSWORD  # Strong password (min 12 chars, mixed case, numbers, symbols)
DATABASE_URL               # Auto-set by Railway PostgreSQL
```

### How to Set in Railway:

1. Go to Railway Dashboard
2. Select your service
3. Click "Variables" tab
4. Click "+ New Variable"
5. Enter name and value
6. Save

---

## 📁 Files That Must NOT Be Committed

These files are in `.gitignore`:

```
.env
.env.local
db.sqlite3
*credentials*.json
*serviceAccount*.json
```

---

## 🔍 Security Checklist

Before deploying:

- [ ] No hardcoded passwords in code
- [ ] No credentials in `.env.example`
- [ ] All secrets in Railway Variables
- [ ] `.env` in `.gitignore`
- [ ] `DEBUG=False` in production
- [ ] Strong `DJANGO_SECRET_KEY` generated
- [ ] HTTPS enabled (automatic on Railway)
- [ ] CSRF protection enabled
- [ ] CORS properly configured

---

## 🚨 If Credentials Are Leaked

If you accidentally commit credentials:

1. **Immediately change** all affected passwords
2. **Revoke** API keys/tokens
3. **Remove** from git history: `git filter-branch` or BFG Repo-Cleaner
4. **Rotate** all related secrets
5. **Audit** for unauthorized access

---

## 📚 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Railway Security](https://docs.railway.app/reference/variables)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
