__author__ = 'joseph'


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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0r&z-dj2z6qz4(bm-=w!3^+_!$9yd!)^mtxn3_w@b#tymml1l)'

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


# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
OSCAR_FROM_EMAIL = 'joseph@josephdgallagher.com'
DEFAULT_FROM_EMAIL = "joseph@josephdgallagher.com"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = OSCAR_FROM_EMAIL
EMAIL_HOST_PASSWORD = "joseph#^#"