from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from src import models, crud, schemas
from src.database import SessionLocal
from src.routers.auth import apenas_funcionario, apenas_gestao, get_current_user
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
    user: models.User = Depends(get_current_user)
):
    crud.registrar_auditoria(
        db,
        user.id,
        action="marcar_ponto",
        endpoint="/pontos/bater-ponto",
        detail=f"Horário: {datetime.now().isoformat()}"
    )
    return crud.registrar_ponto(db, ponto.colaborador_id)

@router.get(
    "",
    response_model=List[schemas.RegistroPontoResponse],
    summary="Listar todos os pontos (autenticado)"
)
def list_pontos(
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    return db.query(models.RegistroPonto).options(
        joinedload(models.RegistroPonto.alterado_por),
        joinedload(models.RegistroPonto.colaborador)
    ).all()

@router.put(
    "/{id}",
    response_model=schemas.RegistroPontoResponse,
    summary="Atualizar ponto (autenticado)"
)
def editar_ponto(
    id: int,
    atualizacao: schemas.RegistroPontoUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(apenas_gestao)
):
    return crud.update_ponto(
        db=db,
        id=id,
        dados=atualizacao,
        user_id=user.id
    )

@router.get("/hoje", response_model=List[RegistroComColaboradorResponse])
def listar_pontos_hoje(db: Session = Depends(get_db)):
    hoje = date.today()

    registros = (
        db.query(models.RegistroPonto)
        .options(
            joinedload(models.RegistroPonto.colaborador),
            joinedload(models.RegistroPonto.alterado_por)
        )
        .filter(models.RegistroPonto.data == hoje)
        .all()
    )

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

# Endpoint fixo DEVE vir antes do endpoint dinâmico
@router.get("/por-data", response_model=List[schemas.RegistroComColaboradorResponse])
def pontos_por_data(
    colaborador_code: str = Query(..., min_length=6, max_length=6),
    inicio: date = Query(...),
    fim: date = Query(...),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    colaborador = db.query(models.Colaborador).filter(models.Colaborador.code == colaborador_code).first()

    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    pontos = (
        db.query(models.RegistroPonto)
        .options(
            joinedload(models.RegistroPonto.colaborador),
            joinedload(models.RegistroPonto.alterado_por)
        )
        .filter(models.RegistroPonto.colaborador_id == colaborador.id)
        .filter(models.RegistroPonto.data >= inicio)
        .filter(models.RegistroPonto.data <= fim)
        .order_by(models.RegistroPonto.data)
        .all()
    )

    for ponto in pontos:
        justificativa = (
            db.query(models.Justificativa)
            .options(joinedload(models.Justificativa.avaliador))
            .filter(models.Justificativa.colaborador_id == colaborador.id)
            .filter(models.Justificativa.data_referente == ponto.data)
            .order_by(models.Justificativa.data_envio.desc())
            .first()
        )
        if justificativa:
            setattr(ponto, "status", justificativa.status)
            setattr(ponto, "avaliador", justificativa.avaliador)

    return pontos



# Endpoint dinâmico precisa vir depois
@router.get(
    "/{colaborador_id}",
    response_model=List[schemas.RegistroPontoResponse],
    summary="Listar pontos por colaborador (autenticado)"
)
def get_por_colaborador(
    colaborador_id: str,
    data: date | None = None,
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    regs = (
        db.query(models.RegistroPonto)
        .options(
            joinedload(models.RegistroPonto.alterado_por),
            joinedload(models.RegistroPonto.colaborador)
        )
        .filter(models.RegistroPonto.colaborador_id == colaborador_id)
        .all()
    )
    if data:
        regs = [r for r in regs if r.data == data]
    if not regs:
        raise HTTPException(status_code=404, detail="Nenhum registro encontrado")
    return regs


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

