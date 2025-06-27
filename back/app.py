from fastapi import FastAPI
from src.database import engine, Base
from src.routers.auth import router as auth_router
from src.routers.colaboradores import router as colaboradores_router
from src.routers.ponto import router as ponto_router

# Cria todas as tabelas definidas em src/models.py
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Ponto 🕒 com Auth e Gestão")

# Registra os routers
app.include_router(auth_router)
app.include_router(colaboradores_router)
app.include_router(ponto_router)

@app.get("/")
async def root():
    return {"message": "API de Ponto 🕒 com Auth funcionando."}
