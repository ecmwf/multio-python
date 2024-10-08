from enum import IntEnum, unique

from .lib import lib


@unique
class ResultType(IntEnum):
    SUCCESS = lib.MULTIO_SUCCESS
    ERROR_ECKIT_EXCEPTION = lib.MULTIO_ERROR_ECKIT_EXCEPTION
    ERROR_GENERAL_EXCEPTION = lib.MULTIO_ERROR_GENERAL_EXCEPTION
    ERROR_UNKNOWN_EXCEPTION = lib.MULTIO_ERROR_UNKNOWN_EXCEPTION


SUCCESS = ResultType.SUCCESS
ERROR_ECKIT_EXCEPTION = ResultType.ERROR_ECKIT_EXCEPTION
ERROR_GENERAL_EXCEPTION = ResultType.ERROR_GENERAL_EXCEPTION
ERROR_UNKNOWN_EXCEPTION = ResultType.ERROR_UNKNOWN_EXCEPTION
