# init_db.py
from src.database import Base, engine
from src import models



if __name__ == "__main__":
    #GRANT ALL ON SCHEMA public TO folha_user;
    print("Criando tabelas no PostgreSQL…")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")
