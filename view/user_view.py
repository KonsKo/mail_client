"""User views."""
import logging

from aiohttp import web
from auth.policy import create_credentials
from aiohttp_security import forget, remember
from middleware import require_login
from service.user_service import UserService
from service.base_service import BaseService
from repository.base_repository import BaseRepository
from socket_io.namespace import close_sio_session
from db.schema import User

logger = logging.getLogger(__name__)


@require_login
class LogoutView(web.View):
    """Logout view."""

    async def delete(self) -> web.Response:
        """
        Logout.

        Returns:
            response (web.Response): response

        """
        response = web.HTTPNoContent()  # 204

        try:
            await close_sio_session(self.request)
        except Exception as exception:
            logger.exception(exception)

        await forget(self.request, response)

        return response


class CreateUserView(web.View):
    """Create user view."""

    async def post(self) -> web.Response:
        """
        Create user.

        Returns:
            response (web.Response): response

        """
        repo = BaseRepository(
            app=self.request.app,
            table=User,
        )
        service = BaseService(
            repository=repo,
            app=self.request.app,
        )
        try:
            body = await self.request.json()
        except Exception as exception1:
            logger.exception(exception1)
            return web.HTTPBadRequest()
        try:
            await create_credentials(
                service=service,
                password=body['password'],
                username=body['username'],
            )
        except Exception as exception:
            logger.exception(exception)
            return web.HTTPBadRequest()
        return web.HTTPCreated()  # 201
