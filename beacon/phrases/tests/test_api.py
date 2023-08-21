# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse

from . import factories as f

pytestmark = pytest.mark.django_db


def test_get_homepage_phrases(client):
    url = reverse("phrases-home-list")
    phrase1 = f.create_homepage_phrase(is_published=True)
    phrase2 = f.create_homepage_phrase(is_published=True)
    f.create_homepage_phrase(is_published=False)

    response = client.json.get(url)
    expected_keys = ["id", "headline", "sub_headline"]
    assert response.status_code == 200
    assert len(response.data) == 2
    assert set(expected_keys).issubset(response.data[0].keys())
    assert response.data[0].get("id") == str(phrase2.id)
    assert response.data[1].get("id") == str(phrase1.id)
