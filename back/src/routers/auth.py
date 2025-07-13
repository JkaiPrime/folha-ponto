import os
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from dotenv import load_dotenv

from src import models, crud, schemas
from src.database import SessionLocal

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "Minha KeySuperS@cret!!@31231")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 25))

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
        raise HTTPException(status_code=423, detail="Usuário bloqueado. Tente novamente mais tarde.")
    
    if not pwd_context.verify(password, user.hashed_password):
        crud.update_failed_attempts(db, user)
        raise HTTPException(status_code=402, detail="Credenciais inválidas")
    
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

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    email = verifica_token_acesso(token)
    user = crud.get_user(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

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
    if user.role not in ["admin", "rh"]:
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para administradores ou RH")
    return user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    crud.update_failed_attempts(db, user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup", response_model=schemas.UserResponse, status_code=201)
def signup(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    token: dict = Depends(verifica_token_condicional)
):
    return crud.create_user(db, user)

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
    _: models.User = Depends(verifica_token_acesso)
):
    usuario = db.query(models.User).filter(models.User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.locked = False
    usuario.locked_until = None
    usuario.failed_attempts = 0
    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/usuarios/{id}", status_code=204)
def deletar_usuario(
    id: int,
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    usuario = db.query(models.User).filter(models.User.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
