# src/routers/colaboradores.py
from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from src.routers.auth import apenas_gestao, get_current_user
from src import models, database, schemas
from src.crud import normalize_cargo

router = APIRouter(prefix="/colaboradores", tags=["colaboradores"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------- Helper para extrair role com segurança ----------
def _role_from_colaborador(colab: models.Colaborador) -> str:
    """
    Retorna 'funcionario' | 'gestao' | 'estagiario' a partir do relacionamento com users.
    Fallback para 'funcionario' se algo vier vazio.
    """
    try:
        role = (colab.user.role if colab.user else None) or "funcionario"
    except Exception:
        role = "funcionario"
    return role if role in ("funcionario", "gestao", "estagiario") else "funcionario"


# ========================= Listar (mantido) =========================
@router.get("", response_model=List[schemas.ColaboradorResponse])
def listar_colaboradores(
    db: Session = Depends(get_db),
    _: models.User = Depends(apenas_gestao),  # igual sua versão antiga (ajuste se quiser abrir)
):
    cols = (
        db.query(models.Colaborador)
        .order_by(models.Colaborador.nome)
        .all()
    )
    return cols


# ========================= GET por ID (novo: traz role) =========================
@router.get("/{id}", response_model=schemas.ColaboradorWithRoleResponse)
def get_colaborador(
    id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    colab = (
        db.query(models.Colaborador)
        .options(joinedload(models.Colaborador.user))
        .filter(models.Colaborador.id == id)
        .first()
    )
    if not colab:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    role = _role_from_colaborador(colab)
    cargo = getattr(colab.user, "cargo", None) if colab.user else None
    return {"id": colab.id, "nome": colab.nome, "code": colab.code, "role": role, "cargo": cargo}


# ===== GET: por user_id (mantido, com cargo/email/role) =====
@router.get("/by-user/{user_id}")
def get_colaborador_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    colab = (
        db.query(models.Colaborador)
        .options(joinedload(models.Colaborador.user))
        .filter(models.Colaborador.user_id == user_id)
        .first()
    )
    if not colab:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado para este usuário.")

    user = colab.user or db.query(models.User).filter(models.User.id == user_id).first()
    role = _role_from_colaborador(colab)

    return {
        "id": colab.id,
        "user_id": user_id,
        "code": colab.code,
        "cargo": getattr(user, "cargo", None),   # cargo vem de users
        "nome": colab.nome,
        "email": user.email if user else None,
        "role": role,
    }


# ===== PATCH: Upsert por user_id (mantido) =====
@router.patch("/by-user/{user_id}")
def upsert_colaborador_by_user(
    user_id: int,
    payload: schemas.ColaboradorUpsert,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    colab = db.query(models.Colaborador).filter(models.Colaborador.user_id == user_id).first()

    # Cria se não existe — exige code
    if not colab:
        if not payload.code:
            raise HTTPException(status_code=422, detail="Para criar o vínculo informe 'code' (6 dígitos).")
        colab = models.Colaborador(
            code=str(payload.code),
            nome=(payload.nome or user.nome or "").strip(),
            user_id=user.id
        )
        db.add(colab)
    else:
        # Atualiza code se veio
        if payload.code is not None:
            code_str = str(payload.code).strip()
            if code_str and not code_str.isdigit():
                raise HTTPException(status_code=422, detail="Código deve conter apenas dígitos.")
            if code_str:
                colab.code = code_str
        # Atualiza nome se veio
        if payload.nome is not None and payload.nome.strip() != "":
            colab.nome = payload.nome.strip()

    # Atualiza cargo (em users)
    if payload.cargo is not None:
        user.cargo = normalize_cargo(payload.cargo)

    db.add_all([colab, user])
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        # deixa a mesma semântica de antes (propaga para o handler global/log)
        raise e

    db.refresh(colab)
    db.refresh(user)

    return {
        "id": colab.id,
        "user_id": colab.user_id,
        "code": colab.code,
        "cargo": user.cargo,
        "nome": colab.nome
    }


# ===== POST: criar colaborador (mantido) =====
@router.post("")
def criar_colaborador(
    payload: schemas.ColaboradorCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    user = None
    if payload.email_usuario:
        user = db.query(models.User).filter(models.User.email == payload.email_usuario).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado com esse email")

    colab = models.Colaborador(
        code=payload.code,
        nome=(payload.nome or (user.nome if user else "")).strip(),
        user_id=user.id if user else None
    )
    db.add(colab)

    # sincroniza cargo em users, se vier e tivermos um user associado
    if user and payload.cargo is not None:
        user.cargo = normalize_cargo(payload.cargo)
        db.add(user)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(colab)

    return {
        "id": colab.id,
        "user_id": colab.user_id,
        "code": colab.code,
        "nome": colab.nome
    }


# ===== DELETE: remover por code (mantido / adiciona segurança de gestão) =====
@router.delete("/{code}")
def delete_colaborador(
    code: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(apenas_gestao)
):
    colab = db.query(models.Colaborador).filter(models.Colaborador.code == code).first()
    if not colab:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    db.delete(colab)
    db.commit()
    return {"message": "Colaborador excluído com sucesso"}
