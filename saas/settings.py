"""
Django settings for saas project.

Generated by 'django-admin startproject' using Django 2.2.20.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
try:
    from saas.local_settings import *
except Exception:
    pass


import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1ywp=2^2aj%f#c#ghzw31l6f0w6vjpi(7=5zn9s7rsw9rpntzq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web.apps.WebConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.mymiddleware.UserStatusAuth',
    'middleware.mymiddleware.ProjectAuth',
    'middleware.mymiddleware.IssueAuth'

]

ROOT_URLCONF = 'saas.urls'

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

WSGI_APPLICATION = 'saas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'saas',
        'HOST':'43.143.205.124',
        'PORT':3306,
        'USER':'root',
        'PASSWORD':mysql_pwd,
        'ATOMIC_REQUEST':False, ## this setting will enable transaction on every single HTTP requests
        'AUTOCOMMIT':True,      ## this setting will enable autocommit of each query when the qyeries are executed
        'OPTIONS':{
            'isolation_level':'read committed'
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LOGIN_URL='/login/'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False  ##the setting USE_TZ means that use_timezone.
#I set the option to be False,because when I use datetime.datetime.now()
#to get a time object and store it in my mysql,the mysql will give a
#the time a timezone info automatically,and when I retrive the time in the backend, I need to
#use it to campare with other time,an error will occur because the time retrived have a
#timezone info.

AUTH_USER_MODEL='web.UserInfo'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'static')
]
#if you configure the variable STATIC_URL ,you have to configure the variable
#STATICFILE_DIRS.When you utilize the tag {% static '' %} you will get a url that
#indicate the staitcfile,and then the tag {% load static %} will load the staticfiles
#depend on the url and the sequence '/static/ ,and the load process only effect when
#you set the variable STATICFILE_DIRS
MEDIA_ROOT=os.path.join(BASE_DIR,'media')