# -*- coding: utf-8 -*-
"""Development Settings

Adds sensible defaults for developement of project
- Enable DEBUG
- Log outgoing emails to console
- Enable Django Extensions
- Enable Django Debug Toolbar
- Use local caches
- Enable livereloading
"""

from .common import *  # noqa F405
from .common import INSTALLED_APPS, env

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # noqa: F405

INTERNAL_IPS = (
    "127.0.0.1",
    "192.168.33.12",
)

ALLOWED_HOSTS = ["*"]


# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# A secret key for this particular Django installation. Used in secret-key
# hashing algorithms. Set this in your settings, or Django will complain
# loudly.
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="CHANGEME!!!")

# cors
# --------------------------------------------------------------------------
CORS_ORIGIN_WHITELIST = env.list(
    "CORS_ORIGIN_WHITELIST", default=["http://localhost", "http://localhost:8000"]
)

# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# django-extensions (http://django-extensions.readthedocs.org/)
# ------------------------------------------------------------------------------
INSTALLED_APPS += ("django_extensions",)

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += [  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
INSTALLED_APPS += ("debug_toolbar",)

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}

# This will expose all browsable api urls. For dev the default value is true
API_DEBUG = env.bool("API_DEBUG", default=True)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------

# Media configuration to support deployment of media files while is debug=True or development.
MEDIA_URL = env("MEDIA_URL", default="/media/")

DDF_DEFAULT_DATA_FIXTURE = (
    "beacon.base.utils.dynamic_fixture_util.PatchedSequentialDataFixture"
)
