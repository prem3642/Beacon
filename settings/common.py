# -*- coding: utf-8 -*-
"""Django settings for beacon project.

see: https://docs.djangoproject.com/en/dev/ref/settings/
"""
# Third Party Stuff
import environ
from corsheaders.defaults import default_headers
from django.utils.translation import gettext_lazy as _

ROOT_DIR = environ.Path(__file__) - 2  # (/a/b/myfile.py - 2 = /a/)
APPS_DIR = ROOT_DIR.path("beacon")

env = environ.Env()

# INSTALLED APPS
# ==========================================================================
# List of strings representing installed apps.
# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django_sites",  # http://niwinz.github.io/django-sites/latest/
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    # 'django.contrib.humanize',  # Useful template tags
    "reversion",
    "beacon.answers",
    "beacon.base",
    "beacon.cognito",
    "beacon.mdlive",
    "beacon.phrases",
    "beacon.organisations",
    "beacon.questionnaire",
    "beacon.users",
    "beacon.scc",
    "rest_framework",  # http://www.django-rest-framework.org/
    "rest_framework_swagger",
    "versatileimagefield",  # https://github.com/WGBH/django-versatileimagefield/
    "corsheaders",  # https://github.com/ottoyiu/django-cors-headers/
    "raven.contrib.django.raven_compat",
    "mail_templated",  # https://github.com/artemrizhov/django-mail-templated
    "solo",  # https://github.com/lazybird/django-solo
    "django_user_agents",  # https://github.com/selwin/django-user_agents
    "adminsortable2",  # https://github.com/jrief/django-admin-sortable2
    "rest_framework_api_key",  ##api_key for dfd
)

# INSTALLED APPS CONFIGURATION
# ==========================================================================

# django.contrib.auth
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# AWS Cognito Configuration
COGNITO_TEST_USERNAME = env("COGNITO_TEST_USERNAME", default="")
COGNITO_TEST_PASSWORD = env("COGNITO_TEST_PASSWORD", default="")
COGNITO_USER_POOL_ID = env("COGNITO_USER_POOL_ID", default="")
COGNITO_APP_ID = env("COGNITO_APP_ID", default="")
COGNITO_APP_SECRET = env("COGNITO_APP_SECRET", default="")
COGNITO_APP_USERNAME = env("COGNITO_APP_USERNAME", default="")
COGNITO_APP_REGION = env("COGNITO_APP_REGION", default="us-east-1")
COGNITO_ATTR_MAPPING = {
    "email": "email",
    "given_name": "first_name",
    "family_name": "last_name",
    "address": "address1",
    "birthdate": "birthdate",
    "gender": "gender",
    "phone_number": "phone",
    "custom:is_active": "is_active",
    "custom:address2": "address2",
    "custom:city": "city",
    "custom:state": "state",
    "custom:zip": "zip",
    "custom:relationship": "relationship",
    "custom:id": "id",
    "custom:employment_status": "employment_status",
    "custom:relationship_status": "relationship_status",
    "custom:job_title": "job_title",
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 6,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "beacon.base.password_validators.ComplexPasswordValidator",
    },
]

# For Exposing browsable api urls. By default urls won't be exposed.
API_DEBUG = env.bool("API_DEBUG", default=False)

# rest_framework
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "beacon.base.api.pagination.PageNumberPagination",
    "PAGE_SIZE": 30,
    # Default renderer classes for Rest framework
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    # 'Accept' header based versioning
    # http://www.django-rest-framework.org/api-guide/versioning/
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.AcceptHeaderVersioning",
    "DEFAULT_VERSION": "1.0",
    "ALLOWED_VERSIONS": [
        "1.0",
    ],
    "VERSION_PARAMETER": "version",
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.AnonRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10000/day",
    },
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        # Primary api authentication
        "beacon.users.backends.UserTokenAuthentication",
        # Mainly used for api debug.
        "rest_framework.authentication.SessionAuthentication",
    ),
    "EXCEPTION_HANDLER": "beacon.base.exceptions.exception_handler",
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

# API Auth Configuration
JWT_TOKEN_EXPIRATION_DURATION = env.int(
    "JWT_TOKEN_EXPIRATION_DURATION", default=30
)  # in minutes

# https://django-rest-swagger.readthedocs.io/en/latest/settings/
SWAGGER_SETTINGS = {
    "LOGIN_URL": "rest_framework:login",
    "LOGOUT_URL": "rest_framework:logout",
    "SECURITY_DEFINITIONS": {
        # For BasicAuthentication
        "basic": {"type": "basic"},
        # For UserTokenAuthentication
        "api_key": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
}

# DJANGO_SITES
# ------------------------------------------------------------------------------
# see: http://django-sites.readthedocs.org
SITE_SCHEME = env("SITE_SCHEME", default="http")
SITE_DOMAIN = env("SITE_DOMAIN", default="localhost:8000")
SITE_NAME = env("SITE_NAME", default="beacon")

# This is used in-case of the frontend is deployed at a different url than this django app.
FRONTEND_SITE_SCHEME = env("FRONTEND_SITE_SCHEME", default="https")
FRONTEND_SITE_DOMAIN = env("FRONTEND_SITE_DOMAIN", default="example.com")
FRONTEND_SITE_NAME = env("FRONTEND_SITE_NAME", default="beacon")

SITES = {
    "current": {"domain": SITE_DOMAIN, "scheme": SITE_SCHEME, "name": SITE_NAME},
    "frontend": {
        "domain": FRONTEND_SITE_DOMAIN,
        "scheme": FRONTEND_SITE_SCHEME,
        "name": FRONTEND_SITE_NAME,
    },
}
SITE_ID = "current"

# see user.services.send_password_reset
# password-confirm path should have placeholder for token
FRONTEND_URLS = {
    "home": "/",
    "recover-password": "/password/forgot",
    "password-confirm": "/reset-password/{token}/",
    "login": "/log-in",
    "messages-inbox": "/messages/inbox",
}

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
# List of middleware classes to use.  Order is important; in the request phase,
# this middleware classes will be applied in the order given, and in the
# response phase the middleware will be applied in reverse order.
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "log_request_id.middleware.RequestIDMiddleware",  # For generating/adding Request id for all the logs
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
]

# DJANGO CORE
# ------------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
# Defaults to false, which is safe, enable them only in development.
DEBUG = env.bool("DJANGO_DEBUG", False)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "UTC"

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

# Languages we provide translations for
LANGUAGES = (("en", _("English")),)

if USE_TZ:
    # Add timezone information to datetime displayed.
    # https://mounirmesselmeni.github.io/2014/11/06/date-format-in-django-admin/
    from django.conf.locale.en import formats as en_formats

    en_formats.DATETIME_FORMAT = "N j, Y, P (e)"

# A tuple of directories where Django looks for translation files.
LOCALE_PATHS = (str(APPS_DIR.path("locale")),)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# The list of directories to search for fixtures
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

# The Python dotted path to the WSGI application that Django's internal servers
# (runserver, runfcgi) will use. If `None`, the return value of
# 'django.core.wsgi.get_wsgi_application' is used, thus preserving the same
# behavior as previous versions of Django. Otherwise this should point to an
# actual WSGI application object.
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "wsgi.application"

# URL CONFIGURATION
# ------------------------------------------------------------------------------
ROOT_URLCONF = "beacon.urls"

# Use this to change base url path django admin
DJANGO_ADMIN_URL = env.str("DJANGO_ADMIN_URL", default="admin")

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="beacon <support@beacon.com>")
EMAIL_SUBJECT_PREFIX = env("EMAIL_SUBJECT_PREFIX", default="[beacon] ")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://localhost/beacon"),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = 10


# TEMPLATE CONFIGURATION
# -----------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            str(APPS_DIR.path("templates")),
        ],
        "OPTIONS": {
            "debug": DEBUG,
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "beacon.base.context_processors.site_settings",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

CSRF_FAILURE_VIEW = "beacon.base.views.csrf_failure"

# STATIC FILE CONFIGURATION
# -----------------------------------------------------------------------------
# Absolute path to the directory static files should be collected to.
# Example: '/var/www/example.com/static/'
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR.path(".staticfiles"))

# URL that handles the static files served from STATIC_ROOT.
# Example: 'http://example.com/static/', 'http://static.example.com/'
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

# A list of locations of additional static files
STATICFILES_DIRS = (str(APPS_DIR.path("static")),)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: '/var/www/example.com/media/'
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(ROOT_DIR.path(".media"))

# URL that handles the media served from MEDIA_ROOT.
# Examples: 'http://example.com/media/', 'http://media.example.com/'
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = env("MEDIA_URL", default="{}://{}/media/".format(SITE_SCHEME, SITE_DOMAIN))

#  SECURITY
# -----------------------------------------------------------------------------
CSRF_COOKIE_HTTPONLY = False  # Allow javascripts to read CSRF token from cookies
SESSION_COOKIE_HTTPONLY = True  # Do not allow Session cookies to be read by javascript

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# django-log-request-id - Sending request id in response
REQUEST_ID_RESPONSE_HEADER = "REQUEST_ID"

# CORS
# --------------------------------------------------------------------------
CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST", default=[])
CORS_ALLOW_HEADERS = default_headers + ("access-control-allow-origin",)

# DJANGO CELERY CONFIGURATION
# -----------------------------------------------------------------------------
# see: http://celery.readthedocs.org/en/latest/userguide/tasks.html#task-states
CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = env(
    "CELERY_TIMEZONE", default=TIME_ZONE
)  # Use django's timezone by default

# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# Default logging for Django. This sends an email to the site admins on every
# HTTP 500 error. Depending on DEBUG, all other log records are either sent to
# the console (DEBUG=True) or discarded by mean of the NullHandler (DEBUG=False).
# See http://docs.djangoproject.com/en/dev/topics/logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "request_id": {"()": "log_request_id.filters.RequestIDFilter"},
    },
    "formatters": {
        "complete": {
            # NOTE: make sure to include 'request_id' in filters when using this
            # formatter in any handlers.
            "format": '%(asctime)s:[%(levelname)s]:logger=%(name)s:request_id=%(request_id)s message="%(message)s"'
        },
        "simple": {"format": "%(levelname)s:%(asctime)s: %(message)s"},
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(levelname)s:%(asctime)s:] %(message)s",
        },
    },
    "handlers": {
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "complete",
            "filters": ["request_id"],
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "sentry": {
            "level": "ERROR",
            "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
            "formatter": "complete",
            "filters": ["request_id"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["null"],
            "propagate": False,
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["mail_admins", "console"],
            "level": "ERROR",
            "propagate": False,
        },
        "gunicorn": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "beacon": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        # Catch All Logger -- Captures any other logging
        "": {
            "handlers": ["console", "sentry"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}


def get_release():
    import os

    import raven

    import beacon

    release = beacon.__version__
    try:
        git_hash = raven.fetch_git_sha(os.path.dirname(os.pardir))[:7]
        release = "{}-{}".format(release, git_hash)
    except raven.exceptions.InvalidGitRepository:
        pass
    return release


RELEASE_VERSION = get_release()
RAVEN_CONFIG = {
    "dsn": env("SENTRY_DSN", default=""),
    "environment": env("SENTRY_ENVIRONMENT", default="production"),
    "release": RELEASE_VERSION,
}

SITE_INFO = {
    "RELEASE_VERSION": RELEASE_VERSION,
    "IS_RAVEN_INSTALLED": True if RAVEN_CONFIG.get("dsn") else False,
}

# MDLive Configuration
MDLIVE_API_KEY = env("MDLIVE_API_KEY", default="")
MDLIVE_PASSWORD = env("MDLIVE_PASSWORD", default="")
MDLIVE_URL = env("MDLIVE_URL", default="https://stage-rest-api.mdlive.com")
MDLIVE_ORGANISATION_USERNAME = env("MDLIVE_ORGANISATION_USERNAME", default="")
MDLIVE_ENTERPRISE_HASH = env("MDLIVE_ENTERPRISE_HASH", default=None)
MDLIVE_SUBSCRIBER_ID = env("MDLIVE_SUBSCRIBER_ID", default="subscriber_id")
MDLIVE_WEBHOOK_BASE_URL = env(
    "MDLIVE_WEBHOOK_BASE_URL", default="http://localhost:8000"
)
MDLIVE_WEBHOOK_URL = env("MDLIVE_WEBHOOK_URL", default="/api/messages/webhook")

# VERSATILE IMAGE FIELD SIZES
# http://django-versatileimagefield.readthedocs.org/en/latest/drf_integration.html
VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    "logo_image": [("full_size", "url")],
}

# Campaign Monitor Configuration
CAMPAIGN_MONITOR_API_KEY = env("CAMPAIGN_MONITOR_API_KEY", default="")
CAMPAIGN_MONITOR_LIST_ID = env("CAMPAIGN_MONITOR_LIST_ID", default="")

# Beacon Server Configuration
BWB_BASE_URL = env("BWB_BASE_URL", default="")
BWB_USER_REGISTER_DATA_SUBMIT_URL = env(
    "BWB_USER_REGISTER_DATA_SUBMIT_URL",
    default="/SelfServiceEAP/inquiryRequest/{service_id}/submit.do",
)
BWB_SERVICE_ID = env("BWB_SERVICE_ID", default="")
APPOINTMENT_HOMEPAGE_MESSAGE_TIME_THRESHOLD = env.int(
    "APPOINTMENT_HOMEPAGE_MESSAGE_TIME_THRESHOLD", default=48
)  # in hours
# In the format 'Full Name <email@example.com>, Full Name <anotheremail@example.com>'
BWB_SERVER_ADMINS = env.list(
    "BWB_SERVER_ADMINS",
    default=[
        "webapplications@beaconhealthoptions.com",
        "BeaconWellbeing@beaconhealthoptions.com",
    ],
)

# Project Configuration
USER_CSV_IMPORT_FILE_PATH = env(
    "USER_CSV_IMPORT_FILE_PATH", default="/tmp/beacon_cm_import.csv"
)
DEFAULT_ORG_FOR_TESTING = env("DEFAULT_ORG_FOR_TESTING", default=None)
ORG_SEARCH_TERM_CHAR_LIMIT = env.int("ORG_SEARCH_TERM_CHAR_LIMIT", default=5)
# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
USER_AGENTS_CACHE = "default"

# Un-Authenticated User Configuration
ANSWER_PERMISSION_SESSION_TIMEOUT = env.int(
    "ANSWER_PERMISSION_SESSION_TIMEOUT", default=30
)  # In  minutes
NUM_OF_FAILED_LOGIN_ATTEMPTS_ALLOWED = env.int(
    "NUM_OF_FAILED_LOGIN_ATTEMPTS_ALLOWED", default=4
)
ACCOUNT_LOCK_DURATION_AFTER_FAILED_LOGIN_ATTEMPTS = env.int(
    "ACCOUNT_LOCK_DURATION_AFTER_FAILED_LOGIN_ATTEMPTS", default=10
)  # In minutes

# Integration with connects (SCC)
INCOMING_SCC_API_SECRET_KEY = env("INCOMING_SCC_API_SECRET_KEY", default="")
OUTGOING_SCC_API_SECRET_KEY = env("OUTGOING_SCC_API_SECRET_KEY", default="")
SCC_TOKEN_EXPIRY_IN_MINUTES = env.int("SCC_TOKEN_EXPIRY_IN_MINUTES", default=60)
SCC_BASE_URL = env("SCC_BASE_URL", default="")
VERIFY_CONNECTS_SSL = env("VERIFY_CONNECTS_SSL", default=True)

# For value X, backoff would be X, 2X, 4X, 8X, and so forth.
SCC_RETRY_BACKOFF_FACTOR = env.int("SCC_RETRY_BACKOFF_FACTOR", default=1)
CELERY_FLOWER_USERNAME = env("CELERY_FLOWER_USERNAME", default="dev@fueled.com")
CELERY_FLOWER_PASSWORD = env("CELERY_FLOWER_PASSWORD", default="Bea1234!")
