"""Alembic environment: use app's Base and DATABASE_URL."""
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool
# Add project root (src/) to path so "app" is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base
from app.config import DATABASE_URL
from app.models import Article, Source  # noqa: F401 - so models are registered

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
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
