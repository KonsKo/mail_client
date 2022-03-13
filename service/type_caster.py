"""Module for cast data types that depends on SQLAlchemy schema."""
import datetime
import logging
from email.utils import parsedate_to_datetime
from typing import Any, Type

import sqlalchemy as sa
from sqlalchemy.orm import class_mapper

logger = logging.getLogger(__name__)


def cast_datetime(field_value: Any) -> datetime.datetime:
    """
    Cast datetime object.

    Args:
        field_value (Any): field value ti cast

    Returns:
        field_value (datetime.datetime): casted field value

    """
    return parsedate_to_datetime(
        str(field_value),
    ).replace(
        tzinfo=None,
    )


type_resolver = {
    str: str,
    int: int,
    datetime.datetime: cast_datetime,
}


def field_to_type(field_value: Any, required_type: type) -> Any:
    """
    Convert field type.

    Args:
        field_value (Any): field value for convert
        required_type (type): field type to convert

    Returns:
        field value (Any): converted field value

    """
    return type_resolver.get(
        required_type,
        lambda field_v: field_v,
    )(
        field_value,
    )


def cast_types(payload: dict, table: Type[sa.Table]):
    """
    Cast types for payload.

    Args:
        payload (dict): payload to cast types
        table (Type[sa.Table]): db model

    """
    mapper = class_mapper(table)
    for field_name, field_value in payload.items():
        try:
            column = getattr(mapper.columns, field_name)
        except Exception:
            #payload.pop(field_name)
            continue
        payload[field_name] = field_to_type(
            field_value=field_value,
            required_type=column.type.python_type,
        )
