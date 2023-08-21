# -*- coding: utf-8 -*-

# Third Party Stuff
from celery import shared_task
from requests import ConnectionError, RequestException, Timeout

from .services import get_patient_from_mdlive, update_patient_on_mdlive


@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, RequestException, Timeout),
    retry_backoff=3,
    retry_jitter=False,
    max_retries=3,
)
def sync_user_timezone_with_mdlive_timezone_id_task(
    self, patient_id, timezone_id, token
):
    """
    Task to sync timezone with MDLive for the given patient.

    :param patient_id: MDLive ID of the user/patient
    :param timezone_id: Timezone to be updated on MDLive
    :param token: User specific JWT Auth token for MDLive
    """
    patient = get_patient_from_mdlive(patient_id=patient_id, token=token)
    patient_profile = patient.get("patient_profile", None)
    timezone_id_on_mdlive = patient_profile.get("us_time_zone_id", None)
    if timezone_id_on_mdlive != timezone_id:
        data_to_update = {"us_time_zone_id": timezone_id}
        update_patient_on_mdlive(
            patient_id=patient_id,
            data_to_update=data_to_update,
            token=token,
        )
