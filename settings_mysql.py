from settings_ddf import *

DDF_TEST_GEODJANGO = True

# MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ddf',
        'USER': 'paulocheque', # please, change this if you want to run tests in your machine
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 3306,
    }
}

if DDF_TEST_GEODJANGO:
    INSTALLED_APPS += ('django.contrib.gis',)
