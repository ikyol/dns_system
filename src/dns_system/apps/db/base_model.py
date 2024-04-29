from inspect import isclass
from typing import Generator

from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta


class ModelOptions:
    def __init__(
            self,
            model_name: str,
            table_name: str,
    ):
        self.model_name = model_name
        self.table_name = table_name


class BaseModelMeta(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_, **kwargs):
        meta = getattr(cls, "Meta", None)
        options = ModelOptions(cls.__name__, cls.__tablename__)
        if meta is not None and isclass(meta):
            options.verbose_name = getattr(meta, "verbose_name", cls.__name__)
        cls.options = options
        DeclarativeMeta.__init__(cls, classname, bases, dict_, **kwargs)


class BaseModel:

    @classmethod
    def child_generator(cls) -> Generator:
        for obj in Model.registry._class_registry.values():
            if hasattr(obj, "__tablename__"):
                yield obj


Model = declarative_base(cls=BaseModel, metaclass=BaseModelMeta)
