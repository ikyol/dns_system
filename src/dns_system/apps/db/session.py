from asyncio import current_task
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_scoped_session, AsyncEngine, async_sessionmaker
)

from dns_system.config.settings import settings
from dns_system.apps.db.abstract import Database


class AsyncPostgresDriver(Database):
    def _get_db_url(self):
        return settings.SQLALCHEMY_DATABASE_URI.unicode_string()

    def _create_engine(self) -> AsyncEngine:
        engine = create_async_engine(
            self._get_db_url(),
            pool_pre_ping=True,
            echo_pool=True,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_size=settings.DB_POOL_SIZE,
            pool_use_lifo=True,
            max_overflow=settings.DB_MAX_OVERFLOW,
        )
        return engine

    def _init_session_factory(self):
        return async_scoped_session(async_sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
                class_=AsyncSession
            ), scopefunc=current_task,
        )

    @asynccontextmanager
    async def session(self):
        session: AsyncSession = self.session_factory
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


driver = AsyncPostgresDriver()
