from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy.orm import joinedload
from src import models
from src import crud, schemas
from src.database import SessionLocal
from src.routers.auth import apenas_funcionario, get_current_user, verifica_token_acesso
from src.schemas import RegistroComColaboradorResponse


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
    summary="Bater ponto (autenticado)"
)
def bater_ponto(
    ponto: schemas.RegistroPontoCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
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


@router.get("/hoje", response_model=List[RegistroComColaboradorResponse])
def listar_pontos_hoje(db: Session = Depends(get_db)):
    hoje = date.today()

    registros = (
        db.query(models.RegistroPonto)
        .options(joinedload(models.RegistroPonto.colaborador))
        .filter(models.RegistroPonto.data == hoje)
        .all()
    )

    # Enriquecer com justificativas (opcional, se quiser que venha direto)
    for registro in registros:
        just = (
            db.query(models.Justificativa)
            .filter(
                models.Justificativa.colaborador_id == registro.colaborador_id,
                models.Justificativa.data_referente == hoje
            )
            .first()
        )
        if just:
            registro.justificativa = just.justificativa
            registro.arquivo = just.arquivo

    return registros

@router.get("/por-data", response_model=List[schemas.RegistroPontoResponse])
def listar_pontos_por_data(
    colaborador_id: str,
    inicio: date,
    fim: date,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    # Pegar pontos
    pontos = db.query(models.RegistroPonto).filter(
        models.RegistroPonto.colaborador_id == colaborador_id,
        models.RegistroPonto.data.between(inicio, fim)
    ).all()

    # Pegar justificativas no mesmo período
    justs = db.query(models.Justificativa).filter(
        models.Justificativa.colaborador_id == colaborador_id,
        models.Justificativa.data_referente.between(inicio, fim)
    ).all()

    # Organizar por data
    registros_por_data = {}
    for ponto in pontos:
        registros_por_data[ponto.data] = ponto

    for just in justs:
        if just.data_referente not in registros_por_data:
            registros_por_data[just.data_referente] = models.RegistroPonto(
                colaborador_id=colaborador_id,
                data=just.data_referente
            )
        registros_por_data[just.data_referente].justificativa = just.justificativa
        registros_por_data[just.data_referente].arquivo = just.arquivo

    return list(registros_por_data.values())

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
