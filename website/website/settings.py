"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from oscar.defaults import *
from oscar import OSCAR_MAIN_TEMPLATE_DIR


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0r&z-dj2z6qz4(bm-=w!3^+_!$9yd!)^mtxn3_w@b#tymml1l)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = True

ALLOWED_HOSTS = ['*']

OSCAR_SHOP_NAME = 'SAII TEST'
OSCAR_DEFAULT_CURRENCY = 'USD'

STRIPE_SECRET_KEY = "sk_test_AwJVJOGHQEbQujjfL5NRQqGg"
STRIPE_PUBLISHABLE_KEY = "pk_test_2iglUrpb6YKX2uzV46WLoBnM"
STRIPE_CURRENCY = "USD"

DATACASH_HOST = 'testserver.datacash.com'
DATACASH_CLIENT = '...'
DATACASH_PASSWORD = '...'
DATACASH_CURRENCY = 'USD'

# PAYPAL_API_USERNAME = 'uhhhmmm-facilitator_api1.gmail.com'
# PAYPAL_API_PASSWORD = 'VWJHPBEBR8Z34RCT'
# PAYPAL_API_SIGNATURE = 'AFcWxV21C7fd0v3bYYYRCpSSRl31ArxgHzKe2jfF6SSUgastSMhqTeJL'

# Application definition

from oscar import get_core_apps

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'compressor',
    'widget_tweaks',
    'datacash',
    'website.apps.quotation',
    'easy_pdf',
    'corsheaders',
    # 'paypal',
] + get_core_apps(['website.apps.checkout', 'website.apps.payment'])


SITE_ID = 1

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
OSCAR_FROM_EMAIL = 'joseph@josephdgallagher.com'
DEFAULT_FROM_EMAIL = "joseph@josephdgallagher.com"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = OSCAR_FROM_EMAIL
EMAIL_HOST_PASSWORD = "joseph#^#"

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'website.urls'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), '', x)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            location('templates'),
            OSCAR_MAIN_TEMPLATE_DIR
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
            ],
        },
    },
]


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)


WSGI_APPLICATION = 'website.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'ATOMIC_REQUESTS': True,
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
#         },
#         'simple': {
#             'format': '[%(asctime)s] %(message)s'
#         },
#     },
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'handlers': {
#         'null': {
#             'level': 'DEBUG',
#             'class': 'django.utils.log.NullHandler',
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         },
#         'checkout_file': {
#             'level': 'INFO',
#             'class': 'oscar.core.logging.handlers.EnvFileHandler',
#             'filename': 'checkout.log',
#             'formatter': 'verbose'
#         },
#         'gateway_file': {
#             'level': 'INFO',
#             'class': 'oscar.core.logging.handlers.EnvFileHandler',
#             'filename': 'gateway.log',
#             'formatter': 'simple'
#         },
#         'error_file': {
#             'level': 'INFO',
#             'class': 'oscar.core.logging.handlers.EnvFileHandler',
#             'filename': 'errors.log',
#             'formatter': 'verbose'
#         },
#         'sorl_file': {
#             'level': 'INFO',
#             'class': 'oscar.core.logging.handlers.EnvFileHandler',
#             'filename': 'sorl.log',
#             'formatter': 'verbose'
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#             'filters': ['require_debug_false'],
#         },
#     },
#     'loggers': {
#         # Django loggers
#         'django': {
#             'handlers': ['null'],
#             'propagate': True,
#             'level': 'INFO',
#         },
#         'django.request': {
#             'handlers': ['mail_admins', 'error_file'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         'django.db.backends': {
#             'handlers': ['null'],
#             'propagate': False,
#             'level': 'DEBUG',
#         },
#         # Oscar core loggers
#         'oscar.checkout': {
#             'handlers': ['console', 'checkout_file'],
#             'propagate': False,
#             'level': 'INFO',
#         },
#         'oscar.catalogue.import': {
#             'handlers': ['console'],
#             'propagate': False,
#             'level': 'INFO',
#         },
#         'oscar.alerts': {
#             'handlers': ['null'],
#             'propagate': False,
#             'level': 'INFO',
#         },
#         # Sandbox logging
#         'gateway': {
#             'handlers': ['gateway_file'],
#             'propagate': True,
#             'level': 'INFO',
#         },
#         # Third party
#         'sorl.thumbnail': {
#             'handlers': ['sorl_file'],
#             'propagate': True,
#             'level': 'INFO',
#         },
#         # Suppress output of this debug toolbar panel
#         'template_timings_panel': {
#             'handlers': ['null'],
#             'level': 'DEBUG',
#             'propagate': False,
#         }
#     }
# }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

print MEDIA_ROOT


STATIC_ROOT = os.path.join(BASE_DIR, "static/")

OSCAR_MISSING_IMAGE_URL = MEDIA_URL + 'image_not_found.jpg'

#Cross origin stuff
CORS_ORIGIN_WHITELIST = (
    'localhost:8000',
    'localhost/',
)

CORS_ORIGIN_ALLOW_ALL = True
