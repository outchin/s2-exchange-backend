#!/usr/bin/env python
"""
Manual superuser creation script
Run this with: railway run python setup_superuser.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's2exchange_api.settings')
django.setup()

from exchange.models import User

print("\n" + "="*70)
print("MANUAL SUPERUSER CREATION")
print("="*70 + "\n")

# Your credentials
EMAIL = "odleyadolesc@hostdjong.com"
PASSWORD = 'DTIJk^u|"w38Z3`:{HCtA{lO'

print(f"Creating/Updating superuser: {EMAIL}")

# Delete existing user if exists
existing = User.objects.filter(email=EMAIL).first()
if existing:
    print(f"Found existing user. Deleting...")
    existing.delete()

# Create fresh superuser
try:
    user = User.objects.create_superuser(
        email=EMAIL,
        password=PASSWORD,
    )
    user.display_name = "Admin User"
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()

    print("\n" + "="*70)
    print("✅ SUCCESS! Superuser created!")
    print("="*70)
    print(f"\nLogin credentials:")
    print(f"  URL: https://s2-exchange-backend-production.up.railway.app/admin/")
    print(f"  Email: {EMAIL}")
    print(f"  Password: {PASSWORD}")
    print("\n" + "="*70 + "\n")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print(traceback.format_exc())
