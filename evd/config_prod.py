from dotenv import load_dotenv
import os
load_dotenv()

kDatabaseHost = os.getenv('EVD_DB_HOST')
kDatabaseUser = os.getenv('EVD_DB_USER')
kDatabasePwd = os.getenv('EVD_DB_PWD')
kDatabaseName = os.getenv('EVD_DB_NAME')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': kDatabaseName,                      # Or path to database file if using sqlite3.
        'USER': kDatabaseUser,                      # Not used with sqlite3.
        'PASSWORD':kDatabasePwd,                  # Not used with sqlite3.
        'HOST': kDatabaseHost,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
	   "init_command": "SET default_storage_engine=MYISAM",
        }
    },
    'wikividya': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'wiki_1_26',                      # Or path to database file if using sqlite3.
        'USER': kDatabaseUser,                      # Not used with sqlite3.
        'PASSWORD':kDatabasePwd,                  # Not used with sqlite3.
        'HOST': kDatabaseHost,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
	   "init_command": "SET default_storage_engine=MYISAM",
        }
    }
}

static_folder = "static/"
