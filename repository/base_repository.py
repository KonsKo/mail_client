"""Base repository for SQLAlchemy and PostgreSQL."""
import logging
from typing import List, Optional, Union

import sqlalchemy as sa
from aiohttp import web
from db.exceptions import make_error_response
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.sql.elements import BinaryExpression

from repository.irepository import IRepository

logger = logging.getLogger(__name__)


DEFAULT_OFFSET = 0
DEFAULT_LIMIT = 50


class BaseRepository(IRepository):
    """Base repository class."""

    def __init__(self, app: web.Application, table: sa.Table):
        """
        Init class instance.

        Args:
            table (sa.Table): table instance to processing
            app (web.Application): aiohttp app

        """
        self.table = table
        self.db_engine = app['db']

    async def insert(
        self,
        payload: Union[str, dict, sa.Column],
    ) -> dict:
        """
        Insert data to table.

        It can insert either single row (new_values={'par1': 1, 'par2': 2})
        or multy value (new_values=[{'par1': 1}, {'par1': 2}])

        Args:
            payload (Union[str, dict, sa.Column]): values to insert

        Returns:
            result (dict): command result

        """
        stmt = sa.insert(
           self.table,
        )
        async with self.db_engine.session_maker() as session:
            async with session.begin():
                try:
                    result_insert = await session.execute(
                        stmt,
                        payload,
                    )
                except Exception as exception:
                    logger.exception(
                        'Inserting was failed. {0}'.format(
                            exception,
                        ),
                    )
                    return {
                        'error': make_error_response(exception),
                    }
        return {
            'inserted_pk': result_insert.inserted_primary_key[0],
        }

    async def update(
        self,
        payload: dict,
        where: List[BinaryExpression],
    ) -> dict:
        """
        Update data.

        Args:
            where (List[BinaryExpression]): filters
            payload (dict): values to update

        Returns:
            result (dict): command result

        """
        stmt = sa.update(
           self.table,
        ).values(
            payload,
        ).where(
            *where,
        ).execution_options(
            synchronize_session='fetch',
        )
        async with self.db_engine.session_maker() as session:
            async with session.begin():
                try:
                    result_update = await session.execute(stmt)
                except Exception as exception:
                    logger.exception(
                        'Updating was failed. {0}'.format(
                            exception,
                        ),
                    )
                    return {
                        'error': make_error_response(exception),
                    }
        return {
            'updated_rows': result_update.rowcount,
        }

    async def delete(
        self,
        where: List[BinaryExpression],
    ) -> dict:
        """
        Delete data.

        Args:
            where (List[BinaryExpression]): filters

        Returns:
            result (dict): command result

        """
        stmt = sa.delete(
           self.table,
        ).where(
            *where,
        ).execution_options(
            synchronize_session='fetch',
        )
        async with self.db_engine.session_maker() as session:
            async with session.begin():
                try:
                    result_delete = await session.execute(stmt)
                except Exception as exception:
                    logger.exception(
                        'Updating was failed. {0}'.format(
                            exception,
                        ),
                    )
                    return {
                        'error': make_error_response(exception),
                    }
        return {
            'deleted_rows': result_delete.rowcount,
        }

    async def select(
        self,
        where: Optional[list] = None,
        order_by: Optional[list] = None,
        offset: int = DEFAULT_OFFSET,
        limit: int = DEFAULT_LIMIT,
    ) -> List[DeclarativeMeta]:
        """
        Return `All` selected rows.

        Args:
            where (Optional[list]): filters,
            order_by (Optional[list]): order for filtering,
            offset (int): offset,
            limit (int): limit,

        Returns:
            selected (List[DeclarativeMeta]): selected rows

        """
        selected = await self._select_scalars(
            where=where,
            order_by=order_by,
            offset=offset,
            limit=limit,
        )
        try:
            return selected.all()
        except Exception as exception:
            logger.exception(
                'Select `all` was failed. {0}'.format(
                    exception,
                ),
            )

    async def select_first(
        self,
        where: Optional[list] = None,
        order_by: Optional[list] = None,
        offset: int = DEFAULT_OFFSET,
        limit: int = DEFAULT_LIMIT,
    ) -> DeclarativeMeta:
        """
        Return `First` selected row.

        Args:
            where (Optional[list]): filters,
            order_by (Optional[list]): order for filtering,
            offset (int): offset,
            limit (int): limit,

        Returns:
            selected (DeclarativeMeta): selected row

        """
        selected = await self._select_scalars(
            where=where,
            order_by=order_by,
            offset=offset,
            limit=limit,
        )
        try:
            return selected.first()
        except Exception as exception:
            logger.exception(
                'Select `first` was failed. {0}'.format(
                    exception,
                ),
            )

    async def _select_scalars(
        self,
        where: Optional[list] = None,
        order_by: Optional[list] = None,
        offset: int = DEFAULT_OFFSET,
        limit: int = DEFAULT_LIMIT,
    ):
        """
        Select data.

        Args:
            where (Optional[list]): filters,
            order_by (Optional[list]): order for filtering,
            offset (int): offset,
            limit (int): limit,

        Returns:
            selected result

        """
        stmt = sa.select(
           self.table,
        ).offset(
            offset,
        ).limit(
            limit,
        )
        if where:
            stmt = stmt.filter(*where)
        if order_by:
            stmt = stmt.order_by(
                *[sa.text(ob) for ob in order_by],
            )
        async with self.db_engine.session_maker() as session:
            async with session.begin():
                try:
                    select_result = await session.execute(stmt)
                except Exception as exception:
                    logger.exception(
                        'Select was failed. {0}'.format(
                            exception,
                        ),
                    )
        return select_result.scalars()
