import csv
import io
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.db import transaction

from .models import LotteryDraw, LotteryTicket


REQUIRED_COLUMNS = {'draw_date', 'number', 'bundle_size', 'quantity', 'price'}
ALLOWED_BUNDLE_SIZES = {1, 2, 5, 10}
ALLOWED_STATUSES = {choice[0] for choice in LotteryTicket.STATUS_CHOICES}


@dataclass
class LotteryImportSummary:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_errors(self):
        return len(self.errors)


def import_lottery_tickets_from_csv(uploaded_file):
    summary = LotteryImportSummary()
    text = _decode_uploaded_file(uploaded_file)
    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        summary.errors.append('CSV file is empty or missing a header row.')
        return summary

    normalized_fieldnames = [field.strip() for field in reader.fieldnames]
    missing_columns = REQUIRED_COLUMNS - set(normalized_fieldnames)
    if missing_columns:
        summary.errors.append(
            f'Missing required columns: {", ".join(sorted(missing_columns))}.'
        )
        return summary

    with transaction.atomic():
        for row_number, raw_row in enumerate(reader, start=2):
            row = {
                (key.strip() if key else key): (value.strip() if value else '')
                for key, value in raw_row.items()
            }
            cleaned = _clean_row(row, row_number, summary)
            if cleaned is None:
                summary.skipped += 1
                continue

            draw, _ = LotteryDraw.objects.get_or_create(
                draw_date=cleaned['draw_date'],
                defaults={
                    'name': cleaned['draw_name'],
                    'is_active': True,
                },
            )
            if draw.name != cleaned['draw_name'] and row.get('draw_name'):
                draw.name = cleaned['draw_name']
                draw.save(update_fields=['name', 'updated_at'])

            _, created = LotteryTicket.objects.update_or_create(
                draw=draw,
                number=cleaned['number'],
                bundle_size=cleaned['bundle_size'],
                defaults={
                    'quantity': cleaned['quantity'],
                    'price': cleaned['price'],
                    'status': cleaned['status'],
                    'note': cleaned['note'],
                },
            )
            if created:
                summary.created += 1
            else:
                summary.updated += 1

    return summary


def _decode_uploaded_file(uploaded_file):
    data = uploaded_file.read()
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError:
        return data.decode('utf-8')


def _clean_row(row, row_number, summary):
    number = row.get('number', '')
    if not (len(number) == 6 and number.isdigit()):
        summary.errors.append(f'Row {row_number}: number must be exactly 6 digits.')
        return None

    try:
        bundle_size = int(row.get('bundle_size', ''))
    except ValueError:
        summary.errors.append(f'Row {row_number}: bundle_size must be a number.')
        return None
    if bundle_size not in ALLOWED_BUNDLE_SIZES:
        summary.errors.append(
            f'Row {row_number}: bundle_size must be one of 1, 2, 5, 10.'
        )
        return None

    try:
        quantity = int(row.get('quantity', ''))
    except ValueError:
        summary.errors.append(f'Row {row_number}: quantity must be a number.')
        return None
    if quantity < 0:
        summary.errors.append(f'Row {row_number}: quantity cannot be negative.')
        return None

    try:
        price = Decimal(row.get('price', ''))
    except (InvalidOperation, TypeError):
        summary.errors.append(f'Row {row_number}: price must be a valid decimal.')
        return None
    if price < 0:
        summary.errors.append(f'Row {row_number}: price cannot be negative.')
        return None

    draw_date = _parse_date(row.get('draw_date', ''))
    if draw_date is None:
        summary.errors.append(f'Row {row_number}: draw_date must use YYYY-MM-DD.')
        return None

    status = row.get('status') or LotteryTicket.STATUS_AVAILABLE
    if status not in ALLOWED_STATUSES:
        summary.errors.append(
            f'Row {row_number}: status must be one of {", ".join(sorted(ALLOWED_STATUSES))}.'
        )
        return None

    return {
        'draw_date': draw_date,
        'draw_name': row.get('draw_name') or f'Thai Lottery - {draw_date}',
        'number': number,
        'bundle_size': bundle_size,
        'quantity': quantity,
        'price': price,
        'status': status,
        'note': row.get('note', ''),
    }


def _parse_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None
