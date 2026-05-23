from decimal import Decimal

from django.core.management.base import BaseCommand

from exchange.models import Currency, ExchangeRate, ExchangeRateTier


class Command(BaseCommand):
    help = 'Seed initial currencies and exchange rates for S2Exchange.'

    def handle(self, *args, **options):
        rows = [
            {
                'code': 'THB',
                'name': 'Thai Baht',
                'symbol': 'THB',
                'sort_order': 10,
                'buy_rate': Decimal('45.5000'),
                'sell_rate': Decimal('46.2000'),
                'change_percentage': Decimal('0.500'),
                'tiers': [
                    ('buy', Decimal('0.00'), Decimal('999999.99'), Decimal('45.5000'), 'Under 1,000,000 MMK'),
                    ('buy', Decimal('1000000.00'), Decimal('1499999.99'), Decimal('45.3000'), '1,000,000 - 1,499,999 MMK'),
                    ('buy', Decimal('1500000.00'), None, Decimal('45.0000'), '1,500,000+ MMK'),
                    ('sell', Decimal('0.00'), Decimal('9999.99'), Decimal('46.2000'), 'Under 10,000 THB'),
                    ('sell', Decimal('10000.00'), Decimal('19999.99'), Decimal('46.4000'), '10,000 - 19,999 THB'),
                    ('sell', Decimal('20000.00'), None, Decimal('46.6000'), '20,000+ THB'),
                ],
            },
            {
                'code': 'VND',
                'name': 'Vietnamese Dong',
                'symbol': 'VND',
                'sort_order': 20,
                'buy_rate': Decimal('0.1800'),
                'sell_rate': Decimal('0.1900'),
                'change_percentage': Decimal('-0.200'),
                'tiers': [],
            },
            {
                'code': 'JPY',
                'name': 'Japanese Yen',
                'symbol': 'JPY',
                'sort_order': 30,
                'buy_rate': Decimal('29.8000'),
                'sell_rate': Decimal('30.5000'),
                'change_percentage': Decimal('1.200'),
                'tiers': [],
            },
            {
                'code': 'USD',
                'name': 'US Dollar',
                'symbol': 'USD',
                'sort_order': 40,
                'buy_rate': Decimal('2100.0000'),
                'sell_rate': Decimal('2150.0000'),
                'change_percentage': Decimal('0.800'),
                'tiers': [],
            },
        ]

        for row in rows:
            currency, _ = Currency.objects.update_or_create(
                code=row['code'],
                defaults={
                    'name': row['name'],
                    'symbol': row['symbol'],
                    'sort_order': row['sort_order'],
                    'is_active': True,
                },
            )
            exchange_rate, _ = ExchangeRate.objects.update_or_create(
                currency=currency,
                defaults={
                    'buy_rate': row['buy_rate'],
                    'sell_rate': row['sell_rate'],
                    'change_percentage': row['change_percentage'],
                    'is_active': True,
                },
            )
            for direction, min_amount, max_amount, rate, label in row['tiers']:
                ExchangeRateTier.objects.update_or_create(
                    exchange_rate=exchange_rate,
                    direction=direction,
                    min_amount=min_amount,
                    max_amount=max_amount,
                    defaults={
                        'rate': rate,
                        'label': label,
                        'is_active': True,
                    },
                )

        self.stdout.write(self.style.SUCCESS('Seeded S2Exchange currencies and rates.'))
