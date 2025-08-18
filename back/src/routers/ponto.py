from typing import List, Optional
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from src import models, crud, schemas
from src.database import SessionLocal
from src.routers.auth import apenas_funcionario, apenas_gestao, get_current_user
from src.schemas import RegistroComColaboradorResponse, RegistroPontoManualCreate
from src.utils.timezone import get_hora_brasilia

router = APIRouter(prefix="/pontos", tags=["pontos"])
BR_TZ = ZoneInfo("America/Sao_Paulo") 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def _ensure_tz(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=BR_TZ)
    return dt.astimezone(BR_TZ)

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
    hora_brasilia = get_hora_brasilia()

    crud.registrar_auditoria(
        db,
        user.id,
        action="marcar_ponto",
        endpoint="/pontos/bater-ponto",
        detail=f"Horário: {hora_brasilia.isoformat()}"
    )

    return crud.registrar_ponto(db, ponto.colaborador_id, hora_brasilia)

@router.post(
    "/inserir-manual",
    response_model=schemas.RegistroPontoResponse,
    summary="Inserir/atualizar ponto manual (somente gestão)"
)
def inserir_manual(
    payload: RegistroPontoManualCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(apenas_gestao)
):
    # Localiza colaborador pelo code
    colaborador = (
        db.query(models.Colaborador)
        .filter(models.Colaborador.code == payload.code)
        .first()
    )
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado pelo code.")

    # Normaliza timezone para Brasília
    entrada = _ensure_tz(payload.entrada)
    saida_almoco = _ensure_tz(payload.saida_almoco)
    volta_almoco = _ensure_tz(payload.volta_almoco)
    saida = _ensure_tz(payload.saida)

    # Auditoria
    crud.registrar_auditoria(
        db,
        user.id,
        action="inserir_ponto_manual",
        endpoint="/pontos/inserir-manual",
        detail=f"code={payload.code} data={payload.data.isoformat()} "
               f"entrada={entrada} saida_almoco={saida_almoco} volta_almoco={volta_almoco} saida={saida}"
    )

    # Insere/atualiza
    reg = crud.inserir_ponto_manual(
        db=db,
        colaborador_id=colaborador.id,
        data=payload.data,
        entrada=entrada,
        saida_almoco=saida_almoco,
        volta_almoco=volta_almoco,
        saida=saida,
        user_id=user.id,
        justificativa=payload.justificativa,
    )
    return reg

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


@router.get("/por-data", response_model=List[schemas.RegistroComColaboradorResponse])
def pontos_por_data(
    colaborador_id: int = Query(...),
    inicio: date = Query(...),
    fim: date = Query(...),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    pontos = (
        db.query(models.RegistroPonto)
        .options(
            joinedload(models.RegistroPonto.colaborador),
            joinedload(models.RegistroPonto.alterado_por)
        )
        .filter(models.RegistroPonto.colaborador_id == colaborador_id)
        .filter(models.RegistroPonto.data >= inicio)
        .filter(models.RegistroPonto.data <= fim)
        .order_by(models.RegistroPonto.data)
        .all()
    )

    for ponto in pontos:
        justificativa = (
            db.query(models.Justificativa)
            .options(joinedload(models.Justificativa.avaliador))
            .filter(models.Justificativa.colaborador_id == colaborador_id)
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
    summary="Excluir ponto (autenticado)"
)
def delete_ponto(
    id: int,
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    return crud.delete_ponto(db, id)

