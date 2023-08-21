# -*- coding: utf-8 -*-
# Third Party Stuff
from django.core.management.base import BaseCommand

# beacon Stuff
from beacon.organisations.models import (
    HomepageNav,
    HomepageNavCategory,
    HomepageNavSubCategory,
)


class Command(BaseCommand):
    help = "Load initial categories"

    def handle(self, *args, **kwargs):
        homepage_nav, _ = HomepageNav.objects.get_or_create(
            label="Care for your family",
            defaults={"label": "Care for your family", "url": "/family"},
        )

        categories = [
            (
                "Child Care Services",
                [
                    (
                        "Adoption Assisted Search",
                        "http://www.powerflexweb.com/resultAdoptionAssistedSearchElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                    (
                        "Adoption Provider Locator",
                        "http://www.powerflexweb.com/resultAdoptionLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                    (
                        "Child Care Assisted Search",
                        "http://www.powerflexweb.com/resultChildCareAssistedSearchElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                    (
                        "Child Care Provider Locator",
                        "http://www.powerflexweb.com/resultChildCareLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                ],
            ),
            (
                "Community Services",
                [
                    (
                        "Volunteer Opportunities",
                        "http://www.powerflexweb.com/resultVolunteerOpportunitiesLocatorElement"
                        ".php?password=employee&id=1614&code=value",
                    )
                ],
            ),
            (
                "Elder Care / Adult Care Services",
                [
                    (
                        "Adult Care Assisted Search",
                        "http://www.powerflexweb.com/resultElderCareLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                    (
                        "Adult Care Service Locator",
                        "http://www.powerflexweb.com/resultElderCareLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                ],
            ),
            (
                "Schools and Camps",
                [
                    (
                        "Camp Locator",
                        "http://www.powerflexweb.com/resultCampLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                    (
                        "College Locator",
                        "http://www.powerflexweb.com/resultCollegeLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                    (
                        "College Undergrad Locator",
                        "http://www.powerflexweb.com/resultCollegeUndergradLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                    (
                        "Education Assisted Search",
                        "http://www.powerflexweb.com/resultEducationAssistedSearchElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                    (
                        "Scholarship Locator",
                        "http://www.powerflexweb.com/resultScholarshipLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                ],
            ),
            (
                "Pet Care",
                [
                    (
                        "Pet Services Search",
                        "http://www.powerflexweb.com/resultPetLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                    (
                        "Pet Services Locator",
                        "http://www.powerflexweb.com/resultPetLocatorElement.php?"
                        "password=employee&id=1614&code=value",
                    ),
                ],
            ),
        ]

        for category in categories:
            category_obj = HomepageNavCategory.objects.create(
                name=category[0], homepage_nav=homepage_nav
            )
            subcategories = [
                HomepageNavSubCategory(
                    category=category_obj, name=subcategory[0], url=subcategory[1]
                )
                for subcategory in category[1]
            ]
            HomepageNavSubCategory.objects.bulk_create(subcategories)

        self.stdout.write(self.style.SUCCESS("Successfully created categories!"))
