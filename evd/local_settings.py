import socket
from settings import *
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'db name',                      # Or path to database file if using sqlite3. evldb2
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD':' your_password',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
       "init_command": "SET default_storage_engine=MYISAM",
        }
    },
    'wikividya': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'db name',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD':'your_password',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
       "init_command": "SET default_storage_engine=MYISAM",
        }
    }
}
TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
    'C:\Jupiter-V0\env\django\contrib\admin\templates\admin'
)
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
    'C:\Jupiter-V0\env\django\contrib\admin\static'
)
TEMPORARY_DOCUMENT_STOREAGE_PATH = 'media/'
