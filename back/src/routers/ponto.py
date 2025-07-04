from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from src import models
from src import crud, schemas
from src.database import SessionLocal
from src.routers.auth import get_current_user, verifica_token_acesso


router = APIRouter(prefix="/pontos", tags=["pontos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/bater-ponto",
    response_model=schemas.RegistroPontoResponse,
    summary="Bater ponto (sem autenticação)"
)
def bater_ponto(
    ponto: schemas.RegistroPontoCreate,
    db: Session = Depends(get_db),
):
    return crud.registrar_ponto(db, ponto.colaborador_id)

@router.get(
    "",
    response_model=list[schemas.RegistroPontoResponse],
    summary="Listar todos os pontos (autenticado)"
)
def list_pontos(
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    return crud.list_pontos(db)

@router.put(
    "/{id}",
    response_model=schemas.RegistroPontoResponse,
    summary="Atualizar ponto (autenticado)"
)
def update_ponto(
    id: int,
    dados: schemas.RegistroPontoUpdate,
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    return crud.update_ponto(db, id, dados)


@router.get("/hoje", response_model=list[schemas.RegistroPontoResponse], dependencies=[Depends(verifica_token_acesso)])
def listar_pontos_hoje(db: Session = Depends(get_db)):
    hoje = date.today()
    registros = (
        db.query(models.RegistroPonto)
        .join(models.Colaborador)
        .filter(models.RegistroPonto.data == hoje)
        .all()
    )
    return registros

@router.get("/por-data", response_model=List[schemas.RegistroPontoResponse])
def listar_pontos_por_data(
    colaborador_id: str,

    inicio: date,
    fim: date,
    db: Session = Depends(get_db),
    usuario: models.User = Depends(verifica_token_acesso)
):
    registros = db.query(models.RegistroPonto).filter(
        models.RegistroPonto.colaborador_id == colaborador_id,
        models.RegistroPonto.data >= inicio,
        models.RegistroPonto.data <= fim
    ).all()
    return registros

@router.delete(
    "/{id}",
    response_model=schemas.RegistroPontoResponse,
    summary="Excluir ponto (autenticado)"
)
def delete_ponto(
    id: int,
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    return crud.delete_ponto(db, id)

@router.get(
    "/{colaborador_id}",
    response_model=list[schemas.RegistroPontoResponse],
    summary="Listar pontos por colaborador (autenticado)"
)
def get_por_colaborador(
    colaborador_id: str,
    data: date | None = None,
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    regs = crud.list_pontos(db)
    regs = [r for r in regs if r.colaborador_id == colaborador_id]
    if data:
        regs = [r for r in regs if r.data == data]
    if not regs:
        raise HTTPException(status_code=404, detail="Nenhum registro encontrado")
    return regs
