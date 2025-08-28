from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, StringConstraints
from typing import Annotated, Optional, TypeAlias
from sqlalchemy.orm import Session
from src.routers.auth import get_current_user
from src import models, database

router = APIRouter(prefix="/colaboradores", tags=["colaboradores"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic v2: string 6 dígitos
DigitCode: TypeAlias = Annotated[str, StringConstraints(min_length=6, max_length=6, pattern=r"^\d{6}$")]

class ColaboradorUpdate(BaseModel):
    code: Optional[DigitCode] = None
    cargo: Optional[str] = None  # <- vamos gravar em users.cargo
    nome: Optional[str] = None
    email_usuario: Optional[str] = None

@router.get("/by-user/{user_id}")
def get_colaborador_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    colab = db.query(models.Colaborador).filter(models.Colaborador.user_id == user_id).first()
    if not colab:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado para este usuário.")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    return {
        "id": colab.id,
        "user_id": user_id,
        "code": getattr(colab, "code", None),
        "cargo": getattr(user, "cargo", None),  # <- cargo vem de users
        "nome": colab.nome,
        "email": user.email if user else None,
        "role": user.role if user else None,
    }

@router.patch("/by-user/{user_id}")
def update_colaborador_by_user(
    user_id: int,
    payload: ColaboradorUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    colab = db.query(models.Colaborador).filter(models.Colaborador.user_id == user_id).first()
    if not colab:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado para este usuário.")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    print("[DEBUG] PATCH /colaboradores/by-user payload:", payload.model_dump())

    # Atualiza CODE em colaboradores
    if payload.code is not None:
        code_str = str(payload.code).strip()
        if code_str and not code_str.isdigit():
            raise HTTPException(status_code=422, detail="Código deve conter apenas dígitos.")
        colab.code = code_str or None

    # Atualiza CARGO em users
    if payload.cargo is not None:
        cargo_norm = payload.cargo.strip()
        if cargo_norm == "" or cargo_norm.lower() in {"não definido", "nao definido", "não-definido", "nao-definido"}:
            user.cargo = None
        else:
            user.cargo = cargo_norm

    # Nome do colaborador (opcional)
    if payload.nome is not None and payload.nome.strip() != "":
        colab.nome = payload.nome.strip()

    # Email do usuário (opcional)
    if payload.email_usuario is not None:
        user.email = payload.email_usuario

    print("[DEBUG] Antes commit -> code(colab):", getattr(colab, "code", None), "cargo(user):", getattr(user, "cargo", None))
    db.add_all([colab, user])
    db.commit()
    db.refresh(colab)
    db.refresh(user)
    print("[DEBUG] Depois commit -> code(colab):", getattr(colab, "code", None), "cargo(user):", getattr(user, "cargo", None))

    return {
        "id": colab.id,
        "user_id": colab.user_id,
        "code": getattr(colab, "code", None),
        "cargo": getattr(user, "cargo", None),  # <- retorna o cargo atualizado (users)
        "nome": colab.nome,
    }

# (se você ainda usa PATCH por colaborador_id em algum lugar, mantenha, mas sem mexer no cargo)
@router.patch("/{colaborador_id}")
def update_colaborador(
    colaborador_id: int,
    payload: ColaboradorUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    colab = db.query(models.Colaborador).filter(models.Colaborador.id == colaborador_id).first()
    if not colab:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado.")

    if payload.code is not None:
        code_str = str(payload.code).strip()
        if code_str and not code_str.isdigit():
            raise HTTPException(status_code=422, detail="Código deve conter apenas dígitos.")
        colab.code = code_str or None

    # NÃO tocamos no cargo aqui (está em users)
    if payload.nome is not None and payload.nome.strip() != "":
        colab.nome = payload.nome.strip()

    db.add(colab)
    db.commit()
    db.refresh(colab)

    # Para consistência, podemos devolver o cargo do user atual:
    user = db.query(models.User).filter(models.User.id == colab.user_id).first()

    return {
        "id": colab.id,
        "user_id": colab.user_id,
        "code": getattr(colab, "code", None),
        "cargo": getattr(user, "cargo", None),
        "nome": colab.nome,
    }
