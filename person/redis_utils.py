"""
person/redis_utils.py
"""

from django.conf import settings


def get_redis_client():
    try:
        import redis as _redis
    except Exception as ex:
        raise RuntimeError(
            "redis-py package is not installed or failed to import. "
            "Install with: pip install redis. Import error: " + str(ex)
        )
    url = getattr(settings, "REDIS_URL", None)
    if not url:
        # Попытка взять broker_url из Celery как запасной вариант
        try:
            from celery import current_app

            url = current_app.conf.get("broker_url")
        except Exception:
            url = None
    if not url:
        raise RuntimeError(
            "REDIS_URL is not set in Django settings and Celery broker_url not found. "
            "Set REDIS_URL env or in settings.py (e.g. 'redis://host:6379/1')."
        )
    try:
        return _redis.from_url(url, decode_responses=True)
    except Exception as ex:
        raise RuntimeError(f"Failed to create Redis client from URL {url}: {ex}")
