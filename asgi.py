# -*- coding: utf-8 -*-
"""
ASGI config for beacon project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

# Standard Library
import os

# Third Party Stuff
from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

# Read .env file and set key/value inside it as environement variables
# see: http://github.com/theskumar/python-dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.production")

application = get_asgi_application()
