import json
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import Currency, ExchangeOrder, ExchangeRate, ExchangeRateTier
from .services import sync_rate_to_realtime_database


def _error(message, status=400):
    return JsonResponse({'error': message}, status=status)


@require_GET
def health(request):
    return JsonResponse({'status': 'ok', 'service': 's2exchange-api'})


@require_GET
def rate_list(request):
    rates = (
        ExchangeRate.objects.select_related('currency')
        .filter(is_active=True, currency__is_active=True)
    )
    return JsonResponse([rate.to_api_dict() for rate in rates], safe=False)


@require_GET
def rate_detail(request, currency_code):
    try:
        rate = ExchangeRate.objects.select_related('currency').get(
            currency__code=currency_code.upper(),
            is_active=True,
            currency__is_active=True,
        )
    except ExchangeRate.DoesNotExist:
        return _error('Exchange rate not found.', status=404)

    return JsonResponse(rate.to_api_dict())


@require_GET
def convert(request):
    from_currency = request.GET.get('from', '').upper()
    to_currency = request.GET.get('to', '').upper()
    amount_value = request.GET.get('amount', '')

    try:
        amount = Decimal(amount_value)
    except (InvalidOperation, TypeError):
        return _error('A valid amount is required.')

    if amount <= 0:
        return _error('Amount must be greater than zero.')

    if from_currency == to_currency:
        result = amount
    elif from_currency == 'MMK':
        rate = _get_active_rate(to_currency)
        if not rate:
            return _error('Target currency rate not found.', status=404)
        tier_rate = rate.rate_for_amount(ExchangeRateTier.DIRECTION_BUY, amount)
        result = amount / tier_rate
    elif to_currency == 'MMK':
        rate = _get_active_rate(from_currency)
        if not rate:
            return _error('Source currency rate not found.', status=404)
        tier_rate = rate.rate_for_amount(ExchangeRateTier.DIRECTION_SELL, amount)
        result = amount * tier_rate
    else:
        from_rate = _get_active_rate(from_currency)
        to_rate = _get_active_rate(to_currency)
        if not from_rate or not to_rate:
            return _error('Currency rate not found.', status=404)
        from_tier_rate = from_rate.rate_for_amount(
            ExchangeRateTier.DIRECTION_SELL,
            amount,
        )
        mmk_amount = amount * from_tier_rate
        to_tier_rate = to_rate.rate_for_amount(
            ExchangeRateTier.DIRECTION_BUY,
            mmk_amount,
        )
        result = mmk_amount / to_tier_rate

    return JsonResponse({
        'from_currency': from_currency,
        'to_currency': to_currency,
        'amount': float(amount),
        'converted_amount': float(result),
    })


@csrf_exempt
@require_http_methods(['POST'])
def create_order(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return _error('Invalid JSON payload.')

    required_fields = ['customer_name', 'customer_phone', 'currency_code', 'direction', 'amount']
    missing_fields = [field for field in required_fields if not payload.get(field)]
    if missing_fields:
        return _error(f'Missing required fields: {", ".join(missing_fields)}.')

    currency_code = payload['currency_code'].upper()
    direction = payload['direction']
    if direction not in [ExchangeOrder.DIRECTION_BUY, ExchangeOrder.DIRECTION_SELL]:
        return _error('Direction must be buy or sell.')

    try:
        amount = Decimal(str(payload['amount']))
    except (InvalidOperation, TypeError):
        return _error('A valid amount is required.')

    if amount <= 0:
        return _error('Amount must be greater than zero.')

    rate = _get_active_rate(currency_code)
    if not rate:
        return _error('Currency rate not found.', status=404)

    if direction == ExchangeOrder.DIRECTION_BUY:
        rate_used = rate.rate_for_amount(ExchangeRateTier.DIRECTION_BUY, amount)
        foreign_amount = amount / rate_used
        mmk_amount = amount
    else:
        rate_used = rate.rate_for_amount(ExchangeRateTier.DIRECTION_SELL, amount)
        foreign_amount = amount
        mmk_amount = amount * rate_used

    order = ExchangeOrder.objects.create(
        customer_name=payload['customer_name'],
        customer_phone=payload['customer_phone'],
        currency=rate.currency,
        direction=direction,
        foreign_amount=foreign_amount,
        mmk_amount=mmk_amount,
        rate_used=rate_used,
        note=payload.get('note', ''),
    )

    return JsonResponse({
        'id': order.id,
        'status': order.status,
        'currency_code': order.currency.code,
        'direction': order.direction,
        'foreign_amount': float(order.foreign_amount),
        'mmk_amount': float(order.mmk_amount),
        'rate_used': float(order.rate_used),
        'created_at': order.created_at.isoformat(),
    }, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def sync_rate(request, currency_code):
    try:
        rate = ExchangeRate.objects.select_related('currency').get(
            currency__code=currency_code.upper()
        )
    except ExchangeRate.DoesNotExist:
        return _error('Exchange rate not found.', status=404)

    result = sync_rate_to_realtime_database(rate)
    return JsonResponse(result)


def _get_active_rate(currency_code):
    if not currency_code:
        return None
    try:
        return ExchangeRate.objects.select_related('currency').get(
            currency__code=currency_code,
            is_active=True,
            currency__is_active=True,
        )
    except ExchangeRate.DoesNotExist:
        return None
