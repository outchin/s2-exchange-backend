#!/usr/bin/env python
"""
Quick script to check admin users in the database
Run this with: railway run python check_admin.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's2exchange_api.settings')
django.setup()

from exchange.models import User

print("\n" + "="*60)
print("CHECKING ADMIN USERS IN DATABASE")
print("="*60 + "\n")

# Check all users
all_users = User.objects.all()
print(f"Total users in database: {all_users.count()}")

# Check staff users
staff_users = User.objects.filter(is_staff=True)
print(f"Staff users: {staff_users.count()}")

# Check superusers
superusers = User.objects.filter(is_superuser=True)
print(f"Superusers: {superusers.count()}")

print("\n" + "-"*60)
print("ALL USERS:")
print("-"*60)

for user in all_users:
    print(f"\nEmail: {user.email}")
    print(f"  - is_active: {user.is_active}")
    print(f"  - is_staff: {user.is_staff}")
    print(f"  - is_superuser: {user.is_superuser}")
    print(f"  - has_usable_password: {user.has_usable_password()}")
    print(f"  - created_at: {user.created_at}")

print("\n" + "="*60)

# If no superuser exists, offer to create one
if not superusers.exists():
    print("\n⚠️  NO SUPERUSER FOUND!")
    print("\nTo create a superuser, run:")
    print("  railway run python manage.py create_default_superuser")
    print("\nOr create manually:")
    print("  railway run python manage.py createsuperuser")
else:
    print("\n✅ Superuser exists!")
    print("\nYou can login with:")
    for su in superusers:
        print(f"  Email: {su.email}")
