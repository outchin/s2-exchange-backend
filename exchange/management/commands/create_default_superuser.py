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

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate the default superuser',
        )

    def handle(self, *args, **options):
        # Get credentials from environment variables ONLY - no defaults for security
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
        last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')

        # Validate required environment variables
        if not email:
            self.stdout.write(
                self.style.ERROR('❌ DJANGO_SUPERUSER_EMAIL environment variable is required!')
            )
            self.stdout.write('Set it in Railway: Settings → Variables → Add Variable')
            return

        if not password:
            self.stdout.write(
                self.style.ERROR('❌ DJANGO_SUPERUSER_PASSWORD environment variable is required!')
            )
            self.stdout.write('Set it in Railway: Settings → Variables → Add Variable')
            return

        self.stdout.write(f'Looking for superuser with email: {email}')

        # Check if this specific user exists
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            if options.get('force'):
                self.stdout.write(self.style.WARNING(f'Deleting existing user: {email}'))
                existing_user.delete()
            else:
                # Update existing user to be superuser
                self.stdout.write(self.style.WARNING(f'User {email} already exists. Updating...'))
                existing_user.is_staff = True
                existing_user.is_superuser = True
                existing_user.is_active = True
                existing_user.set_password(password)
                existing_user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Superuser updated successfully!')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Email: {email}')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Password: {password}')
                )
                return

        # Create new superuser
        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
            )
            user.display_name = f'{first_name} {last_name}'
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f'✅ Superuser created successfully!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Email: {email}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Password: {password}')
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
            import traceback
            self.stdout.write(traceback.format_exc())
