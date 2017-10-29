# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from decouple import config


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG",default=True,cast=bool)

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # my app modules
    'question',
    'assignment',
    'onlinetest',
    'account',
    'appglobal',
)

LOGIN_URL = '/accounts/login/'

LOGIN_EXEMPT_URLS = (
 r'^about/$',
 r'^admin/',
r'^accounts/login/',
 r'^accounts/logout/',
 # allow any URL under /legal/*
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # custom middleware
    'apassite.middleware.LoginRequiredMiddleware',
)


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

ROOT_URLCONF = 'apassite.urls'

WSGI_APPLICATION = 'apassite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'djangodb',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'root',
        'PASSWORD': 'admin',
        'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '3306',                      # Set to empty string for default.
    }
}
"""

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = config("TIME_ZONE")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR,'static'),
)
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)

MEDIA_ROOT=os.path.join(BASE_DIR,'media')

MEDIA_URL='/media/'

TEMPLATE_CONTEXT_PROCESSORS=("django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.contrib.messages.context_processors.messages",
'django.core.context_processors.request',
'account.processors.user_fullname',
)

SESSION_COOKIE_AGE=216000

# custom settings
DEFAULT_SUMMARIZER_CLASS="appglobal.summarizers.ListObjectSummarizer"

LOGIN_EXEMPT_URLNAMES=['user_login','user_logout',#account
                       'index','about',#appglobal
                       ]
STAFF_EXEMPT_URLNAMES=['change_password',#account
                       'home',#appglobal
                       "assignment_question_list",
                       "assignment_assignment_question_submission_view",
                       "assignment_submission_list_student",
                       "assignment_submission_view",
                       "assignment_file_download",
                       "assignment_submission_report",
                       "question_file_download",#assignment
                       "online_test_list_student",
                       "online_test_submission_create",
                       "online_test_submission_list_student",
                       "online_test_submission_view_student",
                       "onlinetest_file_download",
                       "online_test_get_endtime",
                       "online_test_test_compilation"#onlinetest
                       ]


INSTRUCTION_FILE_RELATIVE_PATH={
    "onlinetest":'instruction/onlinetest',
    "assignment":"instruction/assignment",
    "question":"instruction/question"
}

URLS_ALLOWED_IN_TEST=[
    "home",
    "user_logout",
    "user_login",
    "test_compilation_student",
    "onlinetest_file_download",
    "question_file_download",
    "online_test_submission_create",
    "online_test_submission_end_student",
]