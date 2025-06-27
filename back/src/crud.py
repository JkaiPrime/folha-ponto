from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# —— User (RH) —— #
def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    if get_user(db, user.email):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    hashed = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_failed_attempts(db: Session, user: models.User, reset: bool = False):
    if reset:
        user.failed_attempts = 0
        user.locked = False
        user.locked_until = None
    else:
        user.failed_attempts += 1
        if user.failed_attempts >= 3:
            user.locked = True
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    db.refresh(user)
    return user

# —— Colaborador —— #
def create_colaborador(db: Session, colab: schemas.ColaboradorCreate):
    db_colab = models.Colaborador(code=colab.code, nome=colab.nome)
    db.add(db_colab)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Código já existe")
    db.refresh(db_colab)
    return db_colab

def list_colaboradores(db: Session):
    return db.query(models.Colaborador).all()

# —— Registro de Ponto —— #
def registrar_ponto(db: Session, colaborador_id: str):
    hoje = datetime.utcnow().date()
    reg = db.query(models.RegistroPonto).filter(
        models.RegistroPonto.colaborador_id == colaborador_id,
        models.RegistroPonto.data == hoje
    ).first()
    if not reg:
        reg = models.RegistroPonto(
            colaborador_id=colaborador_id,
            data=hoje,
            entrada=datetime.utcnow()
        )
        db.add(reg)
    else:
        if not reg.saida_almoco:
            reg.saida_almoco = datetime.utcnow()
        elif not reg.volta_almoco:
            reg.volta_almoco = datetime.utcnow()
        elif not reg.saida:
            reg.saida = datetime.utcnow()
    db.commit()
    db.refresh(reg)
    return reg

def list_pontos(db: Session):
    return db.query(models.RegistroPonto).all()

def update_ponto(db: Session, id: int, dados: schemas.RegistroPontoUpdate):
    reg = db.query(models.RegistroPonto).filter_by(id=id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    for field, val in dados.dict(exclude_unset=True).items():
        setattr(reg, field, val)
    db.commit()
    db.refresh(reg)
    return reg

def delete_ponto(db: Session, id: int):
    reg = db.query(models.RegistroPonto).filter_by(id=id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    db.delete(reg)
    db.commit()
    return reg
