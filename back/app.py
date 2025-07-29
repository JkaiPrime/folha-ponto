from fastapi import FastAPI
from src.database import engine, Base
from src.routers.auth import router as auth_router
from src.routers.colaboradores import router as colaboradores_router
from src.routers.ponto import router as ponto_router
from src.routers import justificativas, me
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from src.database import SessionLocal
from src.models import User, Colaborador
from src.routers import auth, colaboradores, justificativas, ponto, me
from src.utils.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from src.routers import auditoria


# Cria todas as tabelas definidas em src/models.py
Base.metadata.create_all(bind=engine)
'''
    allow_origins=[
        "https://folha-ponto-six.vercel.app",
        "http://localhost:9000",          
        "http://127.0.0.1:9000"
    ],
'''
app = FastAPI(title="API de Ponto 🕒 com Auth e Gestão")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://folha-ponto-six.vercel.app",
        "http://localhost:9000",          
        "http://127.0.0.1:9000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Você excedeu o limite de requisições. Tente novamente em breve."}
    )



# Rotas
app.include_router(auth.router)
app.include_router(colaboradores.router)
app.include_router(justificativas.router)
app.include_router(ponto.router)
app.include_router(me.router)
app.include_router(auditoria.router)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def startup_configuracoes():
    # Criar tabelas
    print("🛠️ Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)

    # Criar usuários padrão
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            print("[⚙️] Nenhum usuário encontrado. Criando admin e RH padrão...")

            users_data = [
                {
                    "email": os.getenv("DEFAULT_ADMIN_EMAIL"),
                    "password": os.getenv("DEFAULT_ADMIN_PASSWORD"),
                    "role": os.getenv("DEFAULT_ADMIN_ROLE", "gestao"),
                    "codigo": os.getenv("DEFAULT_ADMIN_CODIGO", "000000"),
                    "nome": os.getenv("DEFAULT_ADMIN_NOME", "Administrador")
                },
                {
                    "email": os.getenv("DEFAULT_RH_EMAIL"),
                    "password": os.getenv("DEFAULT_RH_PASSWORD"),
                    "role": os.getenv("DEFAULT_RH_ROLE", "gestao"),
                    "codigo": os.getenv("DEFAULT_RH_CODIGO", "000001"),
                    "nome": os.getenv("DEFAULT_RH_NOME", "RH Padrão")
                }
            ]

            for u in users_data:
                hashed = pwd_context.hash(u["password"])
                user = User(email=u["email"], nome=u["nome"], hashed_password=hashed, role=u["role"], is_active=True)
                db.add(user)
                db.commit()
                db.refresh(user)

                colaborador = Colaborador(code=u["codigo"], nome=u["nome"], user_id=user.id)
                db.add(colaborador)
                db.commit()

                print(f"[✅] Usuário criado: {user.email} | Código: {colaborador.code} | Papel: {user.role}")
        else:
            print("[ℹ️] Usuários já existem. Nenhum admin ou RH criado.")
    except IntegrityError:
        db.rollback()
        print("[⚠️] Erro ao criar usuários padrão. Verifique se os códigos já existem.")
    finally:
        db.close()





@app.get("/")
async def root():
    return {"message": "API de Ponto 🕒 com Auth funcionando."}
