import os
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src import models
from src import crud, schemas
from src.database import SessionLocal


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "uma_chave_muito_secreta")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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
        return False
    if user.locked and user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=423,
            detail="Conta bloqueada. Tente novamente mais tarde."
        )
    if not pwd_context.verify(password, user.hashed_password):
        crud.update_failed_attempts(db, user)
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    crud.update_failed_attempts(db, user, reset=True)
    return user

def create_access_token(data: dict, expires: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def verifica_token_acesso(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token inválido ou ausente",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user(db, email)
    if not user:
        raise credentials_exception

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



@router.post("/signup", response_model=schemas.UserResponse, status_code=201)
def signup(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    token: dict = Depends(verifica_token_condicional)
):
    return crud.create_user(db, user)

@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, email)
    if not user:
        raise credentials_exception
    return user

@router.get("/usuarios", response_model=List[schemas.UserResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    return db.query(models.User).all()


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
