import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# Load .env so `alembic` CLI picks up DATABASE_URL without a manual export.
load_dotenv()

# ---------------------------------------------------------------------------
# Import ORM Base so Alembic can detect all mapped tables automatically.
# All ORM classes must be imported (directly or transitively) before
# target_metadata is read; importing models.py covers all of them.
# ---------------------------------------------------------------------------
from medistock.infrastructure.orm.models import Base  # noqa: F401

# this is the Alembic Config object, which provides access to values within
# the .ini file in use.
config = context.config

# Allow the DATABASE_URL environment variable to override alembic.ini
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData object for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, so
    no actual DB connection is required at migration-script generation time.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    An Engine is created and a connection is associated with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
