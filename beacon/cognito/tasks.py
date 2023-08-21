# -*- coding: utf-8 -*-
# Third Party Stuff
from celery import shared_task
from django.contrib.auth import get_user_model

from .services import admin_update_profile


@shared_task(bind=True, autoretry_for=(ConnectionError,), max_retries=3)
def update_user_on_cognito_task(self, user_id, cognito_data):
    user_obj = get_user_model().objects.get(id=user_id)
    admin_update_profile(user_obj=user_obj, data=cognito_data)
