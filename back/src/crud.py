from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from src.utils.timezone import now_sp

from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# —— User (RH) —— #
def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    if get_user(db, user.email):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        nome=user.nome,  # <-- NOVO
        hashed_password=hashed_password
    )
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

def delete_colaborador(db: Session, colaborador_id: str) -> bool:
    colaborador = db.query(models.Colaborador).filter(models.Colaborador.code == colaborador_id).first()
    if colaborador:
        db.delete(colaborador)
        db.commit()
        return True
    return False

# —— Registro de Ponto —— #
def registrar_ponto(db: Session, colaborador_id: str):
    # Verifica se o colaborador existe
    colaborador = db.query(models.Colaborador).filter_by(code=colaborador_id).first()
    if not colaborador:
        raise HTTPException(
            status_code=404,
            detail="Colaborador não encontrado"
        )

    agora = now_sp()
    hoje = agora.date()

    reg = db.query(models.RegistroPonto).filter(
        models.RegistroPonto.colaborador_id == colaborador_id,
        models.RegistroPonto.data == hoje
    ).first()

    if not reg:
        reg = models.RegistroPonto(
            colaborador_id=colaborador_id,
            data=hoje,
            entrada=agora
        )
        db.add(reg)
    else:
        if not reg.saida_almoco:
            reg.saida_almoco = agora
        elif not reg.volta_almoco:
            reg.volta_almoco = agora
        elif not reg.saida:
            reg.saida = agora

    db.commit()
    db.refresh(reg)
    return reg


def list_pontos(db: Session):
    return db.query(models.RegistroPonto).options(joinedload(models.RegistroPonto.colaborador)).all()

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
