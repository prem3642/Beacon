# -*- coding: utf-8 -*-
# Third Party Stuff
from django_dynamic_fixture import G

from ..models import SccApiLog


def create_scc_api_log(**kwargs):
    return G(SccApiLog, **kwargs)
