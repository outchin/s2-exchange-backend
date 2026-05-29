"""
Django management command to seed communication channels with mock data.
Usage: python manage.py seed_communication_channels
"""
from django.core.management.base import BaseCommand
from exchange.models import CommunicationChannel


class Command(BaseCommand):
    help = 'Seed communication channels with mock data for Facebook, Telegram, Viber'

    def handle(self, *args, **options):
        self.stdout.write('Seeding communication channels...')

        channels = [
            {
                'name': 'Facebook Group',
                'platform': CommunicationChannel.PLATFORM_FACEBOOK,
                'url': 'https://www.facebook.com/groups/s2exchange',
                'description': 'Join our Facebook group for exchange updates',
                'sort_order': 1,
            },
            {
                'name': 'Facebook Messenger',
                'platform': CommunicationChannel.PLATFORM_MESSENGER,
                'url': 'https://m.me/s2exchange',
                'description': 'Chat with us on Messenger',
                'sort_order': 2,
            },
            {
                'name': 'Telegram',
                'platform': CommunicationChannel.PLATFORM_TELEGRAM,
                'url': 'https://t.me/s2exchange',
                'description': 'Contact us on Telegram',
                'sort_order': 3,
            },
            {
                'name': 'Viber',
                'platform': CommunicationChannel.PLATFORM_VIBER,
                'url': 'viber://chat?number=%2B959123456789',
                'description': 'Call us on Viber',
                'sort_order': 4,
            },
        ]

        created_count = 0
        updated_count = 0

        for channel_data in channels:
            channel, created = CommunicationChannel.objects.update_or_create(
                platform=channel_data['platform'],
                defaults=channel_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Created: {channel.name} ({channel.get_platform_display()})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Updated: {channel.name} ({channel.get_platform_display()})')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'  Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Total: {CommunicationChannel.objects.count()}'))
