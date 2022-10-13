# Django settings for evd project.
import os
from config_prod import *
from dotenv import load_dotenv
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
print PROJECT_DIR
# DEBUG = True
DEBUG = False
#DEBUG404 = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('venkat.sriraman@evidyaloka.org', 'tech-team@evidyaloka.org'),
)

MANAGERS = ADMINS


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')6%dz+)co-3ro@ccb5a2bvbknt_n+&uvd-#pu*k@_fypomc^%p'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'genutilities.api_session_auth_middleware.mobile_api_auth_middleware',
)

CORS_ORIGIN_ALLOW_ALL = True
ROOT_URLCONF='evd.urls'
TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
    '/var/www/evd/venv/django/contrib/admin/templates',
    './venv/django/contrib/admin/templates'
)

TEMPLATE_CONTEXT_PROCESSORS = ( 
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)
#Loading environment variables set
load_dotenv()

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'web.pipelines.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)

AUTHENTICATION_BACKENDS = ( 
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

#REGISTRATION_BACKEND = 'registration.backends.default.DefaultBackend'
DEFAULT_FROM_EMAIL   = 'evlSystem@evidyaloka.org'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'grappelli',
    'django.contrib.admin',
    'web',
    'social_auth',
    'notification',
    'mailer',
    'registration',
#    'memcache_status',
#    'chronograph',
    'south',
    'mailer',
    'alerts',
    'rest_authentication',
    'api',
    'workplace',
    'partner',
    'webext',
    'configs',
    'questionbank',
    'genutilities',
    'student',
    'corsheaders',
#    'cronjobs',
    #'django_cron'

    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


ACCOUNT_ACTIVATION_DAYS  = 7
AUTH_PROFILE_MODULE = 'web.UserProfile'
FACEBOOK_CACHE_TIMEOUT = 1800
FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'public_profile', 'user_birthday', 'publish_actions', 'user_events']
GOOGLE_OAUTH_EXTRA_SCOPE = ['https://www.googleapis.com/auth/userinfo.profile']
#FACEBOOK_APP_ID              = '369792343072075'
#FACEBOOK_API_SECRET          = '36b21692228d9a5691a27f2d05093692'

# evd.cloudlibs.com app_id and app_secret:
#FACEBOOK_APP_ID              = '250536911721296'
#FACEBOOK_API_SECRET          = '87bb9ccb0ce03c689e20aebbf3b6aff1'

#evidyaloka.org new app[pamidi].
FACEBOOK_APP_ID              = '499969136679992'
FACEBOOK_API_SECRET          = '0105cdf4d3a915e5f03252b62a778d60'
FACEBOOK_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline',
    'approval_prompt': 'auto'
}

#GOOGLE_OAUTH2_CLIENT_ID      = '506643569510.apps.googleusercontent.com'
#GOOGLE_OAUTH2_CLIENT_SECRET  = '4fkqFtE8PUXSGG3PSErjfgNW'
# GOOGLE_OAUTH2_CLIENT_ID      = '344824378773-gtf9iv6f2oef7ciriu0a7oqnsle5p6kc.apps.googleusercontent.com'
# GOOGLE_OAUTH2_CLIENT_SECRET  = 'TGUv6CN8yh5l-NgpkK5zcJKy'
#sudhir cred - 
# GOOGLE_OAUTH2_CLIENT_ID      = '344824378773-gtf9iv6f2oef7ciriu0a7oqnsle5p6kc.apps.googleusercontent.com'
# GOOGLE_OAUTH2_CLIENT_SECRET  = 'TGUv6CN8yh5l-NgpkK5zcJKy'
# GOOGLE_OAUTH2_CLIENT_ID      = '802633556098-3rkavdsbdg0pg9soseio51mo8dtjads1.apps.googleusercontent.com'
# GOOGLE_OAUTH2_CLIENT_SECRET  = 'paGi0p2yfuPiG9kx6_w6cma2'
# GOOGLE_OAUTH2_CLIENT_ID      = '802633556098-caoflbv1ubs19vmmanmcqia3alij2m64.apps.googleusercontent.com'
# GOOGLE_OAUTH2_CLIENT_SECRET  = 'zY8DL_5ntj6O9uQouqhTYor9'
# GOOGLE_OAUTH2_CLIENT_ID      = '344824378773-gtf9iv6f2oef7ciriu0a7oqnsle5p6kc.apps.googleusercontent.com'
# GOOGLE_OAUTH2_CLIENT_SECRET  = 'TGUv6CN8yh5l-NgpkK5zcJKy'
# GOOGLE_OAUTH2_CLIENT_ID      = '802633556098-3rkavdsbdg0pg9soseio51mo8dtjads1.apps.googleusercontent.com'
# GOOGLE_OAUTH2_CLIENT_SECRET  = 'paGi0p2yfuPiG9kx6_w6cma2'
GOOGLE_OAUTH2_CLIENT_ID      = '802633556098-caoflbv1ubs19vmmanmcqia3alij2m64.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET  = 'zY8DL_5ntj6O9uQouqhTYor9'

GOOGLE_OAUTH2_USE_UNIQUE_USER_ID = True
GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline',
    'approval_prompt': 'auto'
}

TWITTER_CONSUMER_KEY         = 'srs4fILCgszNLdeKpoFl6w'
TWITTER_CONSUMER_SECRET      = 'ltDVB8Q9Q1VsS38misDxjw3WfJO6aXxbUHE6pmzlw'


LOGIN_URL          = '/'
LOGIN_REDIRECT_URL = '/v2/vLounge/'
LOGIN_ERROR_URL    = '/login-error/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/v2/vLounge/'

SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/user_profile/'
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_UUID_LENGTH = 16
SOCIAL_AUTH_EXPIRATION = 'expires'
SOCIAL_AUTH_SESSION_EXPIRATION = False
SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_SANITIZE_REDIRECTS = False
SOCIAL_AUTH_INACTIVE_USER_URL = '...'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'evlSystem@evidyaloka.org'
EMAIL_HOST_PASSWORD = 'evlSystem'
EMAIL_PORT = 587
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

COUNT = 0

FCM_API_KEY = "AAAAuuCwIII:APA91bHBPAcSerXnX9Hh60E23O-HtRJerAivbcK5_Bm4ek2yv9ImhTAZwpve8uEH8Qvhgdi8RW7xhGOajSQJdUCWndSZkfHSxzo-0TyrKwJ8lg1bhVI1jS3q_N5TIjvBEPRZk8pZyrmU"
FCM_API_KEY_STUDENT = "AAAAODAZ7do:APA91bG_wlyCKS391NjGsxlhxY2peQacyZDT2e98739nlUIZ_nHLLDEFOv8bVCe6aII_2qFZtjdfRxBgIZYqnhluObrxBE3mOGZjkxfQA_ca-jgNs1tAmG0HIpOkxAoPTj-7bZJpr2Wb"
# WEB_BASE_URL = 'https://evidyaloka.org/'
WEB_BASE_URL = 'https://www.evidyaloka.org/'
SMS_AUTHENTICATION_KEY = "339829AslD2o28Uzp5f44b249P1"
TEMPLATE_ID = "5f47aba4d6fc055c4b291743"
MOBILE_PREFIX = '91'
MOBILE_SENDER_ID = "EVDYLK"
MOBILE_HASH_CODE_LOCAL = "E5xOJ18sxBG"
MOBILE_DLT_TE_ID = "1107164075999531088"
BASE_URL_MSG91 = "http://api.msg91.com"


TEMPORARY_DOCUMENT_STOREAGE_PATH = './tempfiles'
SCHOOL_DOCUMENT_STORAGE_FOLDER = "user_documents/school_pictures"
STUDENT_DOUBT_DOCUMENT_STORAGE_FOLDER = "user_documents/student_doubts"
TEACHER_DOUBT_RESPONSE_STORAGE_FOLDER = "user_documents/teacher_doubt_responses"
STUDENT_PROFILE_PICTURE_FOLDER = "user_documents/student_profile_pictures"
SYSTEM_USER_ID_AUTH = 8668
CENTER_ACTIVITIES_STORAGE_FOLDER = "user_documents/center_activities"

REDIS_HOST = ''
REDIS_PORT = 6379
REDIS_PWD = ''
