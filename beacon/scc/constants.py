# -*- coding: utf-8 -*-

# Discrepancy for "birthdate" and "phone" are handled separately
FIND_DISCREPANCY_FOR_FIELDS = [
    "connects_mbr_id",
    "first_name",
    "last_name",
    "gender",
    "email",
    "address1",
    "address2",
    "city",
    "state",
    "zip",
]

FIND_CASE_INSENSITIVE_DISCREPANCY_FOR_FIELDS = [
    "first_name",
    "last_name",
    "address1",
    "address2",
    "city",
    "email",
]

# SCC stores some fields in all uppercase, therefore, BWB is also returning values of
# such fields in all uppercase. So that SCC can understand which values are
# mismatched regardless of case sensitivity in values for these fields. This is a
# temp fix here. Ideally, SCC system should handle comparing discrepancy error
# message to decide what is mismatched as per their system's standards. But
# considering it will take them time to release their next build. We are adding this
# temporary fix in the BWB system.
RETURN_DISCREPANCY_IN_UPPERCASE_FOR_SCC_FIELDS = [
    "firstName",
    "lastName",
    "addressLine1",
    "addressLine2",
    "addressCity",
]


def get_reverse_mapping(dict_to_reverse):
    return {value: key for key, value in dict_to_reverse.items()}


# 1-1 Mapping doesn't exist for BWB "phone" field, so it's handled
# separately within services.
SCC_TO_BWB_KEYS = {
    "memberId": "connects_mbr_id",
    "mdLiveMemberID": "mdlive_id",
    "emailAddress": "email",
    "firstName": "first_name",
    "lastName": "last_name",
    "dateOfBirth": "birthdate",
    "gender": "gender",
    "addressLine1": "address1",
    "addressLine2": "address2",
    "addressCity": "city",
    "addressStateCode": "state",
    "addressZipCode": "zip",
    "parentCode": "parent_code",
    "groupNumber": "group_number",
    "benefitPackage": "benefit_package",
    "relationshipStatus": "relationship_status",
    "employmentStatus": "employment_status",
    "jobTitle": "job_title",
    "primaryPresentingProblem": "chief_complaint1",
    "secondaryPresentingProblem": "chief_complaint2",
    "depressionScreenerQuestion3A": "how_often_less_interest_in_things",
    "depressionScreenerQuestion3B": "how_often_depressed",
    "anxietyScreenerQuestion5A": "how_often_nervous",
    "anxietyScreenerQuestion5B": "how_often_worry",
    "substanceUseQuestion7A": "difficulty_in_keeping_drinking_limit",
    "substanceUseQuestion7B": "felt_cut_down_drinking",
    "wellbeingDomainQuestion8": "how_emotionally_doing",
    "wellbeingDomainQuestion9": "how_physical_health",
    "wellbeingDomainQuestion10": "people_support",
    "wellbeingDomainQuestion11": "comfortable_in_managing_finances",
    "wellbeingDomainQuestion12": "resources_to_manage",
    "outcomesESDQuestion1": "number_of_days_missed_work",
    "outcomesESDQuestion2": "number_of_days_less_productive",
}

BWB_TO_SCC_KEYS = get_reverse_mapping(SCC_TO_BWB_KEYS)

EMPLOYMENT_STATUS_VALUE_MAPPING_SCC_TO_BWB = {
    "FT": "Full Time",
    "PT": "Part Time",
    "TM": "Terminated",
    "ML": "Medical Leave",
    "RE": "Retired",
    "DL": "Disciplinary Leave",
    "LO": "Laid Off",
    "IL": "Disability/Worker’s Compensation",
    "OT": None,
    "DATA": None,
}

EMPLOYMENT_STATUS_VALUE_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    EMPLOYMENT_STATUS_VALUE_MAPPING_SCC_TO_BWB
)
# After reverse mapping, None to "DATA" mapping exists in this dict, but that is invalid mapping.
# Because BWB's `None` for this field would be send as it is `None` to SCC (so no `None` to `None` mapping is needed)
# https://linear.app/beacon-health/issue/BEA-199/scc-employment-status-data-not-provided-should-be-translated-to-blank
EMPLOYMENT_STATUS_VALUE_MAPPING_BWB_TO_SCC.pop(None)
EMPLOYMENT_STATUS_VALUE_MAPPING_BWB_TO_SCC.update({"Dependent": "DATA"})

RELATIONSHIP_STATUS_VALUE_MAPPING_SCC_TO_BWB = {
    "1": "Never Married",
    "M": "Married",
    "5": "Separated",
    "D": "Divorced",
    "W": "Widowed",
    "4": "Cohabitating",
    "S": "Prefer not to say",
    "6": "Prefer not to say",
    "7": "Prefer not to say",
    "8": "Prefer not to say",
    "N": None,
}

RELATIONSHIP_STATUS_VALUE_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    RELATIONSHIP_STATUS_VALUE_MAPPING_SCC_TO_BWB
)
RELATIONSHIP_STATUS_VALUE_MAPPING_BWB_TO_SCC.update({"Prefer not to say": "N"})

JOB_TITLE_VALUE_MAPPING_SCC_TO_BWB = {
    "EXEC": "Executive/Manager",
    "PROF": "Professional",
    "TECH": "Technical",
    "SALE": "Sales",
    "OFFI": "Office/Clerical",
    "CRAF": "Craft Worker",
    "OPER": "Operative",
    "LABO": "Laborer",
    "SER": "Service Worker",
    "DATA": None,
}

JOB_TITLE_VALUE_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    JOB_TITLE_VALUE_MAPPING_SCC_TO_BWB
)
JOB_TITLE_VALUE_MAPPING_BWB_TO_SCC.update({"Dependent": "DATA"})

CHIEF_COMPLAINT1_ANSWER_MAPPING_SCC_TO_BWB = {
    "EC": "Stress",
    "ST": "Stress",
    "AA": "Alcohol or Drug use",
    "AX": "Anxiety",
    "CC": "Stress",
    "DP": "Depression",
    "DS": "Stress",
    "DA": "Alcohol or Drug use",
    "ED": "Stress",
    "FA": "Family Issues",
    "FP": "Stress",
    "GL": "Grief or Loss",
    "HY": "Stress",
    "IM": "Stress",
    "IC": "Stress",
    "JO": "Stress",
    "LP": "Stress",
    "MR": "Relationship Issues",
    "MP": "Stress",
    "MA": "Alcohol or Drug use",
    "PT": "Stress",
    "SA": "Stress",
    "DE": "Stress",
}

CHIEF_COMPLAINT1_ANSWER_MAPPING_BWB_TO_SCC = {
    "Stress": "ST",
    "Alcohol or Drug use": "MA",
    "Anxiety": "AX",
    "Depression": "DP",
    "Family Issues": "FA",
    "Grief or Loss": "GL",
    "Relationship Issues": "MR",
}

CHIEF_COMPLAINT2_ANSWER_MAPPING_SCC_TO_BWB = {
    "AX": "Anxiety",
    "DP": "Depression",
    "FI": "Family Issues",
    "GR": "Grief or Loss",
    "RL": "Relationship Issues",
    "ST": "Stress",
    "SU": "Alcohol or Drug use",
}

CHIEF_COMPLAINT2_ANSWER_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    CHIEF_COMPLAINT2_ANSWER_MAPPING_SCC_TO_BWB
)

QUESTION_3A_ANSWER_MAPPING_SCC_TO_BWB = {
    "0": "4",
    "1": "3",
    "2": "2",
    "3": "1",
    "N": None,
}

QUESTION_3A_ANSWER_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    QUESTION_3A_ANSWER_MAPPING_SCC_TO_BWB
)

QUESTION_3B_ANSWER_MAPPING_SCC_TO_BWB = {
    "0": "4",
    "1": "3",
    "2": "2",
    "3": "1",
    "N": None,
}

QUESTION_3B_ANSWER_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    QUESTION_3B_ANSWER_MAPPING_SCC_TO_BWB
)

QUESTION_5A_ANSWER_MAPPING_SCC_TO_BWB = {
    "0": "4",
    "1": "3",
    "2": "2",
    "3": "1",
    "N": None,
}

QUESTION_5A_ANSWER_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    QUESTION_5A_ANSWER_MAPPING_SCC_TO_BWB
)

QUESTION_5B_ANSWER_MAPPING_SCC_TO_BWB = {
    "0": "4",
    "1": "3",
    "2": "2",
    "3": "1",
    "N": None,
}

QUESTION_5B_ANSWER_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    QUESTION_5B_ANSWER_MAPPING_SCC_TO_BWB
)

QUESTION_7A_ANSWER_MAPPING_SCC_TO_BWB = {
    "Y": True,
    "N": False,
}

QUESTION_7A_ANSWER_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    QUESTION_7A_ANSWER_MAPPING_SCC_TO_BWB
)

QUESTION_7B_ANSWER_MAPPING_SCC_TO_BWB = {
    "Y": True,
    "N": False,
}

QUESTION_7B_ANSWER_MAPPING_BWB_TO_SCC = get_reverse_mapping(
    QUESTION_7B_ANSWER_MAPPING_SCC_TO_BWB
)

# There are 5 wellbeingDomainQuestions all of them share same mapping
# SCC to BWB (or vice versa)
# "1" -> "1"
# "2" -> "2"
# ... up to "5" -> "5"
WELLBEING_DOMAIN_QUESTION_SCC_TO_BWB = {str(x): str(x) for x in range(1, 6)}

# questionOutcomeESD1 == number_of_days_missed_work
# questionOutcomeESD2 == number_of_days_less_productive
# SCC store answer to these questions in "String" datatype, while BWB store it in "Integers" (max 30)
# So the mapping goes like: SCC (string) to BWB (integer)
# "0" -> 0
# "1" -> 1
# ... up to "30" -> 30
QUESTION_OUTCOME_ESD_1_NON_DIGIT_VALUES_SCC_TO_BWB = {str(x): x for x in range(31)}
QUESTION_OUTCOME_ESD_2_NON_DIGIT_VALUES_SCC_TO_BWB = {str(x): x for x in range(31)}

# In reverse mapping, BWB need to ensure 2 digits are sent even if the answer is less than 10.
# for example if BWB has value "5" for these answers, then send "05" to SCC.
QUESTION_OUTCOME_ESD_1_NON_DIGIT_VALUES_BWB_TO_SCC = {
    x: str(x).zfill(2) for x in range(0, 31)
}
QUESTION_OUTCOME_ESD_2_NON_DIGIT_VALUES_BWB_TO_SCC = {
    x: str(x).zfill(2) for x in range(0, 31)
}

# Store `None` in BWB, for the following non-integer values from SCC
QUESTION_OUTCOME_ESD_1_NON_DIGIT_VALUES_SCC_TO_BWB.update(
    {
        "CCD": None,
        "CDL": None,
        "DIS": None,
        "FCU": None,
        "INE": None,
        "NAP": None,
        "RET": None,
        "SAH": None,
        "SEA": None,
        "STU": None,
        "UNE": None,
    }
)

# Store `None` in BWB, for the following non-integer values from SCC
QUESTION_OUTCOME_ESD_2_NON_DIGIT_VALUES_SCC_TO_BWB.update(
    {
        "CCD": None,
        "CDL": None,
        "FCU": None,
        "INE": None,
        "NAP": None,
    }
)

GENDER_MAPPING_SCC_TO_BWB = {
    "M": "M",
    "F": "F",
    "U": None,
}

GENDER_MAPPING_BWB_TO_SCC = get_reverse_mapping(GENDER_MAPPING_SCC_TO_BWB)

SCC_KEYS_MAPPING = {
    "gender": GENDER_MAPPING_SCC_TO_BWB,
    "relationshipStatus": RELATIONSHIP_STATUS_VALUE_MAPPING_SCC_TO_BWB,
    "employmentStatus": EMPLOYMENT_STATUS_VALUE_MAPPING_SCC_TO_BWB,
    "jobTitle": JOB_TITLE_VALUE_MAPPING_SCC_TO_BWB,
    "primaryPresentingProblem": CHIEF_COMPLAINT1_ANSWER_MAPPING_SCC_TO_BWB,
    "secondaryPresentingProblem": CHIEF_COMPLAINT2_ANSWER_MAPPING_SCC_TO_BWB,
    "depressionScreenerQuestion3A": QUESTION_3A_ANSWER_MAPPING_SCC_TO_BWB,
    "depressionScreenerQuestion3B": QUESTION_3B_ANSWER_MAPPING_SCC_TO_BWB,
    "anxietyScreenerQuestion5A": QUESTION_5A_ANSWER_MAPPING_SCC_TO_BWB,
    "anxietyScreenerQuestion5B": QUESTION_5B_ANSWER_MAPPING_SCC_TO_BWB,
    "substanceUseQuestion7A": QUESTION_7A_ANSWER_MAPPING_SCC_TO_BWB,
    "substanceUseQuestion7B": QUESTION_7B_ANSWER_MAPPING_SCC_TO_BWB,
    "wellbeingDomainQuestion8": WELLBEING_DOMAIN_QUESTION_SCC_TO_BWB,
    "wellbeingDomainQuestion9": WELLBEING_DOMAIN_QUESTION_SCC_TO_BWB,
    "wellbeingDomainQuestion10": WELLBEING_DOMAIN_QUESTION_SCC_TO_BWB,
    "wellbeingDomainQuestion11": WELLBEING_DOMAIN_QUESTION_SCC_TO_BWB,
    "wellbeingDomainQuestion12": WELLBEING_DOMAIN_QUESTION_SCC_TO_BWB,
    "outcomesESDQuestion1": QUESTION_OUTCOME_ESD_1_NON_DIGIT_VALUES_SCC_TO_BWB,
    "outcomesESDQuestion2": QUESTION_OUTCOME_ESD_2_NON_DIGIT_VALUES_SCC_TO_BWB,
    "memberId": None,
    "emailAddress": None,
    "firstName": None,
    "lastName": None,
    "mdLiveMemberID": None,
    "addressLine1": None,
    "addressLine2": None,
    "addressCity": None,
    "addressStateCode": None,
    "addressZipCode": None,
    "parentCode": None,
    "groupNumber": None,
    "benefitPackage": None,
}
