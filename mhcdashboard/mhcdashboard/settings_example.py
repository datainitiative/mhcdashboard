"""
Django settings for mhcdashboard project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.contrib import messages
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '21(j#c2-nhio$)qb#ng*_j%v^=es_ufwj^l5sfv_xoa7wj4g*h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Template
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]


# Application definition

INSTALLED_APPS = (
    'bootstrap3',
    'django_admin_bootstrapped',
    'smart_selects',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mhcdashboardapp'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mhcdashboard.urls'

WSGI_APPLICATION = 'mhcdashboard.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mhcdashboard',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',#'/opt/bitnami/postgresql' for aws
        'PORT': '5432'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

ROOT_APP_URL = '/mhcdashboard' # use this for localhost
#ROOT_APP_URL = '/mhcdashboard/mhcdashboard' # use this for server

ADMIN_ROOT_URL = '' # use this for localhost
#ADMIN_ROOT_URL = '/mhcdashboard' # use this for server

STATIC_ROOT_URL = '/mhcdashboard'
STATIC_URL = '%s/static/' % STATIC_ROOT_URL

# use this for localhost
SOTRAGE_ROOTPATH = 'C:/QLiu/ql_dj/apps/MHC_dashboard/mhcdashboard/mhcdashboardapp/static/data/'
# use this for server
#SOTRAGE_ROOTPATH = '/home/bitnami/apps/django/django_projects/mhc_dashboard/mhcdashboard/mhcdashboardapp/static/data/'

# Login URL
LOGIN_URL = '/admin/login/' # use this for localhost
#LOGIN_URL = '/mhcdashboard/admin/login/'

# Use Bootstrap3 for Django
## Bootstrap3 config dict
BOOTSTRAP3 = {
    # The URL to the jQuery JavaScript file
    'jquery_url': '//code.jquery.com/jquery.min.js',

    # The Bootstrap base URL
    'base_url': '//netdna.bootstrapcdn.com/bootstrap/3.3.1/',

    # The complete URL to the Bootstrap CSS file (None means derive it from base_url)
    'css_url': None,

    # The complete URL to the Bootstrap CSS file (None means no theme)
    'theme_url': None,

    # The complete URL to the Bootstrap JavaScript file (None means derive it from base_url)
    'javascript_url': None,

    # Put JavaScript in the HEAD section of the HTML document (only relevant if you use bootstrap3.html)
    'javascript_in_head': False,

    # Include jQuery with Bootstrap JavaScript (affects django-bootstrap3 template tags)
    'include_jquery': False,

    # Label class to use in horizontal forms
    'horizontal_label_class': 'col-md-2',

    # Field class to use in horizontal forms
    'horizontal_field_class': 'col-md-4',

    # Set HTML required attribute on required fields
    'set_required': True,

    # Set placeholder attributes to label if no placeholder is provided
    'set_placeholder': True,

    # Class to indicate required (better to set this in your Django form)
    'required_css_class': '',

    # Class to indicate error (better to set this in your Django form)
    'error_css_class': 'has-error',

    # Class to indicate success, meaning the field has valid input (better to set this in your Django form)
    'success_css_class': 'has-success',

    # Renderers (only set these if you have studied the source and understand the inner workings)
    'formset_renderers':{
        'default': 'bootstrap3.renderers.FormsetRenderer',
    },
    'form_renderers': {
        'default': 'bootstrap3.renderers.FormRenderer',
    },
    'field_renderers': {
        'default': 'bootstrap3.renderers.FieldRenderer',
        'inline': 'bootstrap3.renderers.InlineFieldRenderer',
    },
}


## Custom rendere for fields using Bootstrap3
DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'
### Custom admin messages - Add Bootstrap3 tags for messages (tag:"alert-info")
MESSAGE_TAGS = {
    messages.SUCCESS: 'alert-success success',
    messages.WARNING: 'alert-warning warning',
    messages.ERROR: 'alert-danger error'
}