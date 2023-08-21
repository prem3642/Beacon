# -*- coding: utf-8 -*-
# Third Party Stuff
import pytest
from django.urls import reverse

from . import factories as f

pytestmark = pytest.mark.django_db


def test_get_organisation_search(client, settings):
    url = reverse("organisations-list")
    fld = f.create_organisation(
        domain="fldnyc.example.com", parent=None, title="fueled"
    )
    test_org = f.create_organisation(
        domain="test.example.com", parent=None, title="test"
    )
    beacon = f.create_organisation(
        domain="beacon.example.com", parent=None, title="beacon"
    )
    response = client.json.get(url)
    assert response.status_code == 400
    assert (
        response.data["errors"][0]["message"]
        == "Query parameter search_term is required."
    )

    url += "?search_term=fuel"
    response = client.json.get(url)
    assert response.status_code == 400
    assert (
        response.data["errors"][0]["message"]
        == f"search_term should be at least {settings.ORG_SEARCH_TERM_CHAR_LIMIT} char(s) long."
    )

    url = reverse("organisations-list") + "?search_term=fueled"
    response = client.json.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 1
    expected_keys = [
        "title",
        "domain",
        "location",
    ]
    assert set(expected_keys).issubset(response.data["results"][0].keys())
    assert response.data["results"][0].get("title") == str(fld.title)

    # add fueled london
    fld_lnd = f.create_organisation(
        domain="fldlnd.example.com", parent=None, title="fueled London"
    )
    response = client.json.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 2
    expected_keys = [
        "title",
        "domain",
        "location",
    ]
    assert set(expected_keys).issubset(response.data["results"][0].keys())
    assert response.data["results"][0].get("title") == str(fld.title)
    assert response.data["results"][1].get("title") == str(fld_lnd.title)

    # Add test org location to fueled
    test_org.location = "fueled"
    test_org.save()
    response = client.json.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 3
    assert set(expected_keys).issubset(response.data["results"][0].keys())
    assert response.data["results"][0].get("title") == str(fld.title)
    assert response.data["results"][1].get("title") == str(test_org.title)
    assert response.data["results"][2].get("title") == str(fld_lnd.title)

    # Add beacon's alternate name to fueled
    beacon.alternate_names = ["fueled", "beacon", "bwb"]
    beacon.save()
    response = client.json.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 4
    assert set(expected_keys).issubset(response.data["results"][0].keys())
    assert response.data["results"][0].get("title") == str(fld.title)
    assert response.data["results"][1].get("title") == str(test_org.title)
    assert response.data["results"][2].get("title") == str(beacon.title)
    assert response.data["results"][3].get("title") == str(fld_lnd.title)


def test_organisation_search_do_not_return_parent_org_if_children_exist(client):
    parent_org_with_children = f.create_organisation(
        domain="fldnyc.example.com", parent=None, title="parent_one"
    )
    # Child Org
    f.create_organisation(
        domain="test1.example.com",
        parent=parent_org_with_children,
        title="child1",
        is_active=True,
    )
    f.create_organisation(
        domain="test2.example.com",
        parent=parent_org_with_children,
        title="child2",
        is_active=False,
    )
    parent_org_without_child = f.create_organisation(
        domain="fldnyc.example.com", parent=None, title="parent_two"
    )
    url = reverse("organisations-list") + "?search_term=parent"
    response = client.json.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 1
    expected_keys = [
        "title",
        "domain",
        "location",
    ]
    assert set(expected_keys).issubset(response.data["results"][0].keys())
    assert response.data["results"][0].get("title") == str(
        parent_org_without_child.title
    )
    assert response.data["results"][0].get("domain") == str(
        parent_org_without_child.domain
    )
    assert (
        response.data["results"][0].get("location") == parent_org_without_child.location
    )


def test_organisation_search_do_not_return_parent_org_if_all_children_inactive(client):
    parent_org_with_inactive_child = f.create_organisation(
        domain="fldnyc.example.com", parent=None, title="parent_one"
    )
    # Child Org
    f.create_organisation(
        domain="test.example.com",
        parent=parent_org_with_inactive_child,
        title="child",
        is_active=False,
    )
    url = reverse("organisations-list") + "?search_term=parent"
    response = client.json.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 0


def test_get_organisation(client):
    url = reverse("org-config")
    nav = f.create_homepage_nav(is_emergency_nav=True, is_active=True, is_global=True)
    nav2 = f.create_homepage_nav(is_emergency_nav=False, is_active=True)
    org2 = f.create_organisation(domain="test2.example.com", parent=None)
    org = f.create_organisation(domain="test.example.com", parent=None)
    f.create_organisation_homepage_nav(organisation=org2, homepage_nav=nav2)

    headers = {
        "Referer": "https://test.example.com/",
        "Origin": "https://test.example.com",
    }
    response = client.json.get(
        url, HTTP_ORIGIN="http://test.example.com", headers=headers
    )
    assert response.status_code == 200
    expected_keys = [
        "id",
        "domain",
        "phone",
        "username",
        "program_name",
        "logo",
        "glyph",
        "glyph_width",
        "glyph_height",
        "show_international_section",
        "number_of_sessions",
        "session_frequency",
        "is_no_of_sessions_hidden",
        "share_url",
        "company_code",
        "parent_code",
        "mdlive_provider_type",
        "show_safety_screen",
        "safety_screen_phone",
        "safety_screen_url",
        "show_disclaimer",
        "introduction",
    ]
    homepage_nav_keys = [
        "id",
        "label",
        "url",
        "is_emergency_nav",
        "sort_order",
        "description",
        "is_url_target_blank",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("id") == str(org.id)
    assert response.data.get("domain") == "test.example.com"
    assert len(response.data.get("homepage_navs")) == 1
    assert set(homepage_nav_keys).issubset(response.data.get("homepage_navs")[0].keys())
    assert response.data.get("homepage_navs")[0]["id"] == str(nav.id)
    assert response.data.get("mdlive_provider_type") == 38

    headers2 = {
        "Referer": "https://test2.example.com/",
        "Origin": "https://test2.example.com",
    }
    response = client.json.get(
        url, HTTP_ORIGIN="http://test2.example.com", headers=headers2
    )
    assert response.status_code == 200
    assert response.data.get("id") == str(org2.id)
    assert len(response.data.get("homepage_navs")) == 2
    assert set(homepage_nav_keys).issubset(response.data.get("homepage_navs")[0].keys())
    assert response.data.get("homepage_navs")[0]["id"] == str(nav2.id)
    assert response.data.get("homepage_navs")[1]["id"] == str(nav.id)


def test_get_homepage_navs(client):
    url = reverse("homepage-navs-list")
    nav = f.create_homepage_nav(is_emergency_nav=True, is_active=True, is_global=True)
    nav2 = f.create_homepage_nav(is_emergency_nav=False, is_active=True)
    org = f.create_organisation(domain="test.example.com", parent=None)
    f.create_organisation_homepage_nav(organisation=org, homepage_nav=nav2)

    headers = {
        "Referer": "https://test.example.com/",
        "Origin": "https://test.example.com",
    }
    expected_keys = [
        "id",
        "label",
        "url",
        "is_emergency_nav",
        "sort_order",
        "description",
        "is_url_target_blank",
    ]
    response = client.json.get(
        url, HTTP_ORIGIN="http://test.example.com", headers=headers
    )
    assert response.status_code == 200
    assert set(expected_keys).issubset(response.data.get("results")[0].keys())
    assert len(response.data["results"]) == 2
    assert response.data["results"][0]["id"] == str(nav2.id)
    assert response.data["results"][1]["id"] == str(nav.id)


def test_get_homepage_nav_categories(client):
    nav = f.create_homepage_nav(is_emergency_nav=False, is_active=True)
    org = f.create_organisation(domain="test.example.com", parent=None)
    f.create_organisation_homepage_nav(organisation=org, homepage_nav=nav)
    category = f.create_homepage_nav_category(homepage_nav=nav)
    subcategory = f.create_homepage_nav_subcategory(category=category)
    subcategory2 = f.create_homepage_nav_subcategory(category=category)
    subcategory3 = f.create_homepage_nav_subcategory(category=category)
    f.create_excluded_organisation_homepage_nav_subcategory(
        organisation=org, homepage_nav_subcategory=subcategory3
    )

    url = reverse("homepage-navs-categories", kwargs={"pk": str(nav.id)})

    headers = {
        "Referer": "https://test.example.com/",
        "Origin": "https://test.example.com",
    }
    response = client.json.get(
        url, HTTP_ORIGIN="http://test.example.com", headers=headers
    )
    category_expected_keys = ["id", "name", "subcategories"]
    subcategory_expected_keys = ["id", "name", "url"]
    assert response.status_code == 200
    assert len(response.data) == 1
    assert len(response.data[0].get("subcategories")) == 2
    assert set(category_expected_keys).issubset(response.data[0].keys())
    assert set(subcategory_expected_keys).issubset(
        response.data[0].get("subcategories")[0].keys()
    )
    assert response.data[0].get("id") == str(category.id)
    assert response.data[0].get("subcategories")[0].get("id") == str(subcategory.id)
    assert response.data[0].get("subcategories")[1].get("id") == str(subcategory2.id)
