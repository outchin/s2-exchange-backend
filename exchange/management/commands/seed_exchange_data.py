from decimal import Decimal

from django.core.management.base import BaseCommand

from exchange.models import Currency, ExchangeRate, ExchangeRateTier


class Command(BaseCommand):
    help = 'Seed initial currencies and exchange rates for S2Exchange.'

    def handle(self, *args, **options):
        # Note: The system uses MMK as the base currency
        # buy_rate: MMK amount needed to buy 1 unit of foreign currency
        # sell_rate: MMK amount received when selling 1 unit of foreign currency
        # Tiers: buy tiers use MMK amount, sell tiers use foreign currency amount

        rows = [
            {
                'code': 'THB',
                'name': 'Thai Baht',
                'symbol': '฿',
                'sort_order': 10,
                'buy_rate': Decimal('133.8600'),  # Kyat to Baht (We Sell THB)
                'sell_rate': Decimal('775.0000'),  # Baht to Kyat (We Buy THB)
                'change_percentage': Decimal('0.500'),
                'is_active': True,
                'tiers': [
                    # ဘတ်အရောင်းနှုန်းများ (We Sell THB rates)
                    # Kyat to Baht - Customer buys THB with MMK (MMK amount tiers)
                    # 27th May 2026 - ထိုင်းစံတော်ချိန် 10:48am⏱️
                    ('buy', Decimal('0.00'), Decimal('668999.99'), Decimal('133.8600'), '27th May 2026 - 10:48am | ဘတ်5000အထက် 👉🏻 133.86'),
                    ('buy', Decimal('669000.00'), Decimal('1335999.99'), Decimal('133.5100'), '27th May 2026 - 10:48am | ဘတ်10000အထက် 👉🏻 133.51'),
                    ('buy', Decimal('1336000.00'), Decimal('3994999.99'), Decimal('133.1500'), '27th May 2026 - 10:48am | ဘတ်30000အထက် 👉🏻 133.15'),
                    ('buy', Decimal('3995000.00'), Decimal('6639999.99'), Decimal('132.8000'), '27th May 2026 - 10:48am | ဘတ်50000အထက် 👉🏻 132.8'),
                    ('buy', Decimal('6640000.00'), None, Decimal('132.4500'), '27th May 2026 - 10:48am | ဘတ်100000အထက် 👉🏻 132.45'),

                    # ဘတ်အဝယ်နှုန်းများ (We Buy THB rates)
                    # Baht to Kyat - Customer sells THB for MMK (THB amount tiers)
                    # 27th May 2026 - ထိုင်းစံတော်ချိန် 10:47am⏱️
                    # Note: The rate shown is MMK per 100,000 Kyat (inverted from the description)
                    # If customer has 5000 THB, they get: 5000 * 775 = 3,875,000 MMK
                    ('sell', Decimal('0.00'), Decimal('4999.99'), Decimal('775.0000'), '27th May 2026 - 10:47am | ဘတ်5000အထက် 👉🏻 775'),
                    ('sell', Decimal('5000.00'), Decimal('9999.99'), Decimal('772.0000'), '27th May 2026 - 10:47am | ဘတ်10000အထက် 👉🏻 772'),
                    ('sell', Decimal('10000.00'), Decimal('49999.99'), Decimal('770.0000'), '27th May 2026 - 10:47am | ဘတ်50000အထက် 👉🏻 770'),
                    ('sell', Decimal('50000.00'), None, Decimal('768.0000'), '27th May 2026 - 10:47am | ဘတ်100000အထက် 👉🏻 768'),
                ],
            },
            {
                'code': 'VND',
                'name': 'Vietnamese Dong',
                'symbol': '₫',
                'sort_order': 20,
                'buy_rate': Decimal('0.0850'),
                'sell_rate': Decimal('0.0900'),
                'change_percentage': Decimal('-0.200'),
                'is_active': False,  # Disabled
                'tiers': [],
            },
            {
                'code': 'JPY',
                'name': 'Japanese Yen',
                'symbol': '¥',
                'sort_order': 30,
                'buy_rate': Decimal('14.5000'),
                'sell_rate': Decimal('15.0000'),
                'change_percentage': Decimal('1.200'),
                'is_active': False,  # Disabled
                'tiers': [],
            },
            {
                'code': 'MMK',
                'name': 'Myanmar Kyat',
                'symbol': 'K',
                'sort_order': 5,
                'buy_rate': Decimal('1.0000'),  # Base currency
                'sell_rate': Decimal('1.0000'),  # Base currency
                'change_percentage': Decimal('0.000'),
                'is_active': True,
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
                    'is_active': row.get('is_active', True),
                },
            )
            exchange_rate, _ = ExchangeRate.objects.update_or_create(
                currency=currency,
                defaults={
                    'buy_rate': row['buy_rate'],
                    'sell_rate': row['sell_rate'],
                    'change_percentage': row['change_percentage'],
                    'is_active': row.get('is_active', True),
                },
            )

            # Clear existing tiers for this exchange rate
            ExchangeRateTier.objects.filter(exchange_rate=exchange_rate).delete()

            # Add new tiers
            for direction, min_amount, max_amount, rate, label in row['tiers']:
                ExchangeRateTier.objects.create(
                    exchange_rate=exchange_rate,
                    direction=direction,
                    min_amount=min_amount,
                    max_amount=max_amount,
                    rate=rate,
                    label=label,
                    is_active=True,
                )

        self.stdout.write(self.style.SUCCESS('Seeded S2Exchange currencies and rates.'))
