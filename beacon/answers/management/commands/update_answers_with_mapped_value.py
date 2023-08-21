# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from beacon.answers.models import UserResponse


class Command(BaseCommand):
    help = "Update all answers with mapped values"

    def handle(self, *args, **options):
        get_emotional_support_question_mapping = {
            "Myself": "Self",
            "MySelf": "Self",
            "My Partner": "Spouse",
            "A Co-Worker": "Other Adult",
            "A Dependent": "Child",
        }
        for res in UserResponse.objects.all():
            if res.emotional_support_for is not None:
                mapped_value = get_emotional_support_question_mapping.get(
                    res.emotional_support_for
                )
                if mapped_value:
                    res.emotional_support_for = mapped_value
                    res.save()

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully updated all "emotional support for" question response!'
            )
        )
