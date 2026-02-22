"""
Django settings for threeddocs project.
"""

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

_secret_key_default = 'django-insecure-bko0r!gj^#a&1lefs01+n^lkfbd0_zet5p^8*7wx#w8_twxy04'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', _secret_key_default if DEBUG else None)
if not SECRET_KEY:
    raise RuntimeError(
        'DJANGO_SECRET_KEY environment variable must be set when DEBUG=False.'
    )

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'authentication',
    'projects',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'threeddocs.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'threeddocs.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

_db_name = os.environ.get('POSTGRES_DB')
if _db_name:
    _db_password = os.environ.get('POSTGRES_PASSWORD')
    if not _db_password:
        raise RuntimeError('POSTGRES_PASSWORD environment variable must be set.')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _db_name,
            'USER': os.environ.get('POSTGRES_USER', 'postgres'),
            'PASSWORD': _db_password,
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

APPEND_SLASH = False

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'authentication.backends.CookieJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173',
).split(',')
CORS_ALLOW_CREDENTIALS = True

# JWT cookie names
ACCESS_TOKEN_COOKIE = 'access_token'
REFRESH_TOKEN_COOKIE = 'refresh_token'

# Cookie security settings
JWT_COOKIE_HTTPONLY = True
JWT_COOKIE_SAMESITE = 'Lax'
JWT_COOKIE_SECURE = not DEBUG  # True in production (HTTPS)

# SimpleJWT token lifetimes
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173',
).split(',')

