# -*- coding: utf-8 -*-


def get_reverse_mapping(dict_to_reverse):
    return {value: key for key, value in dict_to_reverse.items()}


# Refer: https://linear.app/beacon-health/issue/BEA-172/add-timezone-to-register-endpoint-model
# Refer: docs/backend/mdlive/timezone_mapping.md
TIMEZONE_TO_MDLIVE_ID_MAP = {
    "America/Anchorage": 5,  # Alaska Standard Time (AKST)
    "America/Chicago": 2,  # Central Standard Time (CST)
    "America/Denver": 3,  # Mountain Standard Time (MST)
    "US/Hawaii": 6,  # Hawaii Standard Time (HST)
    "America/Los_Angeles": 4,  # Pacific Standard Time (PST)
    "America/New_York": 1,  # Eastern Standard Time (EST)
    "America/Phoenix": 12,  # Arizona Time (AZT)
    "America/Puerto_Rico": 11,  # Atlantic Standard Time (AST)
}

MDLIVE_ID_TO_TIMEZONE_NAME = get_reverse_mapping(TIMEZONE_TO_MDLIVE_ID_MAP)
