"""
Django settings for cmdb project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
import logging
import datetime

# import ldap
# from django_auth_ldap.config import LDAPSearch


logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sma!&$c$t+qojc^8wt(&l=zow)pnt48*swk)79=jndngc1x@0x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'search.apps.SearchConfig',
    'data.apps.DataConfig',
    'record_data.apps.RecordDataConfig',
    'deleted_data.apps.DeletedDataConfig',
    'mgmt.apps.MgmtConfig',
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'perm',
    'corsheaders',
    'django_filters',
]

MIDDLEWARE = [
    "common.disable_csrf.DisableCSRFCheck",
    # 'utils.middleware.ExceptionMiddleware',
    'mgmt.middleware.InitDynamicTableApiMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cmdb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'cmdb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': "cmdb",
    "HOST": "192.168.2.241",
    "PORT": 3306,
    "USER": "cmdb",
    "PASSWORD": "123456",
    'OPTIONS': {
      'charset': 'utf8mb4',
      'use_unicode': True,
    },
  }
}


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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]

# STATIC_ROOT = os.path.join(BASE_DIR, "static")

AUTH_USER_MODEL = "mgmt.User"

# 权限缓存时间（s） 0 代表不缓存
PERMISSION_CACHE_TIME = 60


AUTHENTICATION_BACKENDS = [
    # 'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
# AUTH_LDAP_SERVER_URI = "ldap://192.168.1.203:389"
# AUTH_LDAP_CONNECTION_OPTIONS = {
#     ldap.OPT_REFERRALS: 0
# }
# AUTH_LDAP_BIND_DN = "cn=Manager,dc=hbgd,dc=com"
# AUTH_LDAP_BIND_PASSWORD = "tmm******"
# # AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=sales,dc=hbgd,dc=com"
# AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=sales,dc=hbgd,dc=com",
#                                    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# AUTH_LDAP_USER_ATTR_MAP = {
#     "first_name": "givenName",
#     "last_name": "sn",
#     "email": "mail"
# }

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_METADATA_CLASS': 'utils.metadata.NoPermissionMetadata',
    'DEFAULT_FILTER_BACKENDS': (
        'utils.backends.MySearchFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
    )
}

JWT_AUTH = {
    "JWT_EXPIRATION_DELTA": datetime.timedelta(days=7),
}

ELASTICSEARCH = {
    # "hosts": ["http://192.168.10.204:9200"],
    "hosts": ["http://117.33.233.74:9200"],
    "username": "elastic",  # 貌似无用
    # "user": "cmdb",
    "password": "wonders,1",  # 貌似无用
    "index_map": {
        "data": "data",
        "record_data": "record_data",
        "deleted_data": "deleted_data"
    }
}

# 网站URL
SITE_URL = "http://cmdb.mingmingt.xyz"

# 发送邮件邮箱设置
SEND_EMAIL = 'mmt_cmdb@163.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'  # SMTP地址 例如: smtp.163.com
EMAIL_PORT = 25  # SMTP端口 例如: 25
EMAIL_HOST_USER = SEND_EMAIL  # 例如: xxxxxx@163.com
EMAIL_HOST_PASSWORD = 'cmdb1234'  # 邮箱授权码
EMAIL_SUBJECT_PREFIX = u'django'  # 为邮件Subject-line前缀,默认是'[django]'
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10

# 验证码过期时间（秒）
MAX_AGE = 10 * 60


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'    #日志格式
        }
    },
    'filters': {
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/default.log',              #日志输出文件
            'maxBytes': 1024*1024*10,                   #文件最大大小
            'backupCount': 5,                           #备份份数
            'encoding': 'utf-8',                        #日志编码格式
            'formatter': 'standard',                    #使用哪种formatters日志格式
        },
        'data': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/data.log',              #日志输出文件
            'maxBytes': 1024*1024*10,                   #文件最大大小
            'backupCount': 5,                           #备份份数
            'encoding': 'utf-8',                        #日志编码格式
            'formatter': 'standard',                    #使用哪种formatters日志格式
        },
        'record_data': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/record_data.log',              #日志输出文件
            'maxBytes': 1024*1024*10,                   #文件最大大小
            'backupCount': 5,                           #备份份数
            'encoding': 'utf-8',                        #日志编码格式
            'formatter': 'standard',                    #使用哪种formatters日志格式
        },
        'deleted_data': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/deleted_data.log',              #日志输出文件
            'maxBytes': 1024*1024*10,                   #文件最大大小
            'backupCount': 5,                           #备份份数
            'encoding': 'utf-8',                        #日志编码格式
            'formatter': 'standard',                    # 使用哪种formatters日志格式
        },
        'mgmt': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/mgmt.log',              #日志输出文件
            'maxBytes': 1024*1024*10,                   #文件最大大小
            'backupCount': 5,                           #备份份数
            'encoding': 'utf-8',                        #日志编码格式
            'formatter': 'standard',                    # 使用哪种formatters日志格式
        },
        'database': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/database.log',     #日志输出文件
            'maxBytes': 1024*1024*10,                  #文件大小
            'backupCount': 5,                           #备份份数
            'encoding': 'utf-8',
            'formatter': 'standard',                   # 使用哪种formatters日志格式
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',               # message level to be written to console
        },
    },
    'loggers': {
        'default': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'data': {
            'handlers': ['data'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'record_data': {
            'handlers': ['record_data'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'deleted_data': {
            'handlers': ['deleted_data'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'mgmt': {
            'handlers': ['mgmt'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = ('*')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'token',
)
