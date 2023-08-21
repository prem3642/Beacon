# -*- coding: utf-8 -*-
# Third Party Stuff
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList


class BaseException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Unexpected error")

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail


class NotFound(BaseException, Http404):
    """Exception used for not found objects."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("Not found.")


class NotSupported(BaseException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = _("Method not supported for this endpoint.")


class BadRequest(BaseException):
    """Exception used on bad arguments detected on api view."""

    default_detail = _("Wrong arguments.")


class WrongArguments(BadRequest):
    """Exception used on bad arguments detected on service. This is same as `BadRequest`."""

    default_detail = _("Wrong arguments.")


class RequestValidationError(BadRequest):
    default_detail = _("Data validation error")


class PermissionDenied(exceptions.PermissionDenied):
    """Compatibility subclass of restframework `PermissionDenied` exception."""

    pass


class IntegrityError(exceptions.ValidationError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("Integrity Error for wrong or invalid arguments")


class CognitoAuthenticationFailedError(exceptions.ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Authentication Failed.")
    error_type = "ValidationError"

    def __init__(self, detail=None, code=None):
        """
        The constructor overrides constructor of "rest_framework.exceptions.ValidationError" class, so that we can use
        our custom "_get_error_details" function.
        """
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        self.detail = self._get_error_details(detail, code)

    def _get_error_details(self, data, default_code=None):
        """
        Descend into a nested data structure, forcing any lazy translation strings or strings into `ErrorDetail`.

        The method replicates "rest_framework.exceptions._get_error_details" as the original function
        converts all data types to strings, but we want to avoid converting "int" to "strings".
        """
        if isinstance(data, (list, tuple)):
            ret = [self._get_error_details(item, default_code) for item in data]
            if isinstance(data, ReturnList):
                return ReturnList(ret, serializer=data.serializer)
            return ret
        elif isinstance(data, dict):
            ret = {
                key: self._get_error_details(value, default_code)
                for key, value in data.items()
            }
            if isinstance(data, ReturnDict):
                return ReturnDict(ret, serializer=data.serializer)
            return ret

        if isinstance(data, int):
            return data

        text = force_str(data)
        code = getattr(data, "code", default_code)
        return ErrorDetail(text, code)


class SccIntegrityError(IntegrityError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("Integrity Error for wrong or invalid arguments")
    error_type = "IntegrityError"

    def __init__(self, detail=None, code=None):
        """
        The constructor overrides constructor of "rest_framework.exceptions.ValidationError" class, so that we can use
        our custom "_get_error_details" function.
        """
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        self.detail = self._get_error_details(detail, code)

    def _get_error_details(self, data, default_code=None):
        """
        Descend into a nested data structure, forcing any lazy translation strings or strings into `ErrorDetail`.

        The method replicates "rest_framework.exceptions._get_error_details" because the original function was
        converting all values to Strings including None to "None". But in SCC discrepancy error message if the value for
        any field is None, then to avoid confusion we should return those None values
        as `null` in JSON instead of string of "None".
        """
        if isinstance(data, (list, tuple)):
            ret = [self._get_error_details(item, default_code) for item in data]
            if isinstance(data, ReturnList):
                return ReturnList(ret, serializer=data.serializer)
            return ret
        elif isinstance(data, dict):
            ret = {
                key: self._get_error_details(value, default_code)
                for key, value in data.items()
            }
            if isinstance(data, ReturnDict):
                return ReturnDict(ret, serializer=data.serializer)
            return ret

        if data is None:
            return None

        text = force_str(data)
        code = getattr(data, "code", default_code)
        return ErrorDetail(text, code)


class PreconditionError(BadRequest):
    """Error raised on precondition method on viewset."""

    default_detail = _("Precondition error")


class NotAuthenticated(exceptions.NotAuthenticated):
    """Compatibility subclass of restframework `NotAuthenticated` exception."""

    pass


class NotVerified(exceptions.ValidationError):
    """Compatibility subclass of restframework `NotAuthenticated` exception."""

    status_code = 420


def parse_field_errors(field, error_msg, error_values, depth=0):
    # We only parse errors upto 10 nested serializers
    if depth is not None:
        assert depth >= 0, "'depth' may not be negative."
        assert depth <= 10, "'depth' may not be greater than 10."

    errors = []

    if isinstance(error_msg, dict):
        for error_msg_key, error_msg_values in list(error_msg.items()):
            for msg in error_msg_values:
                errors.append(
                    {
                        "field": field,
                        "message": None,
                        "errors": parse_field_errors(
                            error_msg_key, msg, error_values, depth=depth + 1
                        ),
                    }
                )
    else:
        errors.append(
            {
                "field": error_msg
                if error_msg and error_values and type(error_values) != list
                else field,
                "message": " ".join(error_values[error_msg])
                if error_msg and error_values and type(error_values) != list
                else error_msg,
            }
        )

    return errors


def format_exception(exc):
    if hasattr(exc, "error_type") and exc.error_type:
        error_type = exc.error_type
    else:
        error_type = exc.__class__.__name__

    detail = {
        "errors": [],
        "error_type": error_type,
    }
    if isinstance(exc.detail, dict):
        for error_key, error_values in list(exc.detail.items()):
            for error_msg in error_values:
                # Special Case for model clean
                if error_key == "non_field_errors":
                    detail["errors"].append(
                        {
                            "message": error_msg,
                        }
                    )
                else:
                    detail["errors"] = detail["errors"] + parse_field_errors(
                        error_key, error_msg, error_values
                    )
    elif isinstance(exc.detail, list):
        for error_msg in exc.detail:
            detail["errors"].append(
                {
                    "message": error_msg,
                }
            )
    else:
        detail["errors"].append(
            {
                "message": force_str(exc.detail),
            }
        )

    return detail


def exception_handler(exc, context=None):
    """Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's builtin `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["X-Throttle-Wait-Seconds"] = "%d" % exc.wait

        detail = format_exception(exc)
        return Response(detail, status=exc.status_code, headers=headers)

    elif isinstance(exc, Http404):
        return Response(
            {"error_type": exc.__class__.__name__, "errors": [{"message": str(exc)}]},
            status=status.HTTP_404_NOT_FOUND,
        )

    elif isinstance(exc, DjangoPermissionDenied):
        return Response(
            {"error_type": exc.__class__.__name__, "errors": [{"message": str(exc)}]},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Note: Unhandled exceptions will raise a 500 error.
    return None


class CeleryTaskFailed(Exception):
    """
    Exception to be used to explicitly fail a celery task by raising an exception.

    It is useful in case the task has `celery.shared_task` decorator, such that, raising any exception other then the
    ones specified in the `autoretry_for` parameter would result in the task failure as no further retry will occur.
    """

    pass
