from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from .lottery_import import import_lottery_tickets_from_csv
from .models import Currency, ExchangeRate, ExchangeRateTier, LotteryTicket


class ExchangeRateTierTests(TestCase):
    def setUp(self):
        currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='THB',
            is_active=True,
        )
        self.rate = ExchangeRate.objects.create(
            currency=currency,
            buy_rate='45.5000',
            sell_rate='46.2000',
            is_active=True,
        )
        ExchangeRateTier.objects.create(
            exchange_rate=self.rate,
            direction=ExchangeRateTier.DIRECTION_BUY,
            min_amount='1500000.00',
            max_amount=None,
            rate='45.0000',
            label='1,500,000+ MMK',
        )
        ExchangeRateTier.objects.create(
            exchange_rate=self.rate,
            direction=ExchangeRateTier.DIRECTION_SELL,
            min_amount='20000.00',
            max_amount=None,
            rate='46.6000',
            label='20,000+ THB',
        )

    def test_convert_uses_buy_tier_for_mmk_amount(self):
        response = self.client.get('/api/convert/?from=MMK&to=THB&amount=1800000')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['converted_amount'], 40000.0)

    def test_convert_uses_sell_tier_for_foreign_amount(self):
        response = self.client.get('/api/convert/?from=THB&to=MMK&amount=20000')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['converted_amount'], 932000.0)


class LotteryTicketCsvImportTests(TestCase):
    def test_import_creates_and_updates_duplicates(self):
        csv_data = (
            'draw_date,draw_name,number,bundle_size,quantity,price,status,note\n'
            '2026-06-01,Thai Lottery - 2026-06-01,001234,1,10,120,available,\n'
            '2026-06-01,Thai Lottery - 2026-06-01,001234,1,7,130,available,updated\n'
        )

        summary = import_lottery_tickets_from_csv(
            SimpleUploadedFile('tickets.csv', csv_data.encode('utf-8'))
        )

        ticket = LotteryTicket.objects.get(number='001234', bundle_size=1)
        self.assertEqual(summary.created, 1)
        self.assertEqual(summary.updated, 1)
        self.assertEqual(summary.skipped, 0)
        self.assertEqual(summary.errors, [])
        self.assertEqual(ticket.quantity, 7)
        self.assertEqual(str(ticket.price), '130.00')
        self.assertEqual(ticket.note, 'updated')

    def test_import_skips_invalid_ticket_numbers_and_bundle_sizes(self):
        csv_data = (
            'draw_date,number,bundle_size,quantity,price\n'
            '2026-06-01,12345,1,10,120\n'
            '2026-06-01,123456,3,10,120\n'
        )

        summary = import_lottery_tickets_from_csv(
            SimpleUploadedFile('tickets.csv', csv_data.encode('utf-8'))
        )

        self.assertEqual(summary.created, 0)
        self.assertEqual(summary.updated, 0)
        self.assertEqual(summary.skipped, 2)
        self.assertEqual(len(summary.errors), 2)
        self.assertIn('number must be exactly 6 digits', summary.errors[0])
        self.assertIn('bundle_size must be one of 1, 2, 5, 10', summary.errors[1])
