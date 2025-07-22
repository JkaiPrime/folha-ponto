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

# Cria todas as tabelas definidas em src/models.py
Base.metadata.create_all(bind=engine)

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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def criar_admin_e_colaborador_se_nao_existir():
    db = SessionLocal()
    try:
        if db.query(User).first() is None:
            print("[⚙️] Nenhum usuário encontrado. Criando admin padrão...")

            hashed_password = pwd_context.hash(os.getenv("DEFAULT_ADMIN_PASSWORD"))
            admin_user = User(
                email=os.getenv("DEFAULT_ADMIN_EMAIL"),
                nome=os.getenv("DEFAULT_ADMIN_NOME"),
                hashed_password=hashed_password,
                role=os.getenv("DEFAULT_ADMIN_ROLE", "gestao"),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            colaborador = Colaborador(
                code=os.getenv("DEFAULT_ADMIN_CODIGO", "000001"),
                nome=os.getenv("DEFAULT_ADMIN_NOME"),
                user_id=admin_user.id
            )
            db.add(colaborador)
            db.commit()

            print(f"[✅] Admin criado: {admin_user.email} | Código do colaborador: {colaborador.code}")
        else:
            print("[ℹ️] Usuários já existem. Nenhum admin criado.")
    except IntegrityError:
        db.rollback()
        print("[⚠️] Código de colaborador já existe. Verifique o DEFAULT_ADMIN_CODIGO.")
    finally:
        db.close()



@app.get("/")
async def root():
    return {"message": "API de Ponto 🕒 com Auth funcionando."}
