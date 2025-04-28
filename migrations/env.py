import os
import logging

from logging.config import fileConfig
from alembic import context

from application.db.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    if "DATABASE_URL" in os.environ:
        url = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)
    else:
        url = os.getenv("WRITE_DATABASE_URL")
    logging.info(f"Running offline migration against {url}")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    from application.settings import get_settings
    from sqlalchemy import create_engine

    if config.get_main_option("sqlalchemy.url"):
        url = config.get_main_option("sqlalchemy.url")
    else:
        url = get_settings().WRITE_DATABASE_URL

    engine = create_engine(url)
    connectable = engine

    with connectable.connect() as connection:
        logging.info(f"Running online migration against {url}")
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
