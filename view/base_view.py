"""Class-based aiohttp views."""
import logging
from typing import Optional, Type

import sqlalchemy as sa
from aiohttp import web
from aiohttp.formdata import MultiDict
from auth.policy import get_current_user_id
from controller.base_controller import BaseController
from filter.base_filter import BaseAlchemyFilter
from repository.base_repository import BaseRepository
from service.base_service import BaseService

logger = logging.getLogger(__name__)


class BaseProcessingView(web.View):
    """
    Base view.

    View only do initialisation and declare additional methods.

    You should declare all necessary methods for handling request.
    Methods must have names as http methods (`get`, `post`, etc. )

    """

    _controller: Type[BaseController] = BaseController
    _repository: Type[BaseRepository] = BaseRepository
    _service: Type[BaseService] = BaseService
    _tabel: Optional[sa.Table] = None
    _filter: Optional[BaseAlchemyFilter] = None

    def __init__(self, request: web.Request):
        """
        Init class instance.

        Args:
            request (web.Request): aiohttp request.

        Raises:
            NotImplementedError: if table was not provided

        """
        super().__init__(request)
        if not self._tabel:
            raise NotImplementedError
        self.repository = self._repository(
            app=self.request.app,
            table=self._tabel,
        )
        self.service = self._service(
            repository=self.repository,
            filter_class=self._filter,
            app=self.request.app,
        )
        self.controller = self._controller(self.service)

    @property
    async def current_user(self) -> int:
        """
        Get current user id.

        Returns:
            user_id (int): current user id

        """
        return await get_current_user_id(self.request)

    async def prepare_body(self) -> dict:
        """
        Get request body.

        Returns:
            body (dict): request body

        Raises:
            HTTPBadRequest: if error getting body

        """
        if self.request.can_read_body:
            try:
                return await self.request.json()
            except Exception as exception1:
                logger.exception(exception1)
                raise web.HTTPBadRequest()
        else:
            return {}

    @staticmethod
    def _url_query_to_dict(query: MultiDict) -> dict:  # TODO to whole remove
        """
        Create regular dict-object from MultiDictProxy.

        If MultiDictProxy has many equal keys return first one

        Args:
            query (MultiDict): url query data from request

        Returns:
            query_dict (dict): converted query data

        """
        query_dict = {}
        for key_query in query.keys():
            query_dict[key_query] = query.get(key_query)
        return query_dict


class BaseEntityView(BaseProcessingView):
    """Entity view class. Required primary key attribute (`id`)."""

    async def get(self) -> web.Response:
        """
        Handle Entity GET request.

        Returns:
            response (web.Response): response

        Raises:
            AttributeError: if `pk` was not provided

        """
        entity_id = self.request.match_info.get('id')
        if not entity_id:
            raise AttributeError
        url_query = self.request.rel_url.query

        try:
            response = await self.controller.process_entity_get(
                user_id=await self.current_user,
                entity_id=entity_id,
                url_query=self._url_query_to_dict(url_query),
            )
        except Exception as exception:
            logger.exception(exception)
            return web.HTTPBadRequest()

        return web.json_response(
            response,
        )

    async def post(self) -> web.Response:
        """
        Handle Entity POST request.

        Returns:
            response (web.Response): response

        Raises:
            AttributeError: if `pk` was not provided

        """
        entity_id = self.request.match_info.get('id')
        body = await self.prepare_body()
        if not entity_id:
            raise AttributeError
        try:
            response = await self.controller.process_entity_post(
                user_id=await self.current_user,
                request_body=body,
                entity_id=entity_id,
                command=self.request.match_info.get('command'),
            )
        except Exception as exception:
            logger.exception(exception)
            return web.HTTPBadRequest()
        return web.json_response(
            response,
        )


class BaseManyView(BaseProcessingView):
    """Many view class. Required primary key attribute (`id`)."""

    async def get(self) -> web.Response:
        """
        Handle GET request.

        If there is neither `entity_id` nor `url_query`
        it returns response filtered by `user id`

        Returns:
            response (web.Response): response

        """
        url_query = self.request.rel_url.query
        try:
            response = await self.controller.process_get(
                user_id=await self.current_user,
                url_query=self._url_query_to_dict(url_query),
            )
        except Exception as exception:
            logger.exception(exception)
            return web.HTTPBadRequest()

        return web.json_response(
           response,
        )

    async def post(self) -> web.Response:
        """
        Handle Entity POST request.

        Returns:
            response (web.Response): response

        Raises:
            AttributeError: if `body` was not provided

        """
        body = await self.prepare_body()
        if not body:
            raise AttributeError
        try:
            response = await self.controller.process_post(
                user_id=await self.current_user,
                request_body=body,
                command=self.request.match_info.get('command'),
            )
        except Exception as exception:
            logger.exception(exception)
            return web.HTTPBadRequest()
        return web.json_response(
            response,
        )
