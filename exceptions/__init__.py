"""Exceptions package."""

from .api_exception import APIException
from .not_authorized import NotAuthorized
from .parameter_missing import ParameterMissing
from .record_invalid import RecordInvalid
from .record_not_found import RecordNotFound
from .unpermitted_parameters import UnpermittedParameters

__all__ = [
    "APIException",
    "NotAuthorized",
    "ParameterMissing",
    "RecordInvalid",
    "RecordNotFound",
    "UnpermittedParameters",
]
