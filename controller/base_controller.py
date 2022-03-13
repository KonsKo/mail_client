"""Base Controller module."""
from typing import Optional

from aiohttp import web
from service.iservice import IService

from controller.icontroller import IController


class BaseController(IController):
    """Base Controller class."""

    def __init__(self, service: IService):
        """
        Init class instance.

        Args:
            service (IService): service

        """
        self.service = service

    async def process_entity_get(
        self,
        entity_id: int,
        user_id: int,
        url_query: Optional[dict] = None,
    ) -> dict:
        """
        Process Entity GET.

        Args:
            entity_id (int): letter id
            url_query (Optional[dict]): url query
            user_id (int): current user id

        Returns:
            result (dict): result of command

        """
        return await self.service.retrieve(
            entity_id=entity_id,
            url_query=url_query,
            user_id=user_id,
        )

    async def process_entity_post(
        self,
        command: str,
        entity_id: int,
        user_id: int,
        request_body: Optional[dict] = None,
    ):
        """
        Work with POST request and process it.

        Args:
            entity_id (int): letter id
            command (str): command name to invoke
            request_body (Optional[dict]): request body
            user_id (int): current user id,

        Returns:
            result (dict): result of command

        Raises:
            HTTPBadRequest: if exception

        """
        if command == 'update':
            return await self.service.update(
                request_body=request_body,
                entity_id=entity_id,
                user_id=user_id,
            )
        elif command == 'delete':
            return await self.service.delete(
                entity_id=entity_id,
            )
        elif command == 'send':  # TODO
            return await self.service.send_email()
        raise web.HTTPBadRequest()

    async def process_get(
        self,
        user_id: int,
        url_query: Optional[dict] = None,
    ) -> dict:
        """
        Work with GET request and process it.

        Args:
            url_query(Optional[dict]): url query
            user_id (int): current user id

        Returns:
            result (dict): result of command

        """
        return await self.service.retrieve(
            url_query=url_query,
            user_id=user_id,
        )

    async def process_post(
        self,
        command: str,
        request_body: dict,
        user_id: int,
    ):
        """
        Work with POST request and process it.

        Args:
            user_id (int): current user id
            command (str): command name to invoke
            request_body(dict): request body

        Returns:
            result (dict): result of command

        Raises:
            HTTPBadRequest: if exception

        """
        if command == 'create':
            return await self.service.create(
                request_body=request_body,
                user_id=user_id,
            )
        elif command == 'update':
            return await self.service.update(
                request_body=request_body,
                user_id=user_id,
            )
        elif command == 'delete':
            return await self.service.delete(
                request_body=request_body,
                user_id=user_id,
            )
        elif command == 'send':  # TODO
            return await self.service.send_email()
        raise web.HTTPBadRequest()
