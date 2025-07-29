from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from src.utils.timezone import now_sp

from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# —— Auditoria (RH) —— 
def registrar_auditoria(db: Session, user_id: int, action: str, endpoint: str, detail: str = ""):
    from .models import AuditLog
    audit = AuditLog(
        user_id=user_id,
        action=action,
        endpoint=endpoint,
        detail=detail
    )
    db.add(audit)
    db.commit()




# —— User (RH) —— #
def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    if get_user(db, user.email):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        nome=user.nome,
        hashed_password=hashed_password,
        role = user.role
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
    user_id = None
    if colab.email_usuario:
        usuario = db.query(models.User).filter_by(email=colab.email_usuario).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado com esse email")
        user_id = usuario.id

    db_colab = models.Colaborador(
        code=colab.code,
        nome=colab.nome,
        user_id=user_id
    )
    db.add(db_colab)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Código já existe")
    db.refresh(db_colab)
    return db_colab


def get_colaborador_by_user_id(db: Session, user_id: int):
    return db.query(models.Colaborador).filter(models.Colaborador.user_id == user_id).first()


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
def registrar_ponto(db: Session, colaborador_code: str):
    colaborador = db.query(models.Colaborador).filter_by(code=colaborador_code).first()
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    agora = now_sp()
    hoje = agora.date()

    reg = db.query(models.RegistroPonto).filter(
        models.RegistroPonto.colaborador_id == colaborador.id,
        models.RegistroPonto.data == hoje
    ).first()

    if not reg:
        reg = models.RegistroPonto(
            colaborador_id=colaborador.id,
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

def update_ponto(db: Session, id: int, dados: schemas.RegistroPontoUpdate, user_id: int):
    ponto = db.query(models.RegistroPonto).filter(models.RegistroPonto.id == id).first()

    if not ponto:
        raise HTTPException(status_code=404, detail="Registro de ponto não encontrado.")


    if ponto.justificativa:
        raise HTTPException(status_code=400, detail="Registros de justificativa não podem ser alterados.")

    for campo, valor in dados.dict(exclude_unset=True).items():
        setattr(ponto, campo, valor)

    ponto.alterado_por_id = user_id  # ✅ seta quem alterou
    db.commit()
    db.refresh(ponto)
    return ponto



def delete_ponto(db: Session, id: int):
    reg = db.query(models.RegistroPonto).filter_by(id=id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    db.delete(reg)
    db.commit()
    return reg



def salvar_justificativa(db: Session, justificativa: schemas.JustificativaCreate) -> models.Justificativa:
    colaborador = db.query(models.Colaborador).filter_by(code=str(justificativa.colaborador_id)).first()
    if not colaborador:
        raise ValueError("Colaborador não encontrado.")

    nova_justificativa = models.Justificativa(
        colaborador_id=colaborador.id,
        justificativa=justificativa.justificativa,
        data_referente=justificativa.data_referente,
        arquivo=justificativa.arquivo
    )

    db.add(nova_justificativa)
    db.commit()
    db.refresh(nova_justificativa)
    return nova_justificativa



def avaliar_justificativa(
    db: Session,
    just_id: int,
    avaliador: models.User,
    nova_avaliacao: schemas.AvaliacaoJustificativa
):
    just = db.query(models.Justificativa).filter_by(id=just_id).first()
    if not just:
        raise HTTPException(status_code=404, detail="Justificativa não encontrada")
    if just.status != "pendente":
        raise HTTPException(status_code=409, detail="Já avaliada")

    just.status = nova_avaliacao.status.value
    just.avaliador_id = avaliador.id
    just.avaliado_em = datetime.utcnow()
    db.commit()
    db.refresh(just)

    registrar_auditoria(
        db,
        avaliador.id,
        action=f"{nova_avaliacao.status}",
        endpoint=f"/justificativas/{just_id}/avaliar",
        detail=f"Comentário: {nova_avaliacao.comentario or '-'}"
    )
    return just