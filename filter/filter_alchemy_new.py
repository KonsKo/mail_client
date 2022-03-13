"""Module for building SQLAlchemy filters."""
import logging
from typing import Any, Callable, Type, List
import datetime
from email.utils import parsedate_to_datetime

import sqlalchemy as sa
from sqlalchemy.orm import class_mapper

import db.exceptions as db_exc

logger = logging.getLogger(__name__)


def cast_datetime(field_value: Any):
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
        column = getattr(mapper.columns, field_name)
        payload[field_name] = field_to_type(
            field_value=field_value,
            required_type=column.type.python_type,
        )


class Filter(object):
    """Filter class."""

    def __init__(self):
        """Init class instance."""
        self.filters = []

    def __str__(self) -> str:
        """
        Convert list elements to readable expressions.

        Returns:
            expression (str): readable expression

        """
        return str(
            sum(self.filters),
        )

    def add(self, expression: sa.sql.expression.BinaryExpression):
        """
        Add filter-like expression to filter list.

        Args:
            expression (a.sql.expression.BinaryExpression): expression to
                add to filters

        """
        self.filters.append(
            expression,
        )

    def list_filters(self) -> list:
        """
        Return filters.

        Returns:
            filters (list): filters

        """
        return self.filters


# noinspection PyTypeChecker
class FilterBuilder(object):   # noqa:WPS214
    """Filter builder class."""

    white_eq = {str, int, datetime.datetime, bool}
    white_like = {str}
    white_compare = {int, datetime.datetime}
    white_in = {str, int, datetime.datetime}

    def __init__(self, table: Type[sa.Table]):
        """
        Init class instance.

        Args:
            table (Type[sa.Table]): table to create filters for

        """
        self.table: Type[sa.Table] = table
        self.mapper = class_mapper(self.table)
        self.filter = Filter()
        self.operations = {
            'eq': self._add_eq,
            '=': self._add_eq,
            'from': self._add_ge,
            'to': self._add_le,
            'T': self._add_term,
            #'ne': self._add_ne,
            #'gt': self._add_gt,
            #'lt': self._add_lt,
            #'ge': self._add_ge,
            #'le': self._add_le,
            #'like': self._add_like,
            #'nlike': self._add_not_like,
            #'ilike': self._add_i_like,
            #'nilike': self._add_not_i_like,
            #'in': self._add_in,
        }

    def build(self, filter_set: List[dict]):
        """
        Create filters.

        """
        for filter_entity in filter_set:
            if filter_entity['field_names']:
                field_name = filter_entity['field_names']
            else:
                field_name = filter_entity['name'].split('_')[0]
            self.resolve_operator(
                operator=filter_entity.get('op'),
            )(
                field_name,
                filter_entity['field_value'],
            )

    def resolve_operator(self, operator: str) -> Callable:
        """
        Check filter operator for existence and return related method.

        Args:
            operator (str): filter operator

        Returns:
            method (Callable): operator-related method

        Raises:
            OperatorDoesNotExist: if operator does not exist

        """
        try:
            return self.operations[operator]
        except Exception as exception:
            logger.exception(
                'Filter creating: operator does not exists: {0}'.format(
                    exception,
                ),
            )
            raise db_exc.OperatorDoesNotExist

    def get_column(
        self,
        field_name: str,
        white_types: tuple,
    ) -> sa.sql.schema.Column:
        """
        Get alchemy column instance from model.

        Args:
            field_name (str): field name to get column instance
            white_types (tuple): white data types for filter operator

        Raises:
            FieldDoesNotExists: if no column for filed_name
            FilterOperatorNotAllowed: if operator not allowed

        Returns:
            column (sa.sql.schema.Column): column

        """
        try:
            column = getattr(self.mapper.columns, field_name)
        except Exception as exception:
            logger.exception(
                'Filter creating: field does not exists: {0}'.format(
                    exception,
                ),
            )
            raise db_exc.FieldDoesNotExists   # TODO ignor inexistent column?
        if column.type.python_type not in white_types:
            raise db_exc.FilterOperatorNotAllowed
        return column

    def get_allowed_operations(self) -> list:
        """
        Get list of allowed operations.

        Returns:
            operations (list): list of operations

        """
        return list(self.operations.keys())

    def _add_eq(self, field_name, field_value):
        column = self.get_column(field_name, self.white_eq)
        self.filter.add(
            column == field_to_type(field_value, column.type.python_type),
        )

    def _add_ne(self, field_name, field_value):
        column = self.get_column(field_name, self.white_eq)
        self.filter.add(
            column != field_to_type(field_value, column.type.python_type),
        )

    def _add_gt(self, field_name, field_value):
        column = self.get_column(field_name, self.white_compare)
        self.filter.add(
            column > field_to_type(field_value, column.type.python_type),
        )

    def _add_lt(self, field_name, field_value):
        column = self.get_column(field_name, self.white_compare)
        self.filter.add(
            column < field_to_type(field_value, column.type.python_type),
        )

    def _add_ge(self, field_name, field_value):
        column = self.get_column(field_name, self.white_compare)
        self.filter.add(
            column >= field_to_type(field_value, column.type.python_type),
        )

    def _add_le(self, field_name, field_value):
        column = self.get_column(field_name, self.white_compare)
        self.filter.add(
            column <= field_to_type(field_value, column.type.python_type),
        )

    def _add_in(self, field_name, field_value):
        column = self.get_column(field_name, self.white_in)
        self.filter.add(
            column.in_(
                [
                    field_to_type(
                        fv,
                        column.type.python_type,
                    ) for fv in field_value
                ],
            ),
        )

    def _add_like(self, field_name, field_value):
        column = self.get_column(field_name, self.white_like)
        self.filter.add(
            column.like(
                '%{0}%'.format(
                    str(field_value),
                ),
            ),
        )

    def _add_i_like(self, field_name, field_value):
        column = self.get_column(field_name, self.white_like)
        self.filter.add(
            column.ilike(
                '%{0}%'.format(
                    str(field_value),
                ),
            ),
        )

    def _add_not_like(self, field_name, field_value):
        column = self.get_column(field_name, self.white_like)
        self.filter.add(
            column.not_like(
                '%{0}%'.format(
                    str(field_value),
                ),
            ),
        )

    def _add_not_i_like(self, field_name, field_value):
        column = self.get_column(field_name, self.white_like)
        self.filter.add(
            column.not_ilike(
                '%{0}%'.format(
                    str(field_value),
                ),
            ),
        )

    #def _build_or(self, filter_set: dict):  TODO
    #    filter_or = FilterBuilder(self.table)
    #    filter_or.build(filter_set=filter_set)
    #    self.filter.add(
    #        sa.or_(
    #            *filter_or.filter.list_filters(),
    #        ),
    #    )

    #def _build_and(self, filter_set: dict):  TODO
    #    filter_and = FilterBuilder(self.table)
    #    filter_and.build(filter_set=filter_set)
    #    self.filter.add(
    #        sa.and_(
    #            *filter_and.filter.list_filters(),
    #        ),
    #    )

    def _add_term(self, field_name: list, field_value):
        tmp = []
        for f_name in field_name:
            column = self.get_column(f_name, self.white_like)
            tmp.append(
                column.like(
                    '%{0}%'.format(
                        str(field_value),
                    ),
                ),
            )
        self.filter.add(
            sa.or_(*tmp),
        )
