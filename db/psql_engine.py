"""PostgreSQL async client module."""
import logging

import sqlalchemy as sa
from config_model import PostgresConfig
from sqlalchemy.ext import asyncio as sa_asyncio
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class PostgresEngine(object):   # noqa:WPS214
    """Class implements Postgresql async client."""

    cache_size = 2000

    def __init__(self, config: PostgresConfig):
        """
        Init class instance.

        Args:
            config (PostgresConfig): db config data

        """
        self.config = config
        self.engine = None
        self.connection = None
        self.session_maker = None
        self.meta = None

    async def create_engine(self):
        """Create db engine: postgresql+asyncpg."""
        self.engine: sa_asyncio.AsyncEngine = sa_asyncio.create_async_engine(
            'postgresql+asyncpg://{0}:{1}@{2}:{3}/{4}'.format(
                self.config.user,
                self.config.password,
                self.config.hostname,
                self.config.port,
                self.config.database,
            ),
            query_cache_size=self.cache_size,
            pool_pre_ping=True,  # check conn every request
            future=True,  # auto begin
        )
        logger.info('Postgresql <engine> was created successfully.')
        self.meta = sa.MetaData(bind=self.engine)

    async def run_session_maker(self):
        """Run session maker factory to create db session."""
        await self.create_engine()
        try:
            self.session_maker = sessionmaker(
                self.engine,
                expire_on_commit=False,
                class_=sa_asyncio.AsyncSession,
            )
        except Exception as exception:
            logger.exception(
                'Session maker factory error: {0}'.format(
                    exception,
                ),
            )
        logger.info('Postgresql <session> was created successfully.')

    async def stop(self):
        """Dispose db engine."""
        await self.engine.dispose()
        logger.info('Postgresql has been stopped successfully.')
