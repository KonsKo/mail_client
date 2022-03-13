"""Exceptions module."""
import re


class TableDoesNotExists(Exception):
    """Exception raised if table doesn't exist for schema."""


class FieldDoesNotExists(Exception):
    """Exception raised if field doesn't exist for table."""


class FilterOperatorNotAllowed(Exception):
    """Exception raised if wrong filter operator."""


class OperatorDoesNotExist(Exception):
    """Exception raised if operator does not exist."""


def make_error_response(exception: Exception) -> str:
    orig = str(exception.__dict__.get('orig'))
    pattern = r'DETAIL:\s\s(.+)'
    try:
        return re.search(
            pattern=pattern,
            string=orig,
        ).group(1)
    except Exception:
        return str(exception)

