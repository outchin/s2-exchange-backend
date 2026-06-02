from django.shortcuts import render
from django.http import JsonResponse
from exchange.models import ExchangeRate, Currency


def home(request):
    """Homepage with live exchange rates"""
    return render(request, 'website/home.html')


def about(request):
    """About Us page"""
    return render(request, 'website/about.html')


def contact(request):
    """Contact Us page"""
    return render(request, 'website/contact.html')


def privacy(request):
    """Privacy Policy page"""
    return render(request, 'website/privacy.html')


def exchange_rates_json(request):
    """API endpoint to get exchange rates for the website"""
    rates = ExchangeRate.objects.filter(is_active=True).select_related('currency')

    data = []
    for rate in rates:
        data.append({
            'code': rate.currency.code,
            'name': rate.currency.name,
            'symbol': rate.currency.symbol,
            'buy_rate': float(rate.buy_rate),
            'sell_rate': float(rate.sell_rate),
            'change_percentage': float(rate.change_percentage) if rate.change_percentage else None,
            'last_updated': rate.last_updated.isoformat(),
        })

    return JsonResponse({'rates': data})
