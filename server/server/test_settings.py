import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-audql-unit-tests-only")

from .settings import *

SECRET_KEY = "test-secret-key-for-audql-unit-tests-only"
SIMPLE_JWT = {**SIMPLE_JWT, "SIGNING_KEY": SECRET_KEY}
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
ELASTICSEARCH_ENABLED = False
ELASTICSEARCH_URL = "http://localhost:9200"
MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE
    if middleware != "whitenoise.middleware.WhiteNoiseMiddleware"
]

DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "audql-test-cache",
        "TIMEOUT": 300,
    }
}
