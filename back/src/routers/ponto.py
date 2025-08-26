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
from src.utils.jornada_workalendar import (
    validar_batida,
    validar_dia,
)

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


def _resolve_colaborador(
    db: Session,
    user: models.User,
    colaborador_id: int | str | None
) -> Optional[models.Colaborador]:
    if colaborador_id is None:
        # 🔁 tenta achar o colaborador vinculado ao user logado
        return (
            db.query(models.Colaborador)
            .filter(models.Colaborador.user_id == user.id)
            .first()
        )
    if isinstance(colaborador_id, int):
        return (
            db.query(models.Colaborador)
            .filter(models.Colaborador.id == colaborador_id)
            .first()
        )
    # string -> code de 6 dígitos
    return (
        db.query(models.Colaborador)
        .filter(models.Colaborador.code == colaborador_id)
        .first()
    )

@router.get(
    "/status",
    summary="Status para bater ponto (bloqueia fds/feriado)"
)
def status_ponto(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    agora = get_hora_brasilia()
    ok, motivo = validar_dia(agora)  # usa sua regra atual: bloqueia fds + feriado
    return {
        "allowed": ok,
        "message": motivo or "Liberado para bater ponto.",
        "now": agora.isoformat()
    }



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
    hoje = hora_brasilia.date()

    # 1) Dia permitido?
    ok, motivo = validar_dia(hora_brasilia)
    if not ok:
        raise HTTPException(status_code=403, detail=motivo)

    # 2) Resolve colaborador (id | code | sessão)
    colaborador = _resolve_colaborador(db, user, ponto.colaborador_id)
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    # 3) Quantas batidas hoje?
    batidas_hoje = (
        db.query(models.RegistroPonto)
        .filter(models.RegistroPonto.colaborador_id == colaborador.id)
        .filter(models.RegistroPonto.data == hoje)
        .count()
    )

    # 4) Regras unificadas
    ok, motivo = validar_batida(hora_brasilia, batidas_hoje)
    if not ok:
        raise HTTPException(status_code=403, detail=motivo)

    # 5) Auditoria + gravação
    crud.registrar_auditoria(
        db,
        user.id,
        action="marcar_ponto",
        endpoint="/pontos/bater-ponto",
        detail=f"Horário: {hora_brasilia.isoformat()}",
    )

    # ⚠️ Seu CRUD parece esperar 'code' (string). Mantendo compat:
    return crud.registrar_ponto(db, colaborador.code, hora_brasilia)

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


@router.get(
    "/hoje/me",
    response_model=List[schemas.RegistroComColaboradorResponse],
    summary="Pontos do usuário logado no dia atual"
)
def pontos_hoje_me(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    hoje = date.today()
    # resolve colaborador via sessão
    colaborador = (
        db.query(models.Colaborador)
        .filter(models.Colaborador.user_id == user.id)
        .first()
    )
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não vinculado ao usuário.")

    # Reaproveita a mesma query de por-data (id numérico):
    pontos = (
        db.query(models.RegistroPonto)
        .options(
            joinedload(models.RegistroPonto.colaborador),
            joinedload(models.RegistroPonto.alterado_por)
        )
        .filter(models.RegistroPonto.colaborador_id == colaborador.id)
        .filter(models.RegistroPonto.data >= hoje)
        .filter(models.RegistroPonto.data <= hoje)
        .order_by(models.RegistroPonto.data)
        .all()
    )

    # enriquecer com justificativas (como em /por-data)
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

@router.get(
    "/{colaborador_id:int}",
    response_model=List[schemas.RegistroPontoResponse],
    summary="Listar pontos por colaborador (autenticado)"
)
def get_por_colaborador(
    colaborador_id: int,
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



'''
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
'''

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

