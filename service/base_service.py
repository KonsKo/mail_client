"""Base service module."""
import datetime
import logging
from email.utils import format_datetime
from typing import Optional, Type

import sqlalchemy as sa
from aiohttp import web
from repository.irepository import IRepository
from sqlalchemy.orm.decl_api import DeclarativeMeta

from service.iservice import IService
from service.mapper import BodyCreate, BodyDelete, BodyUpdate
from service.type_caster import cast_types
from filter.base_filter import BaseAlchemyFilter

logger = logging.getLogger(__name__)


class BaseService(IService):  # noqa:WPS214
    """Base Service class."""

    def __init__(
        self,
        repository: IRepository,
        filter_class: Type[BaseAlchemyFilter],
        app: web.Application,
    ):
        """
        Init class instance.

        Args:
            repository (IRepository): repository instance
            app (web.Application): aiohttp application
            filter_class (Type[BaseAlchemyFilter]): static filter class

        """
        self.repo = repository
        self.app = app
        if filter_class:
            self.filter = filter_class()

    async def create(
        self,
        request_body: dict,
        user_id: Optional[int] = None,
    ) -> dict:
        """
        Run create method.

        We suppose that table has user-related field, but if table has not
            such field than it will be ignored during creation

        Args:
            request_body (dict): request body.
            user_id (int): current user id

        Returns:
            result (dict): result of repo command

        Raises:
            KeyError: if request body has wrong mapping

        """
        try:
            request_body = BodyCreate(**request_body)
        except Exception as exception:
            logger.exception(exception)
            raise KeyError
        request_body.payload.update(
            {'user': user_id},
        )
        cast_types(
            payload=request_body.payload,
            table=self.repo.table,
        )
        return await self.repo.insert(
            payload=request_body.payload,
        )

    async def update(
        self,
        request_body: dict,
        user_id: Optional[int] = None,
        entity_id: Optional[int] = None,
    ) -> dict:
        """
        Run update method.

        Args:
            request_body (dict): values to update
            user_id (int): current user id
            entity_id (int): letter id

        Returns:
            result (dict): result of repo command

        Raises:
            KeyError: if request body has wrong mapping

        """
        filter_set = {}  # TODO
        try:
            request_body = BodyUpdate(**request_body)
        except Exception as exception:
            logger.exception(exception)
            raise KeyError
        if request_body.filter_set:
            filter_set.update(
                request_body.filter_set,
            )
        # TODO make filter
        return await self.repo.update(
            where=self.filter.create_alchemy_filters(
                query_dict=filter_set,
            ),
            payload=request_body.payload,
        )

    async def delete(
        self,
        request_body: Optional[dict] = None,
        entity_id: Optional[int] = None,
    ) -> dict:
        """
        Run delete method.

        Args:
            request_body (dict): values to update
            entity_id (Optional[int]): letter id

        Returns:
            result (dict): result of repo command

        Raises:
            KeyError: if request body has wrong mapping

        """
        filter_set = {}  # TODO
        try:
            request_body = BodyDelete(**request_body)
        except Exception as exception:
            logger.exception(exception)
            raise KeyError
        if request_body.filter_set:
            filter_set.update(
                request_body.filter_set,
            )
        elif entity_id:
            filter_set.update(
                {'id__eq': entity_id},
            )
        return await self.repo.delete(
            where=self.filter.create_alchemy_filters(
                query_dict=filter_set,
            ),
        )

    async def retrieve(
        self,
        entity_id: Optional[int] = None,
        url_query: Optional[dict] = None,
        user_id: Optional[int] = None,
        bake: str = 'all',
    ) -> dict:
        """
        Run select method.

        Args:
            entity_id (Optional[int]): letter id
            url_query(Optional[dict]): url query
            bake (str): form-factor for return
            user_id (int): current user id

        Returns:
            result (dict): result of repo command

        Raises:
            AttributeError: if any data was not provided

        """
        if any([entity_id, url_query, user_id]):
            filter_set = {}
            if user_id:
                filter_set.update(
                    {'user': user_id},
                )
            if entity_id:
                filter_set.update(
                    {'id': entity_id},
                )
            elif url_query:
                filter_set.update(
                    url_query,
                )
            if bake == 'first':
                return self.to_dict(
                    await self.repo.select_first(
                        where=self.filter.create_alchemy_filters(
                            query_dict=filter_set,
                        ),
                        order_by=self.filter.filter_class.order_by,
                        offset=self.filter.filter_class.offset,
                        limit=self.filter.filter_class.limit,
                    ),
                )
            return self.serialize(
                await self.repo.select(
                    where=self.filter.create_alchemy_filters(
                        query_dict=filter_set,
                    ),
                    order_by=self.filter.filter_class.order_by,
                    offset=self.filter.filter_class.offset,
                    limit=self.filter.filter_class.limit,
                ),
            )
        raise AttributeError

    async def send_email(self, *args, **kwargs):
        """
        Send email.

        Args:
            args: arguments
            kwargs: key arguments

        Raises:
            NotImplementedError: always

        """
        raise NotImplementedError

    def serialize(self, raw_data: list) -> dict:
        """
        Convert data sequence to json-format.

        Args:
            raw_data(list): data to convert

        Returns:
            serialized (dict): converted sequence

        """
        serialized_seq = []
        for element in raw_data:
            serialized_seq.append(
                self.to_dict(to_serialize=element),
            )
        return {
            'data': serialized_seq,
        }

    @staticmethod
    def to_dict(to_serialize: DeclarativeMeta) -> dict:   # noqa:WPS602
        """
        Convert data entity to json-format.

        Args:
            to_serialize (DeclarativeMeta): data to convert

        Returns:
            serialized (dict): converted entity

        """
        serialized = {}
        for attr in sa.inspect(to_serialize).mapper.column_attrs:
            attr_val = getattr(to_serialize, attr.key)
            if not attr_val:
                attr_val = ''
            if isinstance(attr_val, datetime.datetime):
                attr_val = format_datetime(attr_val)
            serialized[attr.key] = attr_val
        return serialized

    """
    async def download_files(self):  # TODO move to service
        if 'multipart/form-data' in self.request.headers.get('Content-Type'):
            multipart = await self.request.multipart()
            while not multipart.at_eof():
                part = await multipart.next()  # noqa:B305 , aiohttp usage
                if not part:
                    break
                with open(part.filename, 'wb') as new_file:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        new_file.write(chunk)
                    new_file.seek(0)
    """