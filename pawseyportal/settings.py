"""
Django settings for pawseyportal project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType
from django.core.handlers.wsgi import get_script_name
from django.core.urlresolvers import get_script_prefix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-4jcbzjxpww2du7e$uxut10=k^5ddngsegjvdl3*=0^(lpcg8*'

MYURL = os.environ.get('SCRIPT_NAME','')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ajax_select',
    'pawseyportal.userportal',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'commonware.middleware.ScrubRequestOnException',
)

ROOT_URLCONF = 'pawseyportal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pawseyportal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# LDAP Authentication
AUTH_LDAP_SERVER_URI = "ldap://ldap.example.com"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",
    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=django,ou=groups,dc=example,dc=com",
    ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")
AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=django,ou=groups,dc=example,dc=com"
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

# LDAP User Directory 
USER_LDAP_SERVER = "ldap://ldap.example.com"
USER_LDAP_GROUP = "example"
USER_LDAP_GROUP_BASE = "example"
USER_LDAP_ADMIN_BASE = "example"
USER_LDAP_USER_BASE = "example"


LOGIN_URL = "%s/%s"%(MYURL,'login/')
LOGIN_REDIRECT_URL = "%s/%s"%(MYURL,'pawseyportal/')

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Perth'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = "%s/%s"%(MYURL,'static/')
STATIC_ROOT = "%s/%s"%(BASE_DIR, 'static/')

ADMIN_MEDIA_PREFIX = '/static/admin/'

# Mail settings
SERVER_EMAIL = 'pawseyportal@example.com'
ADMINS = [('Administrator','admins@example.com')]
MANAGERS = [('Manager','managers@example.com')]
EMAIL_HOST = 'localhost'
EMAIL_SUBJECT_PREFIX = '[PawseyPortal] '

# Security settings
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True

# Try to find a custom settings file (rather than changing this one)

try:
    print
    print 'Attepting to import pawseyconfig.pawseyportal if it exists ...',
    from pawseyconfig.pawseyportal import *
    print 'OK'
except Exception, e:
    print 'Fail'
