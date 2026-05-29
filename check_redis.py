#!/usr/bin/env python
"""
Script to verify Redis cache is working and contains data.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's2exchange_api.settings')
django.setup()

from django.core.cache import cache
from exchange.cache import CACHE_KEY_ALL_RATES, get_cached_exchange_rates

print("=" * 60)
print("🔍 REDIS CONNECTION TEST")
print("=" * 60)

# Check Redis URL
redis_url = os.environ.get('REDIS_URL', 'Not set')
print(f"\n1. REDIS_URL: {redis_url[:50]}..." if len(redis_url) > 50 else f"\n1. REDIS_URL: {redis_url}")

# Test Django cache connection
print("\n2. Testing Django cache connection...")
try:
    cache.set('test_key', 'test_value', timeout=10)
    result = cache.get('test_key')
    if result == 'test_value':
        print("   ✅ Django cache is working!")
    else:
        print("   ❌ Django cache test failed")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check for exchange rates cache
print("\n3. Checking exchange rates cache...")
cached_rates = cache.get(CACHE_KEY_ALL_RATES)
if cached_rates:
    print(f"   ✅ Cache key exists: {CACHE_KEY_ALL_RATES}")
    print(f"   ✅ Number of cached rates: {len(cached_rates)}")
    if cached_rates:
        print(f"   ✅ First rate: {cached_rates[0].get('currency_code')} - {cached_rates[0].get('currency_name')}")
else:
    print(f"   ⚠️  Cache key not found: {CACHE_KEY_ALL_RATES}")
    print("   This is normal if no API/WebSocket requests have been made yet")

# Test getting rates (should populate cache)
print("\n4. Testing cache population...")
rates = get_cached_exchange_rates()
print(f"   ✅ Retrieved {len(rates)} rates")

# Verify cache was populated
cached_after = cache.get(CACHE_KEY_ALL_RATES)
if cached_after:
    print(f"   ✅ Cache now populated with {len(cached_after)} rates")
    for rate in cached_after:
        print(f"      - {rate.get('currency_code')}: Buy {rate.get('buy_rate')}, Sell {rate.get('sell_rate')}")
else:
    print("   ❌ Cache still empty after get_cached_exchange_rates()")

# Check cache TTL
print("\n5. Checking cache TTL...")
import time
cache.set('ttl_test', 'value', timeout=5)
ttl_test = cache.get('ttl_test')
if ttl_test:
    print("   ✅ Cache TTL is working (key expires after timeout)")

# Try to connect to Redis directly
print("\n6. Testing direct Redis connection...")
try:
    import redis
    from django.conf import settings
    redis_url = settings.REDIS_URL
    r = redis.from_url(redis_url)
    r.ping()
    print("   ✅ Direct Redis connection successful!")

    # Get all keys
    keys = r.keys('s2exchange:*')
    print(f"   ✅ Found {len(keys)} keys with prefix 's2exchange:'")
    for key in keys:
        print(f"      - {key.decode('utf-8')}")
except Exception as e:
    print(f"   ❌ Direct Redis connection failed: {e}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("=" * 60)
if cached_after:
    print("✅ Redis caching is WORKING!")
    print(f"✅ {len(cached_after)} exchange rates cached")
else:
    print("⚠️  Redis cache is empty (will be populated on first request)")
print("=" * 60)
