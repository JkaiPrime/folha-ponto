import os
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from dotenv import load_dotenv
from src import models, crud, schemas
from src.database import SessionLocal
from src.utils.rate_limiter import limiter
from fastapi import Request

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "Minha KeySuperS@cret!!@31231")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 25))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 1))

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user(db, email)
    if not user:
        raise HTTPException(status_code=402, detail="Credenciais inválidas")
    
    if user.locked:
        raise HTTPException(
            status_code=423,
            detail="Usuário bloqueado devido a múltiplas tentativas incorretas. Tente novamente mais tarde."
        )
    
    if not pwd_context.verify(password, user.hashed_password):
        tentativas_restantes = crud.update_failed_attempts(db, user)
        raise HTTPException(
            status_code=402,
            detail=f"Credenciais inválidas. Tentativas restantes: {tentativas_restantes}"
        )
    crud.update_failed_attempts(db, user, reset=True)
    return user




def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verifica_token_acesso(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido ou ausente")
        return email
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou ausente")

#def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
#    email = verifica_token_acesso(token)
#    user = crud.get_user(db, email)
#    if not user:
#        raise HTTPException(status_code=401, detail="Usuário não encontrado")
#    return user


def get_current_user(
    db: Session = Depends(get_db),
    access_token: str = Cookie(None)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token ausente")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = crud.get_user(db, email)
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

def verifica_token_condicional(
    db: Session = Depends(get_db),
    usuario: dict = Depends(verifica_token_acesso)
):
    # Se já existe algum usuário no banco, exigir token
    if db.query(models.User).first():
        return usuario
    # Caso contrário, permitir seguir sem token
    return None

def apenas_funcionario(user: models.User = Depends(get_current_user)):
    if user.role != "funcionario":
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para funcionários")
    return user

def apenas_gestao(user: models.User = Depends(get_current_user)):
    if user.role not in ["gestao", "admin", "rh"]:
        raise HTTPException(
            status_code=403,
            detail="Acesso permitido apenas para usuários de gestão / RH / admin"
        )
    return user

def apenas_rh(user: models.User = Depends(get_current_user)):
    if user.role != "rh":
        raise HTTPException(status_code=403, detail="Acesso restrito ao RH")
    return user
'''
@limiter.limit("14/minute")
@router.post("/login", response_model=schemas.TokenRefresh)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )



    crud.update_failed_attempts(db, user)
    crud.registrar_auditoria(
        db,
        user.id,
        action="login",
        endpoint="/auth/login",
        detail="Login realizado com sucesso"
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
'''
@limiter.limit("14/minute")
@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        data={"sub": user.email},
        expires_delta=refresh_token_expires
    )

    crud.update_failed_attempts(db, user, reset=True)
    crud.registrar_auditoria(
        db,
        user.id,
        action="login",
        endpoint="/auth/login",
        detail="Login realizado com sucesso"
    )

    response = JSONResponse(content={
        "message": "Login realizado com sucesso",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite=None,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite=None,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )
    return response


@limiter.limit("1/minute")
@router.post("/refresh", response_model=schemas.Token)
def refresh_token(request: Request, req: schemas.RefreshTokenRequest):
    try:
        payload = jwt.decode(req.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")

        new_token = create_access_token(data={"sub": email})
        return {"access_token": new_token, "token_type": "bearer"}

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@limiter.limit("10/minute")
@router.post("/signup", response_model=schemas.UserResponse, status_code=201)
def signup(
    user: schemas.UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    # Permitir cadastro do primeiro usuário sem autenticação
    if db.query(models.User).count() == 0:
        db_user = crud.create_user(db, user)
        crud.registrar_auditoria(
            db,
            db_user.id,
            action="criar_usuario",
            endpoint="/auth/signup",
            detail=f"Primeiro usuário criado: {db_user.email}"
        )
        return db_user

    # Bloquear caso usuário logado não seja gestão
    if not current_user or current_user.role != "gestao":
        raise HTTPException(status_code=403, detail="Permissão negada para criar usuários.")

    db_user = crud.create_user(db, user)
    crud.registrar_auditoria(
        db,
        db_user.id,
        action="criar_usuario",
        endpoint="/auth/signup",
        detail=f"Usuário criado: {db_user.email}"
    )
    return db_user


@router.get("/usuarios", response_model=List[schemas.UserResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    return db.query(models.User).all()

@router.patch("/usuarios/{id}/papel", response_model=schemas.UserResponse)
def atualizar_papel_usuario(
    id: int,
    role: str = Form(...),
    db: Session = Depends(get_db),
    _: models.User = Depends(apenas_gestao)
):
    user = db.query(models.User).filter_by(id=id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if role not in ["funcionario", "gestao"]:
        raise HTTPException(status_code=400, detail="Papel inválido")

    user.role = role
    db.commit()
    db.refresh(user)
    return user

@router.post("/usuarios/{user_id}/desbloquear", response_model=schemas.UserResponse)
def desbloquear_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Apenas gestão pode desbloquear
    if current_user.role != "gestao":
        raise HTTPException(status_code=403, detail="Permissão negada.")

    usuario = db.query(models.User).filter(models.User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.locked = False
    usuario.locked_until = None
    usuario.failed_attempts = 0
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/usuarios/{id}")
def deletar_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.User).filter(models.User.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(usuario)
    db.commit()
    return {"message": "Usuário excluído com sucesso"}

@router.put("/alterar-senha")
def alterar_senha(
    new_password: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    hashed_password = pwd_context.hash(new_password)
    user.hashed_password = hashed_password
    db.commit()
    return {"message": "Senha alterada com sucesso"}



@router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logout realizado com sucesso"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response