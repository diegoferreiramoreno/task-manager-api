import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool, engine_from_config
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from dotenv import load_dotenv

from alembic import context

# 1. Configurações de Path e Ambiente
sys.path.append(os.getcwd())
load_dotenv()

# 2. Importação dos Models
# Certifique-se de que o import está correto para o seu arquivo database.py e models.py
from database import Base, DATABASE_URL
from models import Task, Holiday  # Importante importar os modelos para serem detectados

# Configuração do Alembic
config = context.config

# Configuração de Log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadados do alvo (Seus modelos)
target_metadata = Base.metadata

# --- FUNÇÃO 1: Executa a migração (Síncrono) ---
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

# --- FUNÇÃO 2: Ponto de Entrada Online ---
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = os.getenv("DATABASE_URL", str(DATABASE_URL))
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = url

    if "+asyncpg" in url or "+aiopg" in url:
        async def run_async_migrations() -> None:
            connectable = async_engine_from_config(
                configuration,
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )
            async with connectable.connect() as connection:
                await connection.run_sync(do_run_migrations)
            await connectable.dispose()

        asyncio.run(run_async_migrations())
    else:
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        with connectable.connect() as connection:
            do_run_migrations(connection)
        connectable.dispose()

if context.is_offline_mode():
    # Se fosse offline, rodaria aqui (geralmente não precisa mexer para esse caso)
    context.configure(url=os.getenv("DATABASE_URL"))
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()