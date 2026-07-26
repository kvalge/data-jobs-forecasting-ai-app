"""Alembic environment: uses project DATABASE_URL and SQLAlchemy metadata."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.config import validate_config
import src.config as app_config
from src.dal.models import Base

# Alembic Config object (alembic.ini values)
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _configure_database_url() -> None:
    """Load .env, validate, and inject DATABASE_URL into Alembic config."""
    validate_config()
    assert app_config.DATABASE_URL is not None
    config.set_main_option("sqlalchemy.url", app_config.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL without a live DB)."""
    _configure_database_url()
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database."""
    _configure_database_url()
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
