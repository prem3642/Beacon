# -*- coding: utf-8 -*-
import pytz
from extended_choices import Choices

from beacon.mdlive.constants import TIMEZONE_TO_MDLIVE_ID_MAP

STATE_CHOICES = [
    ("AK", "Alaska"),
    ("AL", "Alabama"),
    ("AR", "Arkansas"),
    ("AZ", "Arizona"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DC", "District of Columbia"),
    ("DE", "Delaware"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("IA", "Iowa"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("MA", "Massachusetts"),
    ("MD", "Maryland"),
    ("ME", "Maine"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MO", "Missouri"),
    ("MS", "Mississippi"),
    ("MT", "Montana"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("NE", "Nebraska"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NV", "Nevada"),
    ("NY", "New York"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("PR", "Puerto Rico"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VA", "Virginia"),
    ("VT", "Vermont"),
    ("WA", "Washington"),
    ("WI", "Wisconsin"),
    ("WV", "West Virginia"),
    ("WY", "Wyoming"),
]


GENDER_CHOICES = [("M", "Male"), ("F", "Female"),("P",'Prefer Not to say')]
RELATIONSHIP_CHOICES = [
    ("Self", "Self"),
    ("Spouse", "Spouse"),
    ("Child", "Child"),
    ("Other Adult", "Other Adult"),
]
EMPLOYMENT_STATUS_CHOICES = [
    ("Full Time", "Full Time"),
    ("Part Time", "Part Time"),
    ("Terminated", "Terminated"),
    ("Medical Leave", "Medical Leave"),
    ("Retired", "Retired"),
    ("Disciplinary Leave", "Disciplinary Leave"),
    ("Laid Off", "Laid Off"),
    ("Disability/Worker’s Compensation", "Disability/Worker’s Compensation"),
    ("Dependent", "Dependent"),
]
RELATIONSHIP_STATUS_CHOICES = [
    ("Never Married", "Never Married"),
    ("Married", "Married"),
    ("Divorced", "Divorced"),
    ("Cohabitating", "Cohabitating"),
    ("Separated", "Separated"),
    ("Widowed", "Widowed"),
    ("Prefer not to say", "Prefer not to say"),
]
JOB_TITLE_CHOICE = [
    ("Executive/Manager", "Executive/Manager"),
    ("Professional", "Professional"),
    ("Technical", "Technical"),
    ("Sales", "Sales"),
    ("Office/Clerical", "Office/Clerical"),
    ("Craft Worker", "Craft Worker"),
    ("Operative", "Operative"),
    ("Laborer", "Laborer"),
    ("Service Worker", "Service Worker"),
    ("Dependent", "Dependent"),
]

USER_DEACTIVATION_CHOICES = Choices(
    ("CLIENT_TERMINATED", "client_terminated", "Client terminated"),
    ("ELIGIBILITY_EXPIRED", "eligibility_expired", "Eligibility expired"),
    ("SESSION_OVERUSE", "session_overuse", "Session overuse"),
    ("DUPLICATE_ACCOUNT", "duplicate_account", "Duplicate account"),
    ("REGISTERED_IN_ERROR", "registered_in_error", "Registered in error"),
)

# Initially, added as choices for field `User.timezone`, but later removed
# as we learnt that Beacon team needs only a few timezones.
TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

# These allowed timezone choices are in sync with what MDLive expects.
ALLOWED_TIMEZONES = TIMEZONE_TO_MDLIVE_ID_MAP.keys()

# Only these timezones are allowed from FE for now.
CURRENTLY_ALLOWED_TIMEZONE_CHOICES = tuple(zip(ALLOWED_TIMEZONES, ALLOWED_TIMEZONES))
