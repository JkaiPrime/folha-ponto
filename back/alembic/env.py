from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

# ① — carregue variáveis de ambiente
import os
from dotenv import load_dotenv
load_dotenv(".env")

# ② — importe metadata
from src.database import Base          # ajuste o caminho se necessário
from src import models                 # importe TODAS as models para que o autogenerate funcione

config = context.config

# ③ — injete a URL do banco no objeto de configuração
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# ④ — Logging padrão do Alembic
if config.config_file_name:
    fileConfig(config.config_file_name)

# ⑤ — metadata apontando para o seu Base
target_metadata = Base.metadata
