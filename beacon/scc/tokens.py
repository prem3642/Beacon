# -*- coding: utf-8 -*-
import jwt
from django.conf import settings
from django.utils import timezone

ALGORITHM = "HS256"  # type: str


def generate_incoming_scc_auth_token():
    """
    Generates Authorization JWT that ServiceCareConnect (SCC) system uses to connect with BeaconWellBeing (BWB) system.
    The JWT configurations are defined by BWB team.
    """
    now = timezone.now()
    expiry_time = now + timezone.timedelta(minutes=settings.SCC_TOKEN_EXPIRY_IN_MINUTES)
    expiry_timestamp = int(timezone.datetime.timestamp(expiry_time))
    data = {"APP_NAME": "BeaconWellBeing", "exp": expiry_timestamp}
    return jwt.encode(data, settings.INCOMING_SCC_API_SECRET_KEY, algorithm=ALGORITHM)


def is_incoming_scc_token_valid(token):
    """
    Validates the incoming auth token from ServiceCareConnect (SCC).
    """
    try:
        jwt.decode(token, settings.INCOMING_SCC_API_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.DecodeError:
        return False
    except jwt.ExpiredSignatureError:
        return False

    return True


def generate_outgoing_scc_auth_token():
    """
    Generates Authorization JWT that BeaconWellBeing (BWB) System uses to connect with ServiceCareConnect (SCC) system.
    The JWT configurations are defined by Beacon IT Team.
    """
    payload = {"APP_NAME": "BWB"}
    auth_token = jwt.encode(
        payload, settings.OUTGOING_SCC_API_SECRET_KEY, algorithm=ALGORITHM
    )
    return auth_token
