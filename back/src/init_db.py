# init_db.py
import os
from src.database import Base, engine
from src import models



if __name__ == "__main__":
    print("DATABASE_URL:", os.getenv("DATABASE_URL")) 
    print("Raw URL:", repr(os.getenv("DATABASE_URL")))  # veja o que está sendo lido
    #GRANT ALL ON SCHEMA public TO folha_user;
    print("Criando tabelas no PostgreSQL…")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")
