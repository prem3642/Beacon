# -*- coding: utf-8 -*-
# Third Party Stuff
from json import JSONDecodeError

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from requests import ConnectionError, RequestException, Timeout

from beacon.base.exceptions import CeleryTaskFailed

from . import services


def format_error(error_json=None, exception=None):
    error_response = {}
    if error_json:
        error_response.update({"Error": error_json})
    if exception:
        error_response.update({"Exception": str(exception)})
    return error_response


@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, Timeout),
    retry_backoff=settings.SCC_RETRY_BACKOFF_FACTOR,
    retry_jitter=False,
    max_retries=3,
)
def send_user_data_to_scc_task(self, user_id, request):
    def handle_exception(self, exc, user_id, request):
        if (
            isinstance(exc, RequestException)
            and hasattr(exc, "response")
            and hasattr(exc.response, "json")
        ):
            # Create failure log If a valid error json has been received from SCC system.
            try:
                error_resp = format_error(error_json=exc.response.json(), exception=exc)
            except JSONDecodeError as exc:
                error_resp = format_error(exception=exc)

            services.create_scc_api_log(
                user_id=user_id,
                request=request,
                response=error_resp,
                is_successful=False,
                is_incoming=False,
            )
            raise CeleryTaskFailed(f"Error received from SCC {error_resp}")
        elif self.request.retries >= self.max_retries:
            # Create failure log if max retries are done
            error_resp = format_error(exception=exc)
            services.create_scc_api_log(
                user_id=user_id,
                request=request,
                response=error_resp,
                is_successful=False,
                is_incoming=False,
            )
            raise CeleryTaskFailed(f"Exceeded max retries {error_resp}")
        else:
            raise exc

    scc_api_client = services.get_scc_api_client()
    try:
        response_json = scc_api_client.send_new_user_registration(request)
        services.create_scc_api_log(
            user_id=user_id,
            request=request,
            response=response_json,
            is_successful=True,
            is_incoming=False,
        )
        user = get_user_model().objects.filter(id=user_id).first()
        user.connects_mbr_id = response_json.get("memberId")
        user.save()
        return response_json
    except (RequestException, ConnectionError, Timeout) as e:
        handle_exception(self, exc=e, user_id=user_id, request=request)
