release: python manage.py migrate --noinput && python manage.py create_default_superuser && python manage.py seed_exchange_data
web: daphne -b 0.0.0.0 -p $PORT s2exchange_api.asgi:application
