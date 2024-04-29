from abc import ABC, abstractmethod

from sqlalchemy import Column, BigInteger, Integer
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from dns_system.apps.db.base_model import Model


class IDBase(Model):
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)


class TimestampBase(Model):
    __abstract__ = True

    created_at = Column(
        Integer, index=True, nullable=False
    )

    updated_at = Column(
        Integer, index=True
    )


class Database(ABC):
    def __init__(self) -> None:
        self.engine: AsyncEngine = self._create_engine()
        self.session_factory: AsyncSession = self._init_session_factory()

    @abstractmethod
    def _get_db_url(self):
        ...

    @abstractmethod
    def _create_engine(self):
        ...

    @abstractmethod
    def _init_session_factory(self):
        ...
