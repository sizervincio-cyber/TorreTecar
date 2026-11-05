"""Migrações do banco da Torre. A URL vem de DATABASE_URL, como na API."""
from alembic import context

from server.app.config import load_settings
from server.app.db import Base, make_engine
from server.app import models  # noqa: F401  (registra as tabelas)

engine = make_engine(load_settings().database_url)
with engine.connect() as conn:
    context.configure(connection=conn, target_metadata=Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()
