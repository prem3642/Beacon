# -*- coding: utf-8 -*-
# Standard Library
import time

# Third Party Stuff
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

# beacon Stuff
from beacon.cognito import services as cognito_services


class Command(BaseCommand):
    help = "Store all cognito data for existing users"

    def handle(self, *args, **options):
        user_model = get_user_model()

        # Get Exception classes
        # exceptions_mapping = cognito_services.get_exception_handling_classes('test@example.com')

        # there is no api to check if user is verified or not.
        # So, its a hackish way to check if user is verified or not
        for user in user_model.objects.all():
            # Get data only when its not set locally
            if user.first_name is None:
                cognito_data, _ = cognito_services.get_cognito_data_as_admin(user.email)
                if cognito_data:
                    user.first_name = cognito_data.get("first_name")
                    user.last_name = cognito_data.get("last_name")
                    user.birthdate = cognito_data.get("birthdate")
                    user.gender = cognito_data.get("gender")
                    user.phone = cognito_data.get("phone")
                    user.job_title = cognito_data.get("job_title")
                    user.relationship_status = cognito_data.get("relationship_status")
                    user.employment_status = cognito_data.get("employment_status")
                    user.address1 = cognito_data.get("address1")
                    user.address2 = cognito_data.get("address2")
                    user.city = cognito_data.get("city")
                    user.state = cognito_data.get("state")
                    user.zip = cognito_data.get("zip")
                    user.save()
                time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS("Successfully updated all users' cognito data!")
        )
