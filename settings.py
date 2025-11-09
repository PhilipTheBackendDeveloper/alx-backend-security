MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # ✅ Custom IP blocking middleware
    'ip_tracking.middleware.IPBlockMiddleware',
]

# Add to INSTALLED_APPS
INSTALLED_APPS += [
    "ip_tracking",
    "ratelimit",  # django-ratelimit
    # "ipgeolocation",  # if you installed django-ipgeolocation and configured it
]

# Middleware — add our middleware at the end (after sessions/auth)
MIDDLEWARE += [
    "ip_tracking.middleware.IPBlockMiddleware",
]

# Simple cache config (use Redis in production)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ipgeo-cache",
    }
}
# If you have Redis:
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
#     }
# }

# Geolocation service config (optional). Use 'ipapi' fallback (no API key needed)
IP_GEOLOCATION_CACHE_TTL = 60 * 60 * 24  # 24 hours
IP_GEO_SERVICE = "ipapi"  # or name of provider you plan to use

# Celery configuration (example using Redis broker)
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_BEAT_SCHEDULE = {
    # run anomaly detection every hour
    "ip-anomaly-detection-hourly": {
        "task": "ip_tracking.tasks.detect_suspicious_ips",
        "schedule": 3600.0,  # seconds
    },
}

# Logging snippet (ensure the ip_tracking logger prints warnings)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "ip_tracking": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

