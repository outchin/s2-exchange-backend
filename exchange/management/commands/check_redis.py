"""
Django management command to verify Redis cache is working.
Usage: python manage.py check_redis
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from exchange.cache import CACHE_KEY_ALL_RATES, get_cached_exchange_rates
import os


class Command(BaseCommand):
    help = 'Verify Redis cache is working and contains data'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("🔍 REDIS CONNECTION TEST"))
        self.stdout.write("=" * 60)

        # Check Redis URL
        redis_url = os.environ.get('REDIS_URL', 'Not set')
        masked_url = redis_url[:50] + "..." if len(redis_url) > 50 else redis_url
        self.stdout.write(f"\n1. REDIS_URL: {masked_url}")

        # Test Django cache connection
        self.stdout.write("\n2. Testing Django cache connection...")
        try:
            cache.set('test_key', 'test_value', timeout=10)
            result = cache.get('test_key')
            if result == 'test_value':
                self.stdout.write(self.style.SUCCESS("   ✅ Django cache is working!"))
            else:
                self.stdout.write(self.style.ERROR("   ❌ Django cache test failed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error: {e}"))

        # Check for exchange rates cache
        self.stdout.write("\n3. Checking exchange rates cache...")
        cached_rates = cache.get(CACHE_KEY_ALL_RATES)
        if cached_rates:
            self.stdout.write(self.style.SUCCESS(f"   ✅ Cache key exists: {CACHE_KEY_ALL_RATES}"))
            self.stdout.write(self.style.SUCCESS(f"   ✅ Number of cached rates: {len(cached_rates)}"))
            if cached_rates:
                first = cached_rates[0]
                self.stdout.write(self.style.SUCCESS(f"   ✅ First rate: {first.get('currency_code')} - {first.get('currency_name')}"))
        else:
            self.stdout.write(self.style.WARNING(f"   ⚠️  Cache key not found: {CACHE_KEY_ALL_RATES}"))
            self.stdout.write("   This is normal if no API/WebSocket requests have been made yet")

        # Test getting rates (should populate cache)
        self.stdout.write("\n4. Testing cache population...")
        rates = get_cached_exchange_rates()
        self.stdout.write(self.style.SUCCESS(f"   ✅ Retrieved {len(rates)} rates from get_cached_exchange_rates()"))

        # Verify cache was populated
        cached_after = cache.get(CACHE_KEY_ALL_RATES)
        if cached_after:
            self.stdout.write(self.style.SUCCESS(f"   ✅ Cache now populated with {len(cached_after)} rates"))
            for rate in cached_after:
                self.stdout.write(f"      - {rate.get('currency_code')}: Buy {rate.get('buy_rate')}, Sell {rate.get('sell_rate')}")
        else:
            self.stdout.write(self.style.ERROR("   ❌ Cache still empty after get_cached_exchange_rates()"))

        # Try to connect to Redis directly using redis-py
        self.stdout.write("\n5. Testing direct Redis connection...")
        try:
            import redis
            redis_url = settings.REDIS_URL
            r = redis.from_url(redis_url)
            r.ping()
            self.stdout.write(self.style.SUCCESS("   ✅ Direct Redis connection successful (PING received PONG)"))

            # Get all keys
            keys = r.keys('s2exchange:*')
            self.stdout.write(self.style.SUCCESS(f"   ✅ Found {len(keys)} keys with prefix 's2exchange:'"))
            for key in keys:
                key_name = key.decode('utf-8')
                self.stdout.write(f"      - {key_name}")

                # Try to get the key value
                try:
                    value = r.get(key)
                    if value:
                        self.stdout.write(f"        Size: {len(value)} bytes")
                except Exception as e:
                    self.stdout.write(f"        Error reading: {e}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Direct Redis connection failed: {e}"))

        # Test cache invalidation
        self.stdout.write("\n6. Testing cache invalidation...")
        try:
            from exchange.cache import invalidate_exchange_rates_cache
            invalidate_exchange_rates_cache()
            self.stdout.write(self.style.SUCCESS("   ✅ Cache invalidation successful"))

            # Check if cache is actually empty
            check = cache.get(CACHE_KEY_ALL_RATES)
            if check is None:
                self.stdout.write(self.style.SUCCESS("   ✅ Cache key successfully removed"))
            else:
                self.stdout.write(self.style.WARNING("   ⚠️  Cache key still exists after invalidation"))

            # Re-populate
            rates = get_cached_exchange_rates()
            self.stdout.write(self.style.SUCCESS(f"   ✅ Cache re-populated with {len(rates)} rates"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Cache invalidation test failed: {e}"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SUMMARY:"))
        self.stdout.write("=" * 60)
        if cached_after:
            self.stdout.write(self.style.SUCCESS("✅ Redis caching is WORKING!"))
            self.stdout.write(self.style.SUCCESS(f"✅ {len(cached_after)} exchange rates cached"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Redis cache is empty"))
            self.stdout.write("   Run get_cached_exchange_rates() or make an API request to populate")
        self.stdout.write("=" * 60)
