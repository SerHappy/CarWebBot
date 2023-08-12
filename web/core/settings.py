"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from .loguru_setup import setup_logger
from decouple import config
from dj_easy_log import load_loguru
from pathlib import Path

import os


# --------------------------------
# BASE PATHS AND URLS
# --------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
LOGIN_URL = config("LOGIN_URL", cast=str, default="/users/login/")
TMP_STORAGE_PATH = os.path.join(BASE_DIR, "tmp/")

# --------------------------------
# SECURITY SETTINGS
# --------------------------------
SECRET_KEY = config("SECRET_KEY", cast=str)
DEBUG = config("DEBUG", cast=bool, default=True)
ALLOWED_HOSTS: list[str] = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default="127.0.0.1",
)
if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]

# --------------------------------
# AUTHENTICATION SETTINGS
# --------------------------------
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["apps.users.backends.EmailBackend"]

# --------------------------------
# APPLICATION AND MIDDLEWARE SETTINGS
# --------------------------------
INSTALLED_APPS = [
    "debug_toolbar",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.announcement",
    "apps.tag",
    "apps.users",
    "apps.bot",
    "apps.settings",
]
MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# --------------------------------
# URL AND WSGI SETTINGS
# --------------------------------
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# --------------------------------
# TEMPLATE SETTINGS
# --------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates/")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# --------------------------------
# DATABASE SETTINGS
# --------------------------------
DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", cast=str, default="django.db.backends.mysql"),
        "NAME": config("DB_NAME", cast=str, default="cars"),
        "USER": config("DB_USER", cast=str, default="root"),
        "PASSWORD": config("DB_PASSWORD", cast=str, default="root"),
        "HOST": config("DB_HOST", cast=str, default="localhost"),
        "PORT": config("DB_PORT", cast=int, default="3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

# --------------------------------
# PASSWORD VALIDATION SETTINGS
# --------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# --------------------------------
# INTERNATIONALIZATION SETTINGS
# --------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------
# CELERY SETTINGS
# --------------------------------
CELERY_BROKER_URL = config("CELERY_BROKER_URL", cast=str, default="redis://localhost:6379")
CELERY_TIMEZONE = "UTC"

# --------------------------------
# STATIC FILES SETTINGS
# --------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/")]
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# --------------------------------
# DEFAULT FIELD TYPE SETTINGS
# --------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------
# PAGINATION SETTINGS
# --------------------------------
ANNOUNCEMENT_LIST_PER_PAGE = config("ANNOUNCEMENT_LIST_PER_PAGE", cast=int, default=5)
TAG_LIST_PER_PAGE = config("TAG_LIST_PER_PAGE", cast=int, default=10)

# --------------------------------
# TELEGRAM SETTINGS
# --------------------------------
MAIN_CHANNEL_ID = config("MAIN_CHANNEL_ID", cast=int)
MAIN_CHANNEL_NAME = config("MAIN_CHANNEL_NAME", cast=str)

# --------------------------------
# TELETHON SETTINGS
# --------------------------------
TELETHON_API_ID = config("TELETHON_API_ID", cast=int)
TELETHON_API_HASH = config("TELETHON_API_HASH", cast=str)
TELETHON_SESSION_NAME = os.path.join(BASE_DIR.parent, config("TELETHON_SESSION_NAME", cast=str, default="session"))
TELETHON_SYSTEM_VERSION = config("TELETHON_SYSTEM_VERSION", cast=str, default="4.16.30-vxCUSTOM")

# --------------------------------
# LOGGER SETTINGS
# --------------------------------
LOGURU_FOLDER = os.path.join(BASE_DIR.parent, config("LOGURU_FOLDER", cast=str, default="logs/"))
LOGURU_LEVEL = config("LOGURU_LEVEL", cast=str, default="INFO")
LOGURU_FORMAT = config("LOGURU_FORMAT", cast=str, default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
load_loguru(globals(), configure_func=setup_logger)
