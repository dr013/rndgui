from settings import *

DEBUG = False
AUTH_URL = "http://sv2-web.bt.bpc.in/auth/"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gui',
        'USER': 'gui',
        'PASSWORD': 'gui1',
        'HOST': 'rnd-pg.bt.bpc.in',
        'PORT': '5432',
    }
}

ALLOWED_HOSTS = ["sv2-web.bt.bpc.in", "10.7.33.73"]
INTERNAL_IPS = ["127.0.0.1", '10.7.33.73']
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# Email
EMAIL_HOST = 'bpcrelay1.bpc.in'
DEFAULT_FROM_EMAIL = 'svtools@bpcbt.com'
EMAIL_SUBJECT_PREFIX = '[SVTools] '
EMAIL_HOST_USER = 'svtools'
EMAIL_HOST_PASSWORD = 'R7xdEp3Y'

# Jira
JIRA_URL = 'http://jira.bpc.in:8080'
JIRA_OPTIONS = {
            'server': JIRA_URL,
            'verify': False
        }

# GitLab
GITLAB_URL = 'http://gitlab.bt.bpc.in'
GITLAB_TOKEN = 'SasnDpte7dhAMgNAFPLA'  # RnD Master key

BASE_URL = 'http://sv2.bpc.in/svtools/'

# CELERY STUFF
BROKER_URL = 'redis://sv2-web.bt.bpc.in:6379'
CELERY_RESULT_BACKEND = 'redis://sv2-web.bt.bpc.in:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Jenkins settings
JENKINS_HOST = 'http://jenkins2.bt.bpc.in:8080/'
JENKINS_USER = 'jira-system'
JENKINS_PASS = '3WqOGzrj9G'
JENKINS_BUILD_TASK = 'rnd.core.auto_test.deploy.smart'

SERVICE_HOST = 'http://sv2.bpc.in'

# MongoDB base
DB_MONGO = MONGO_CLIENT['ci']
