# src/crud.py
from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from src import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_TENTATIVAS = 3
TEMPO_BLOQUEIO_MINUTOS = 15

# ------------------ Normalização ------------------
CARGO_PLACEHOLDER = "Não Definido"

def normalize_cargo(value: Optional[str]) -> str:
    """
    Garante que NUNCA retornará None (evita NOT NULL violation).
    Normaliza vazio/indefinido para o placeholder 'Não Definido'.
    """
    if value is None:
        return CARGO_PLACEHOLDER
    v = value.strip()
    if v == "" or v.lower() in {"não definido", "nao definido", "não-definido", "nao-definido"}:
        return CARGO_PLACEHOLDER
    return v

# —— Auditoria (RH) —— 
def registrar_auditoria(db: Session, user_id: int, action: str, endpoint: str, detail: str = ""):
    from .models import AuditLog
    audit = models.AuditLog(
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
    """
    Cria usuário respeitando o 'role' enviado e, se 'code' vier no payload,
    cria o Colaborador VINCULADO com consistência transacional:
      - Pré-checa duplicidade de code
      - Se falhar ao criar o colaborador, apaga o user (evita órfão)
    """
    if get_user(db, user.email):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    # 1) Pré-checagem de code para evitar órfão depois
    if user.code:
        ja_existe = db.query(models.Colaborador).filter(models.Colaborador.code == user.code).first()
        if ja_existe:
            raise HTTPException(status_code=409, detail="Código de colaborador já existe")

    hashed_password = pwd_context.hash(user.password)

    # Nunca permitir cargo=None se a coluna for NOT NULL
    cargo_final = normalize_cargo(user.cargo)
    # Se for estagiário e não veio cargo "de verdade", define algo mais semântico
    if cargo_final == CARGO_PLACEHOLDER and user.role == "estagiario":
        cargo_final = "Estagiário"

    # 2) Criação do usuário
    db_user = models.User(
        email=user.email,
        nome=user.nome,
        hashed_password=hashed_password,
        role=user.role,                  # usa exatamente o papel recebido
        is_active=True,
        failed_attempts=0,
        locked=False,
        locked_until=None,
        cargo=cargo_final,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 3) Se veio code, criar o colaborador vinculado
    if user.code:
        db_colab = models.Colaborador(
            code=user.code,
            nome=db_user.nome,
            user_id=db_user.id
        )
        db.add(db_colab)
        try:
            db.commit()
        except IntegrityError:
            # 3.1) Algo deu errado ao criar o colaborador -> remover o user para não ficar órfão
            db.rollback()
            try:
                db.delete(db_user)
                db.commit()
            except Exception:
                db.rollback()
            raise HTTPException(status_code=409, detail="Falha ao criar colaborador (code possivelmente duplicado). Operação revertida.")

        db.refresh(db_colab)

    return db_user

def vincular_colaborador_em_user(
    db: Session,
    user_id: int,
    code: str,
    nome: Optional[str] = None,
    cargo: Optional[str] = None
) -> models.Colaborador:
    """
    Cria Colaborador e vincula a um user existente.
    Protege contra duplicidade de code e sincroniza cargo (opcional).
    """
    usuario = db.query(models.User).filter(models.User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # code precisa ser único
    existe = db.query(models.Colaborador).filter(models.Colaborador.code == code).first()
    if existe:
        raise HTTPException(status_code=409, detail="Código de colaborador já existe")

    colab = models.Colaborador(
        code=code,
        nome=nome or usuario.nome,
        user_id=user_id
    )
    db.add(colab)

    # opcional: sincroniza cargo no user
    if cargo is not None:
        usuario.cargo = normalize_cargo(cargo)
        db.add(usuario)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Falha ao vincular colaborador (code duplicado).")
    db.refresh(colab)
    return colab

def update_failed_attempts(db: Session, user: models.User, reset: bool = False) -> int:
    if reset:
        user.failed_attempts = 0
        user.locked = False
        user.locked_until = None
    else:
        user.failed_attempts += 1
        if user.failed_attempts >= MAX_TENTATIVAS:
            user.locked = True
            user.locked_until = datetime.utcnow() + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)

    db.commit()
    db.refresh(user)
    return max(0, MAX_TENTATIVAS - user.failed_attempts)

# —— Colaborador —— #
def create_colaborador(db: Session, colab: schemas.ColaboradorCreate):
    """
    Cria colaborador e sincroniza cargo em users.cargo (se informado e user existir).
    """
    user_id = None
    usuario: Optional[models.User] = None

    if colab.email_usuario:
        usuario = db.query(models.User).filter_by(email=colab.email_usuario).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado com esse email")
        user_id = usuario.id

    db_colab = models.Colaborador(
        code=colab.code,
        nome=colab.nome or (usuario.nome if usuario else ""),
        user_id=user_id
    )
    db.add(db_colab)

    # Se veio cargo -> salva em users (sempre normalizado para evitar NULL)
    if usuario is not None and colab.cargo is not None:
        usuario.cargo = normalize_cargo(colab.cargo)
        db.add(usuario)

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

def delete_colaborador(db: Session, colaborador_code: str) -> bool:
    colaborador = db.query(models.Colaborador).filter(models.Colaborador.code == colaborador_code).first()
    if colaborador:
        db.delete(colaborador)
        db.commit()
        return True
    return False

# —— Registro de Ponto —— #
def registrar_ponto(db: Session, colaborador_code: str, hora_brasilia: datetime):
    colaborador = db.query(models.Colaborador).filter_by(code=colaborador_code).first()
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    # Descobre o papel do usuário vinculado ao colaborador
    usuario = None
    if colaborador.user_id:
        usuario = db.query(models.User).filter(models.User.id == colaborador.user_id).first()
    role = (usuario.role if usuario else "funcionario") or "funcionario"

    hoje = hora_brasilia.date()

    reg = db.query(models.RegistroPonto).filter(
        models.RegistroPonto.colaborador_id == colaborador.id,
        models.RegistroPonto.data == hoje
    ).first()

    # Tratativa especial para estagiário: apenas entrada -> saída
    if role == "estagiario":
        if not reg:
            reg = models.RegistroPonto(
                colaborador_id=colaborador.id,
                data=hoje,
                entrada=hora_brasilia
            )
            db.add(reg)
        else:
            if reg.saida is None:
                reg.saida = hora_brasilia
            else:
                # já registrou entrada e saída hoje
                raise HTTPException(status_code=409, detail="Estagiário já registrou entrada e saída hoje.")
        db.commit()
        db.refresh(reg)
        return reg

    # Demais papéis: ciclo completo
    if not reg:
        reg = models.RegistroPonto(
            colaborador_id=colaborador.id,
            data=hoje,
            entrada=hora_brasilia
        )
        db.add(reg)
    else:
        if not reg.saida_almoco:
            reg.saida_almoco = hora_brasilia
        elif not reg.volta_almoco:
            reg.volta_almoco = hora_brasilia
        elif not reg.saida:
            reg.saida = hora_brasilia
        else:
            raise HTTPException(status_code=409, detail="Todas as batidas já foram registradas para hoje.")

    db.commit()
    db.refresh(reg)
    return reg

def inserir_ponto_manual(
    db: Session,
    colaborador_id: int,
    data: date,
    *,
    entrada: Optional[datetime] = None,
    saida_almoco: Optional[datetime] = None,
    volta_almoco: Optional[datetime] = None,
    saida: Optional[datetime] = None,
    user_id: Optional[int] = None,
    justificativa: Optional[str] = None,
) -> models.RegistroPonto:
    # Verifica papel do usuário dono do colaborador para aplicar regra de estagiário
    colab = db.query(models.Colaborador).filter(models.Colaborador.id == colaborador_id).first()
    if not colab:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado.")

    dono = None
    if colab.user_id:
        dono = db.query(models.User).filter(models.User.id == colab.user_id).first()
    role_dono = (dono.role if dono else "funcionario") or "funcionario"

    if role_dono == "estagiario":
        # Bloqueia campos de almoço para estagiário (decisão explícita)
        if saida_almoco is not None or volta_almoco is not None:
            raise HTTPException(status_code=400, detail="Estagiário não registra pausa de almoço: apenas entrada e saída.")
        # Nada a fazer aqui além de permitir apenas entrada/saída

    reg = (
        db.query(models.RegistroPonto)
        .filter(models.RegistroPonto.colaborador_id == colaborador_id)
        .filter(models.RegistroPonto.data == data)
        .first()
    )

    if reg is None:
        reg = models.RegistroPonto(
            colaborador_id=colaborador_id,
            data=data,
            entrada=entrada,
            saida_almoco=saida_almoco if role_dono != "estagiario" else None,
            volta_almoco=volta_almoco if role_dono != "estagiario" else None,
            saida=saida,
            justificativa=justificativa or None,
            alterado_por_id=user_id,
        )
        db.add(reg)
    else:
        if entrada is not None:
            reg.entrada = entrada
        if role_dono != "estagiario":
            if saida_almoco is not None:
                reg.saida_almoco = saida_almoco
            if volta_almoco is not None:
                reg.volta_almoco = volta_almoco
        if saida is not None:
            reg.saida = saida
        if justificativa is not None:
            reg.justificativa = justificativa
        reg.alterado_por_id = user_id

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

    ponto.alterado_por_id = user_id
    db.commit()
    db.refresh(ponto)
    return ponto

def delete_ponto(db: Session, id: int):
    reg = db.query(models.RegistroPonto).filter_by(id=id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    db.delete(reg)
    db.commit()
    return {"message": "Registro de ponto excluído com sucesso"}

# —— Justificativas —— #
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
        raise HTTPException(status_code=404, detail="Justificativa não encontrado")
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
