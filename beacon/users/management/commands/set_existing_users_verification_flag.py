# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from beacon.cognito import services as cognito_services


class Command(BaseCommand):
    help = "Set verification flag for existing users by checking it on cognito"

    def handle(self, *args, **options):
        user_model = get_user_model()
        cognito_user = cognito_services.Cognito(
            settings.COGNITO_USER_POOL_ID,
            settings.COGNITO_APP_ID,
            user_pool_region=settings.COGNITO_APP_REGION,
        )

        # Get Exception classes
        exceptions_mapping = cognito_services.get_exception_handling_classes(
            "test@example.com"
        )

        # there is no api to check if user is verified or not.
        # So, its a hackish way to check if user is verified or not
        for user in user_model.objects.all():
            try:
                cognito_user.confirm_sign_up("123456", username=user.email)
            except exceptions_mapping["_code_to_exception"]["NotAuthorizedException"]:
                user.is_verified = True
                user.save()
            except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
                pass
            except exceptions_mapping["_code_to_exception"]["CodeMismatchException"]:
                pass
            except exceptions_mapping["_code_to_exception"]["ExpiredCodeException"]:
                pass
            except exceptions_mapping["_code_to_exception"]["TooManyRequestsException"]:
                pass

        self.stdout.write(
            self.style.SUCCESS("Successfully updated all users' verification flag!")
        )
