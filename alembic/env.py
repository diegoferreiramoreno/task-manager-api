import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
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
from models import Task # Importante importar os modelos para serem detectados

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

# --- FUNÇÃO 2: Configura a Engine e Conexão (Assíncrono) ---
async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    
    # PEGAR A CONFIGURAÇÃO E INJETAR A URL DO .ENV
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv("DATABASE_URL")

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Chama a função síncrona dentro do contexto assíncrono
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

# --- FUNÇÃO 3: Ponto de Entrada (Roda o Asyncio) ---
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # Aqui usamos o asyncio.run para rodar a função async definida acima
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    # Se fosse offline, rodaria aqui (geralmente não precisa mexer para esse caso)
    context.configure(url=os.getenv("DATABASE_URL"))
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()