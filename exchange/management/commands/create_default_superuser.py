"""
Django management command to create a default superuser if none exists.
This is useful for automated deployments.
"""

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from exchange.models import User
import os


class Command(BaseCommand):
    help = 'Creates a default superuser if no superuser exists'

    def handle(self, *args, **options):
        # Check if any superuser exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Superuser already exists. Skipping creation.')
            )
            return

        # Get credentials from environment or use defaults
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@s2exchange.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
        last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')

        try:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Superuser created successfully!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Email: {email}')
            )
            self.stdout.write(
                self.style.WARNING(f'⚠️  Please change the password after first login!')
            )
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create superuser: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
