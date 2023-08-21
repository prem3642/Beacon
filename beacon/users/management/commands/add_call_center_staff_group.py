# -*- coding: utf-8 -*-

# Third Party Stuff
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Add Call Center Staff Group and assign permissions"

    def handle(self, *args, **options):
        call_center_staff_group, _ = Group.objects.get_or_create(
            name="Call Center Staff"
        )

        permission_names = [
            "Can view appointment",
            "Can view answer",
            "Can view appointment slot query",
            "Can view provider",
            "Can view organisation",
            "Can view organisation homepage nav",
            "Can add user",
            "Can add User",
            "Can view User",
            "Can view user",
            "Can view user agent",
        ]

        permissions = Permission.objects.filter(name__in=permission_names)

        for permission in permissions:
            call_center_staff_group.permissions.add(permission)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully added call center staff group with permissions"
            )
        )
