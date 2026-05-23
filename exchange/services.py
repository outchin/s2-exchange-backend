from django.conf import settings


def sync_rate_to_realtime_database(rate):
    if not settings.FIREBASE_DATABASE_URL or not settings.FIREBASE_SERVICE_ACCOUNT_PATH:
        return {
            'synced': False,
            'reason': 'Firebase settings are not configured.',
        }

    try:
        import firebase_admin
        from firebase_admin import credentials, db
    except ImportError:
        return {
            'synced': False,
            'reason': 'firebase-admin package is not installed.',
        }

    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': settings.FIREBASE_DATABASE_URL,
        })

    path = f'{settings.FIREBASE_RATES_PATH}/{rate.currency.code}'
    db.reference(path).set(rate.to_api_dict())
    return {
        'synced': True,
        'path': path,
        'currency_code': rate.currency.code,
    }
