"""
Development settings for DjangoArchitectAPI.

Включает дополнительные инструменты для разработки и отладки.
"""

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

try:
    import django_extensions
    INSTALLED_APPS += ['django_extensions']
except ImportError:
    pass

try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass

# Database - для разработки можно использовать SQLite
if config('USE_SQLITE', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if config('DISABLE_CACHE', default=False, cast=bool):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

LOGGING['root']['level'] = 'INFO'
if config('DEBUG_SQL', default=False, cast=bool):
    LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'

# Shell Plus configuration
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = True

# Django Extensions
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}
