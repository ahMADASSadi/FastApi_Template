import asyncio
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
import alembic_postgresql_enum

from config.settings import get_setting
from database.base import BaseModelWithDeleted  # type:ignore
from models import *  # noqa: F401
    

# from models.users import User, UserRole  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

config.set_main_option(
    "sqlalchemy.url",
    str(get_setting("db").DATABASE_ASYNC_URL),  # type:ignore
)
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None and Path(config.config_file_name).is_file():
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BaseModelWithDeleted.metadata


# def include_object(object, name, type_, reflected, compare_to):
#     if type_ == "table" and reflected:
#         return name in target_metadata.tables
#     return True
def include_object(object, name, type_, reflected, compare_to):
    # For tables: include only those that exist in the target_metadata
    # compare_to is the reflected target (from metadata) when autogenerating.
    # If a reflected table has no matching table in metadata (compare_to is None)
    # it should be skipped.
    if type_ == "table":
        # skip DB-only tables (no matching model)
        if reflected and compare_to is None:
            return False
        # skip specific tables by name even if they appear in metadata/DB
        if name in ["accounts_user", "accounts_userrole", "acccounts_user", "accounts_profile", "activities_relation"]:
            return False
        return True

    # For columns: allow only those not marked to skip
    if type_ == "column":
        if getattr(object, "info", {}).get("skip_autogenerate", False):
            return False
        return True

    # for all other object types (indexes, FKs, etc.) use default include
    return True


# def include_object(object, name, type_, reflected, compare_to):
#     # Skip specific tables by name
#     if type_ == "table" and name in ["acccounts_user", "accounts_userrole"]:
#         return False

#     # Skip columns with a specific flag in their info dict
#     if type_ == "column" and object.info.get("skip_autogenerate", False):
#         return False

#     return True


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    def do_run_migrations(connection) -> None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()

    async def run_async_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
