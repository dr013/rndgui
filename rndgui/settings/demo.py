from settings import *

DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ["127.0.0.1", '10.7.32.91', ]

AUTH_URL = "http://sv2-web.bt.bpc.in/auth/"

ALLOWED_HOSTS = ["sv2.bpc.in", "127.0.0.1", "localhost", ]

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'guidev',
        'USER': 'guidev',
        'PASSWORD': 'guidev1',
        'HOST': 'rnd-pg.bt.bpc.in',
        'PORT': '5432',
    }
}

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]

# Jira
JIRA_URL = 'http://jira.bpc.in:8080'
JIRA_OPTIONS = {
    'server': JIRA_URL,
    'verify': False
}

# GitLab
GITLAB_URL = 'http://gitlab.bt.bpc.in'
GITLAB_TOKEN = 'SasnDpte7dhAMgNAFPLA'  # RnD Master key

# Email
EMAIL_HOST = 'bpcrelay1.bpc.in'
DEFAULT_FROM_EMAIL = 'svtools@bpcbt.com'
EMAIL_SUBJECT_PREFIX = '[SVTools] '
EMAIL_HOST_USER = 'svtools'
EMAIL_HOST_PASSWORD = 'R7xdEp3Y'

BASE_URL = 'http://sv2.bpc.in/svtools/'

# CELERY STUFF
BROKER_URL = 'redis://sv2.bpc.in:6379'
CELERY_RESULT_BACKEND = 'redis://sv2.bpc.in:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Jenkins settings
JENKINS_HOST = 'http://jenkins2.bt.bpc.in:8080/'
JENKINS_USER = 'jira-system'
JENKINS_PASS = '3WqOGzrj9G'
JENKINS_BUILD_TASK = 'test.host.deploy'
