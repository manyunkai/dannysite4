"""
Django settings for dannysite4 project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

from __future__ import unicode_literals

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n-#nl-6m8!!mfh_^jp-wcl)zf8_5^07l+hj_c1j*%$el$!-5gj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

ADMINS = (
    ('admin', 'admin@example.com'),
)


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'ckeditor',

    'comment',
    'user',
    'blog',
    'box',
    'dsite'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.BrowserCheckingMiddleware',
    'core.middleware.AccessLoggingMiddleware'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': (
            'dannysite_web/templates/',
        ),
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request'
            )
        }
    },
]

ROOT_URLCONF = 'dannysite_web.urls'

WSGI_APPLICATION = 'dannysite_web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_DIRS = (
    'dannysite_web/static/',
)

LOGIN_URL = '/auth/login/'

AUTH_USER_MODEL = 'user.User'
AUTHENTICATION_BACKENDS = ('user.backends.AuthenticationBackend',)

ACCOUNT_LOCK_TIME = 30 * 60
ACCOUNT_LOCK_BY_ATTEMPTED_COUNT = 5

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'
TIME_FORMAT = 'H:i:s'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

# sites
SITE_ID = 1

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '../media/'

# CKEditor
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
# CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'cus',
    },
    'basic': {
        'toolbar': 'Basic'
    }
}

# Blog
BLOG_VISITORS_CACHE_KEY = 'blog:{0}:visitors'
BLOG_VISITORS_CACHE_TIMEOUT = 24 * 60 * 60

# OSS options
OSS_OPTIONS = {
    'bucket': '',       # your bucket
    'location': '',     # location prefix
    'base_url': '',     # url prefix when requesting
    'image_process_base_url': '',   # url prefix when requesting processed image
    'image_process_rule': '',   # such as @1e_1c_0o_0l_100h_100w_100q
    'endpoint': '',     # your endpoint
    'access_key': '',   # your access key
    'access_key_secret': ''     # your access key secret
}
