"""
Django settings for ecommerce project.

Generated by 'django-admin startproject' using Django 5.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import os
from decouple import config
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^$tq__n+dv6(@fbjm1j^i1)_epbyl=!9k-qvlv=pp666ow9(z+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # my installed appps
    'users.apps.UsersConfig',
    'base.apps.BaseConfig',
    'widget_tweaks',
    'django_countries',
    'django.contrib.humanize',  # For natural time formatting
    # 'phonenumber_field',
    'about.apps.AboutConfig',
    'blog.apps.BlogConfig',
    'shop.apps.ShopConfig',
    'contacts.apps.ContactsConfig',
    'payments.apps.PaymentsConfig',
    'policy.apps.PolicyConfig',
    'newsletter.apps.NewsletterConfig',
    'wishlist.apps.WishlistConfig',


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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

WSGI_APPLICATION = 'ecommerce.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    # 'default': dj_database_url.config(default=os.getenv('DATABASE_URL'), conn_max_age=600)
    'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3'
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR / 'static'),)
STATIC_ROOT = os.path.join(BASE_DIR / 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR / 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# settings for custom user
AUTH_USER_MODEL = 'users.CustomUser'
LOGOUT_REDIRECT_URL = 'base:index'  # Redirect to 'home' after logout

# email verification fileds
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or smtp.mailgun.org
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mceemoney1@gmail.com'
EMAIL_HOST_PASSWORD = config('EMAIL_APP_PASSWORD')
DEFAULT_FROM_EMAIL = 'mceemoney1@gmail.com'
SITE_URL = '#'  # For confirmation links
SITE_NAME = 'Vege Grocer'  # Used in emails

PASSWORD_RESET_TIMEOUT = 14400

PHONENUMBER_DEFAULT_REGION = 'KE'  # Kenya
PHONENUMBER_DB_FORMAT = 'E164'

# from dotenv import load_dotenv
# load_dotenv()
# FIELD_ENCRYPTION_KEY = os.environ['FIELD_ENCRYPTION_KEY']


# stripe payments API test key
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY')

# models field encryption 
FIELD_ENCRYPTION_KEY = config('FIELD_ENCRYPTION_KEY')

# upload storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'