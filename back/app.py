from fastapi import FastAPI, Request
from src.database import engine, Base
from src.routers import auth, colaboradores, justificativas, ponto, me, auditoria
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.utils.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from src.database import SessionLocal
from src.models import User, Colaborador

load_dotenv()

# Lista de origens autorizadas
ALLOWED_ORIGINS = [
    "https://folha-ponto-six.vercel.app",
    "http://localhost:9000",
    "http://127.0.0.1:9000"
]

# Cria todas as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Ponto 🕒 com Auth e Gestão")

# 1️⃣ Middleware CORS (atua no navegador)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2️⃣ Middleware personalizado para reforçar bloqueio de origens externas
@app.middleware("http")
async def validate_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    # Exigir sempre origem ou referer
    if not origin and not referer:
        return JSONResponse(status_code=403, content={"detail": "Origem obrigatória e não informada"})

    # Validação por Origin
    if origin and origin not in ALLOWED_ORIGINS:
        return JSONResponse(status_code=403, content={"detail": "Origem não autorizada"})

    # Validação por Referer
    if referer and not any(referer.startswith(allowed) for allowed in ALLOWED_ORIGINS):
        return JSONResponse(status_code=403, content={"detail": "Referer não autorizado"})

    return await call_next(request)

# Configuração do rate limiter
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
    print("🛠️ Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)

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
