"""Web application module."""
import logging

from aiohttp import web

from config_model import MainConfig
from db.psql_engine import PostgresEngine
from emailing.smtp_client import SMTPClient
from middleware import check_login
from socket_io.namespace import sio, socket_test
from view.letter_view import LetterEntityView, LetterManyView
from view.user_view import CreateUserView

logger = logging.getLogger(__name__)


# noinspection PyTypeChecker
class Application(web.Application):
    """Web application."""

    def __init__(self, config: MainConfig, **kwargs):
        """
        Init class instance.

        Args:
            config (MainConfig): app config
            kwargs: extra key parameters

        """
        super().__init__(**kwargs)
        self.config = config
        self._prepare_app()

    def _prepare_app(self):
        self.on_startup.append(self._setup_db)
        self.on_startup.append(self._setup_smtp)
        self['socketio_session'] = {}
        self._setup_routes()
        self._setup_socketio()
        self._setup_middleware()

    def _setup_routes(self):
        """
        Set up routes for app.

        Raises:
            NotImplementedError: if route set up error

        """
        try:
            self.add_routes(
                [
                    web.get(
                        '/socket.io/',
                        socket_test,
                    ),

                    web.view(
                        '/create_user',
                        CreateUserView,
                    ),

                    web.view(
                        '/api/crud/letter',
                        LetterManyView,
                    ),
                    web.view(
                        r'/api/crud/letter/{id:\d+}',
                        LetterEntityView,
                    ),

                    web.view(
                        '/api/crud/letter/{command}',
                        LetterManyView,
                    ),
                    web.view(
                        r'/api/crud/letter/{id:\d+}/{command}',
                        LetterEntityView,
                    ),
                ],
            )
        except Exception as exception:
            logger.exception(
                'Routes setting up was failed. {0}'.format(
                    exception,
                ),
            )
            raise NotImplementedError
        logger.info('Routes has been set up.')

    async def _setup_db(self, *args):
        """
        Run db engine.

        Args:
            args: extra parameter, required

        """
        db_engine = PostgresEngine(
            config=self.config.db,
        )
        await db_engine.run_session_maker()
        self['db'] = db_engine

    def _setup_middleware(self):
        self.middlewares.append(check_login)

    def _setup_socketio(self):
        sio.attach(self)

    async def _setup_smtp(self, *args):
        smtp = SMTPClient(config=self.config.smtp)
        await smtp.connect()
        self['smtp'] = smtp
