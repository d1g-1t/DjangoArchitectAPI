"""
Development settings for DjangoArchitectAPI.

Включает дополнительные инструменты для разработки и отладки.
"""

from .base import *

# Development mode
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development apps
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# Development middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug Toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
]

# Database - для разработки можно использовать SQLite
if config('USE_SQLITE', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Email backend для разработки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache - можно отключить для разработки
if config('DISABLE_CACHE', default=False, cast=bool):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Logging level для разработки
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'

# Shell Plus configuration
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = True

# Django Extensions
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}
