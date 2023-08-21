# -*- coding: utf-8 -*-
from .. import services as scc_services


def get_data_in_bwb_format(scc_data):
    """
    Test utility to convert SCC data into BWB and clean Null parameters.
    """
    bwb_data = scc_services.convert_scc_data_into_bwb_format(scc_data)
    return bwb_data


def generate_test_data(keys, values):
    """
    Test utility to generate sub-dict. from a given values dict. containing only the given keys.
    """
    return {k: v for k, v in values.items() if k in keys}
