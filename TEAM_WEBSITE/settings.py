from pathlib import Path
import os
import dj_database_url
from decouple import config
import cloudinary
import cloudinary_storage

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)



# Only force SSL and HSTS if in production

SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY  = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG

X_FRAME_OPTIONS = 'DENY'

SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True


# settings.py

# This splits by comma AND strips away any accidental spaces!
ALLOWED_HOSTS = [host.strip() for host in config("ALLOWED_HOSTS").split(",")]


# Application definition
INSTALLED_APPS = [
   
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',


    'team',
    'rest_framework',
    'members', 
    'widget_tweaks',
    'store',
    'cart',
    'payment',
    'teamAPI',
    'services',
    'cloudinary',
    'cloudinary_storage',
    'import_export',
    'axes',
    

]

MIDDLEWARE = [
    
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

ROOT_URLCONF = 'TEAM_WEBSITE.urls'

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

                 # ---NEWLY ADDED CONTEXT PROCESSOR HERE ---
                'team.context_processors.global_site_context',
                'cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'TEAM_WEBSITE.wsgi.application'


from datetime import timedelta
from django.urls import reverse_lazy

AXES_FAILURE_LIMIT = 3                      # Lock out after  failed attempts
AXES_COOLOFF_TIME = timedelta(minutes=15)    # Lockout lasts 15 minutes
AXES_USE_ATTEMPT_EXPIRATION = True
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]
AXES_LOCKOUT_URL = reverse_lazy('axes-lockout')

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


DATABASES["default"] = dj_database_url.parse(config("DATABASE_URL"))
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
LOGIN_URL = "/accounts/login/"
LOGIN_REDIECT_URL = "/"

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


"""
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
"""



#
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

# 2. Modern Storage (Keep this, it replaces DEFAULT_FILE_STORAGE)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# 3. DELETE these two lines (They conflict with the Cloudinary setup)
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
# MEDIA_URL = 'media/' 
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')




#MEDIA_URL = 'media/' #Path that serves files like photos, videos, mp3 and the likes...
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # This is the filesystem path to the directory conveying the media.

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587        
EMAIL_USE_TLS = True   

# Reading email credentials from .env
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# Reading bank details from .env
BANK_DETAILS = {
    'BANK_NAME': config('BANK_NAME'),
    'ACCOUNT_NUMBER': config('BANK_ACCOUNT_NUMBER'),
    'ACCOUNT_NAME': config('BANK_ACCOUNT_NAME'),
}


# Cloudinary Configuration







import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn= config('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,  # captures performance data (set lower in production if needed)
    send_default_pii=True,   # captures user info (like logged-in user) for debugging
)


