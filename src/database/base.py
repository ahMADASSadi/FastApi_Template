import re
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, MetaData, event, func
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm.decl_api import DeclarativeBase


class Base(DeclarativeBase):
    __abstract__ = True

    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type:ignore
        """Automatically derived table name from the model's class name in snake_case."""
        return (
            cls._to_snake(cls.__name__) + "s"
            if not cls.module_name  # type:ignore
            else cls.module_name + "s_" + cls._to_snake(cls.__name__)  # type:ignore
        )

    @staticmethod
    def _to_snake(camel: str) -> str:
        """Convert CamelCase to snake_case."""
        [
            camel := p.sub(r, camel)  # type:ignore
            for p, r in [
                (re.compile(r"[^0-9A-Za-z_]"), ""),
                (re.compile(r"([A-Z]+)([A-Z][a-z])"), r"\1_\2"),
                (re.compile(r"([a-z0-9])([A-Z])"), r"\1_\2"),
                (re.compile(r"([a-z])([0-9])"), r"\1_\2"),
            ]
        ]
        return camel.lower()

    config = {"orm_mode": True}


class BaseModel(Base):
    __abstract__ = True

    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def _set_updated_at(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


event.listens_for(BaseModel, "before_update", propagate=True)(_set_updated_at)


class BaseModelWithDeleted(Base):
    __abstract__ = True

    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )


def _set_deleted_at(mapper, connection, target) -> None:
    target.deleted_at = datetime.now(timezone.utc)


event.listens_for(BaseModelWithDeleted, "before_update", propagate=True)(_set_updated_at)
event.listens_for(BaseModelWithDeleted, "before_delete", propagate=True)(_set_deleted_at)
