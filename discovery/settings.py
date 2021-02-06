"""
Django settings for discovery project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
import yaml

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"] if "DJANGO_SECRET_KEY" in os.environ else 'suh*#@*8lr59)da9w=8(sdmdz#7_z(yxz&3*i353bi(+j$i*w-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if DEBUG and os.path.exists(BASE_DIR / 'secrets.yml'):
    with open(BASE_DIR / 'secrets.yml') as f:
        addl_config = yaml.full_load(f.read())
    
    assert isinstance(addl_config, dict), f"Additional environment variables invalid: {addl_config}"
    os.environ.update(addl_config)

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'logfile': {
                'class': 'logging.handlers.WatchedFileHandler',
                'filename': '/home/site/wwwroot/app-logs.log',
            },
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['logfile', 'console'],
                'level': 'WARNING',
                'propagate': False,
            }
        }
    }


ALLOWED_HOSTS = [
    # 'discovery-application.azurewebsites.net', # old host
    'dsdiscovery.org',
    'ds-discovery.azurewebsites.net',
    'ds-discovery-staging.azurewebsites.net',
    "127.0.0.1",
]


# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'constance', # constance
    'projects.apps.ProjectsConfig',
    'students.apps.StudentsConfig',
    'applications.apps.ApplicationsConfig',
    'archive.apps.ArchiveConfig',
    'user_profile.apps.UserProfileConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'gmailapi_backend', # for email
    'import_export', # for exporting data
    'flags', # feature flags
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'constance.backends.database', # constance
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'discovery.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = 'discovery.wsgi.application'


# Django Flags
# https://cfpb.github.io/django-flags/

FLAGS = {
    'APPLICATIONS_REVIEWABLE': [],
    'APPLICATIONS_OPEN': [],
    # 'HIDE_PROJECT_APPLICATION_THRESHOLD': [],
}


# Constance (singleton settings in the databse)
# https://django-constance.readthedocs.io/en/latest/index.html

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    "HIDE_PROJECT_APPLICATION_THRESHOLD": (10, "Number of applications at which to hide project", int),
    "SCHOLAR_APP_LIMIT": (9, "Number of applications a Data Scholar can submit", int),
    "APP_LIMIT": (6, "Number of applications any student can submit", int),
    "CURRENT_SEMESTER": ('Spring 2021', "Current semester", str),
}

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'discovery_db',
        #'NAME': 'discoverydb',
        # 'USER': 'postgres',
        'USER': os.environ["DBUSER"] if "DBUSER" in os.environ else "postgres",
        # comment out own password before pushing to master
        'PASSWORD': os.environ["DBPASS"] if "DBPASS" in os.environ else "root",
        #'PASSWORD': "ly13579",
        # 'PASSWORD':,
        # 'HOST': '127.0.0.1',
        'HOST': os.environ["DBHOST"] if "DBHOST" in os.environ else "127.0.0.1",
        'PORT': '5432',
    }
}

# Data import/export
IMPORT_EXPORT_USE_TRANSACTIONS = True


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_MANIFEST_STRICT = True
WHITENOISE_USE_FINDERS = True

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# Email
EMAIL_BACKEND = 'gmailapi_backend.mail.GmailBackend'
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
GMAIL_API_CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID")
GMAIL_API_CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET")
GMAIL_API_REFRESH_TOKEN = os.environ.get("GMAIL_REFRESH_TOKEN")

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# site_id is really weird, check from 1-n to see which one eventually works
SITE_ID = os.environ.get("SITE_ID") if os.environ.get("SITE_ID") is not None else 4

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = None
ACCOUNT_LOGOUT_ON_GET = True #url accounts/logout 
ACCOUNT_USER_DISPLAY = 'user_profile.views.get_user_email'

# ACCOUNT_USER_MODEL_USERNAME_FIELD = 'email'
SOCIALACCOUNT_AUTO_SIGNUP = True

SIGNUP_REDIRECT_URL = '/profile/login/callback'
LOGIN_REDIRECT_URL = '/profile/login/callback'
ACCOUNT_LOGOUT_REDIRECT_URL ='/'

# for login_required decorate
LOGIN_URL = '/profile/login'

SOCIALACCOUNT_ADAPTER = "user_profile.models.CustomSocialAccountAdapter"
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
