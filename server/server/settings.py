"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os

from pathlib import Path
from datetime import timedelta
from invoke import run
from django.core.exceptions import ImproperlyConfigured


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.environ.get("SECRET_KEY"))
OPENAI_API_KEY = str(os.environ.get("OPENAI_API_KEY"))

MYSQL_USER = str(os.getenv("MYSQL_USER"))
MYSQL_PASSWORD = str(os.getenv("MYSQL_PASSWORD"))
MYSQL_NAME = str(os.getenv("MYSQL_NAME"))
MYSQL_HOST = str(os.getenv("MYSQL_HOST"))
MYSQL_PORT = str(os.getenv("MYSQL_PORT"))


ELASTICSEARCH_PORT = str(os.getenv("ELASTICSEARCH_PORT"))
ELASTICSEARCH_HOST = str(os.getenv("ELASTICSEARCH_HOST"))
ELASTICSEARCH_USER = str(os.getenv("ELASTICSEARCH_USER"))
ELASTICSEARCH_PASSWORD = str(os.getenv("ELASTICSEARCH_PASSWORD"))

EMAIL_HOST = str(os.getenv("EMAIL_HOST"))
EMAIL_PORT = str(os.getenv("EMAIL_PORT"))
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = str(os.getenv("EMAIL_HOST_USER"))
EMAIL_HOST_PASSWORD = str(os.getenv("EMAIL_HOST_PASSWORD"))
EMAIL_BACKEND = str(os.getenv("EMAIL_BACKEND"))
DEFAULT_FROM_EMAIL = str(os.getenv("EMAIL_HOST_USER"))


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG") == "true"


ALLOWED_HOSTS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOWED_ORIGINS = ["http://localhost:4174", "http://127.0.0.1:4174"]


X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app.apps.AppConfig",
    "drf_spectacular",
    "corsheaders",
    "phonenumber_field",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(SETTINGS_PATH, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


DATABASE_PATH = os.path.join(BASE_DIR, "db.sqlite3")

PRIMARY_DB = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": MYSQL_NAME,
    "USER": MYSQL_USER,
    "PASSWORD": MYSQL_PASSWORD,
    "HOST": MYSQL_HOST,
    "PORT": MYSQL_PORT,
}

FALLBACK_DB = {"ENGINE": "django.db.backends.sqlite3", "NAME": DATABASE_PATH}


# try:
#     DATABASES = {'default': PRIMARY_DB}
#     if not PRIMARY_DB['NAME'] or not PRIMARY_DB['USER']:
#         raise ImproperlyConfigured(
#             'Missing MySQL configuration. Falling back to SQLite.'
#         )
# except ImproperlyConfigured:
#     # run(f"docker-compose run server pipenv run python3 manage.py makemigrations")
#     run(f"docker-compose run server pipenv run python3 manage.py migrate")
DATABASES = {"default": FALLBACK_DB}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "app.User"


CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 15,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "AudQL API Documentation",
    "DESCRIPTION": "This is the official documentation for the AudQL backend",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

CopySTATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


ELASTICSEARCH_DSL = {
    "default": {
        "hosts": f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}",
        "http_auth": (ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
    }
}
