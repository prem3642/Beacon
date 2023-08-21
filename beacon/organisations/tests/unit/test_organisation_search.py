# -*- coding: utf-8 -*-
# Third Party Stuff
import pytest
from rest_framework.exceptions import ValidationError

from beacon.organisations.services import search_organisation
from beacon.organisations.tests import factories as f

pytestmark = pytest.mark.django_db


def test_organisation_search_for_scc_sync():
    org1 = f.create_organisation(
        parent_code="FLD", group_number="gp1", benefit_package="bp1"
    )

    with pytest.raises(ValidationError) as err:
        search_organisation(
            parent_code="FD",
            group_number="gp1",
            benefit_package="bp1",
            raise_exception=True,
        )

    assert (
        err.value.args[0]
        == "We cannot find this organization within BWB. Please register this user manually within BWB admin"
    )

    searched_org = search_organisation(
        parent_code="FLD",
        group_number="gp1",
        benefit_package="bp1",
        raise_exception=True,
    )
    assert searched_org.id == org1.id

    org2 = f.create_organisation(
        parent_code="FLD", group_number="gp1", benefit_package="bp2"
    )

    searched_org = search_organisation(
        parent_code="FLD",
        group_number="gp1",
        benefit_package="bp2",
        raise_exception=True,
    )
    assert searched_org.id == org2.id

    org2.benefit_package = "bp1"
    # In order to test search for combo of
    # parent code + group number
    org2.group_number = "gp2"
    org2.save()

    searched_org = search_organisation(
        parent_code="FLD",
        group_number="gp1",
        benefit_package="bp2",
        raise_exception=True,
    )
    assert searched_org.id == org1.id

    org2.group_number = "gp1"
    org2.save()

    with pytest.raises(ValidationError) as err:
        search_organisation(
            parent_code="FD",
            group_number="gp1",
            benefit_package="bp1",
            raise_exception=True,
        )

    assert (
        err.value.args[0]
        == "We cannot find this organization within BWB. Please register this user manually within BWB admin"
    )

    org3 = f.create_organisation(
        parent_code="FLD", group_number="gp1", benefit_package="bp2"
    )

    searched_org = search_organisation(
        parent_code="FLD",
        group_number="gp1",
        benefit_package="bp2",
        raise_exception=True,
    )
    assert searched_org.id == org3.id

    searched_org = search_organisation(
        parent_code="FLD",
        group_number="gp1",
        benefit_package="bp3",
        raise_exception=False,
    )
    assert searched_org is None
