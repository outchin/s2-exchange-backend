"""
Django management command to seed exchange communication channels with mock data.
Usage: python manage.py seed_exchange_channels
"""
from django.core.management.base import BaseCommand
from exchange.models import ExchangeCommunicationChannel


class Command(BaseCommand):
    help = 'Seed exchange communication channels with mock data for Facebook Messenger, Telegram, etc.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding exchange communication channels...')

        # Primary contact channels (email, phone, website)
        primary_channels = [
            {
                'name': 'Email',
                'platform': ExchangeCommunicationChannel.PLATFORM_EMAIL,
                'url': 'mailto:contact@s2exchange.com',
                'description': 'Send us an email',
                'is_primary': True,
                'sort_order': 1,
            },
            {
                'name': 'Phone',
                'platform': ExchangeCommunicationChannel.PLATFORM_PHONE,
                'url': 'tel:+959123456789',
                'description': 'Call us directly',
                'is_primary': True,
                'sort_order': 2,
            },
            {
                'name': 'Website',
                'platform': ExchangeCommunicationChannel.PLATFORM_WEBSITE,
                'url': 'https://s2exchange.com',
                'description': 'Visit our website',
                'is_primary': True,
                'sort_order': 3,
            },
        ]

        # Additional messaging channels
        additional_channels = [
            {
                'name': 'Facebook Messenger',
                'platform': ExchangeCommunicationChannel.PLATFORM_MESSENGER,
                'url': 'https://m.me/s2exchange',
                'description': 'Chat with us on Messenger',
                'is_primary': False,
                'sort_order': 4,
            },
            {
                'name': 'Telegram',
                'platform': ExchangeCommunicationChannel.PLATFORM_TELEGRAM,
                'url': 'https://t.me/s2exchange_bot',
                'description': 'Contact us on Telegram',
                'is_primary': False,
                'sort_order': 5,
            },
            {
                'name': 'Facebook Page',
                'platform': ExchangeCommunicationChannel.PLATFORM_FACEBOOK,
                'url': 'https://www.facebook.com/s2exchange',
                'description': 'Message us on Facebook',
                'is_primary': False,
                'sort_order': 6,
            },
        ]

        channels = primary_channels + additional_channels

        created_count = 0
        updated_count = 0

        for channel_data in channels:
            channel, created = ExchangeCommunicationChannel.objects.update_or_create(
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
        self.stdout.write(self.style.SUCCESS(f'  Total: {ExchangeCommunicationChannel.objects.count()}'))
