from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Carregar variáveis do .env
load_dotenv(dotenv_path=".env")

# Ler a URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não foi encontrada no .env")

# Criar engine de conexão com PostgreSQL
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c timezone=America/Sao_Paulo"}
)

# Sessão padrão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
