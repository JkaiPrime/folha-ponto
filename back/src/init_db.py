# init_db.py
from src.database import Base, engine
from src import models



if __name__ == "__main__":

    print("Criando tabelas no PostgreSQL…")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")
