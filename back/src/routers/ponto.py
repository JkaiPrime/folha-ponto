from typing import List, Optional
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime, timedelta

from src import models, crud, schemas
from src.database import SessionLocal
from src.routers.auth import apenas_gestao, get_current_user
from src.schemas import RegistroComColaboradorResponse, RegistroPontoManualCreate
from src.utils.timezone import get_hora_brasilia
from src.utils.jornada_workalendar import validar_dia  # manter validação de dia (fds/feriado)

router = APIRouter(prefix="/pontos", tags=["pontos"])
BR_TZ = ZoneInfo("America/Sao_Paulo")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------- Helpers -----------------
def _ensure_tz(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=BR_TZ)
    return dt.astimezone(BR_TZ)

def _combine_dt(d: date, hhmm: Optional[str]) -> Optional[datetime]:
    """
    Combina YYYY-MM-DD + HH:MM em datetime tz-aware (America/Sao_Paulo).
    """
    if not hhmm:
        return None
    h, m = hhmm.split(":")
    dt = datetime(d.year, d.month, d.day, int(h), int(m), 0)
    return dt.replace(tzinfo=BR_TZ)


def _resolve_colaborador(
    db: Session,
    user: models.User,
    colaborador_id: int | str | None
) -> Optional[models.Colaborador]:
    if colaborador_id is None:
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
    # string = code de 6 dígitos
    return (
        db.query(models.Colaborador)
        .filter(models.Colaborador.code == colaborador_id)
        .first()
    )


def _get_reg_hoje(
    db: Session,
    colaborador_id: int,
    dia: date
) -> Optional[models.RegistroPonto]:
    return (
        db.query(models.RegistroPonto)
        .filter(models.RegistroPonto.colaborador_id == colaborador_id)
        .filter(models.RegistroPonto.data == dia)
        .first()
    )


def _proxima_acao(role: str, reg: Optional[models.RegistroPonto]) -> Optional[str]:
    """
    Decide qual campo preencher AGORA:
    - 'estagiario': entrada -> saida
    - demais: entrada -> saida_almoco -> volta_almoco -> saida
    Retorna None se não há mais batidas possíveis hoje.
    """
    if reg is None or reg.entrada is None:
        return "entrada"

    if role == "estagiario":
        if reg.saida is None:
            return "saida"
        return None

    # ciclo completo
    if reg.saida_almoco is None:
        return "saida_almoco"
    if reg.volta_almoco is None:
        return "volta_almoco"
    if reg.saida is None:
        return "saida"
    return None


def _registrar_por_acao(
    db: Session,
    colaborador_id: int,
    when: datetime,
    action: str
) -> models.RegistroPonto:
    """
    Persiste a batida da 'action'. Se você já adicionou crud.registrar_batida,
    usamos ela; caso contrário, cai no fallback inline.
    """
    # Tenta usar crud.registrar_batida se existir:
    fn = getattr(crud, "registrar_batida", None)
    if callable(fn):
        return fn(db, colaborador_id=colaborador_id, when=when, action=action)

    # ---- Fallback (inline) ----
    reg = _get_reg_hoje(db, colaborador_id, when.date())
    if not reg:
        reg = models.RegistroPonto(colaborador_id=colaborador_id, data=when.date())
        db.add(reg)
        db.commit()
        db.refresh(reg)

    if action == "entrada":
        if reg.entrada is not None:
            raise HTTPException(status_code=409, detail="Entrada já registrada para hoje.")
        reg.entrada = when

    elif action == "saida_almoco":
        if reg.entrada is None:
            raise HTTPException(status_code=409, detail="Não é possível sair para almoço antes da entrada.")
        if reg.saida_almoco is not None:
            raise HTTPException(status_code=409, detail="Saída para almoço já registrada.")
        reg.saida_almoco = when

    elif action == "volta_almoco":
        if reg.saida_almoco is None:
            raise HTTPException(status_code=409, detail="Volta do almoço sem saída prévia.")
        if reg.volta_almoco is not None:
            raise HTTPException(status_code=409, detail="Volta do almoço já registrada.")
        reg.volta_almoco = when

    elif action == "saida":
        if reg.entrada is None:
            raise HTTPException(status_code=409, detail="Não é possível registrar saída sem entrada.")
        if reg.saida is not None:
            raise HTTPException(status_code=409, detail="Saída já registrada para hoje.")
        reg.saida = when

    else:
        raise HTTPException(status_code=400, detail="Ação de batida inválida.")

    db.commit()
    db.refresh(reg)
    return reg


# ----------------- Endpoints -----------------
@router.get(
    "/status",
    summary="Status para bater ponto (bloqueia fds/feriado e indica próxima ação)"
)
def status_ponto(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    agora = get_hora_brasilia()
    ok, motivo = validar_dia(agora)

    # Tenta descobrir a próxima ação para o colaborador logado
    next_action = None
    colaborador = _resolve_colaborador(db, user, None)
    if colaborador:
        reg = _get_reg_hoje(db, colaborador.id, agora.date())
        next_action = _proxima_acao(user.role, reg)

    return {
        "allowed": ok,
        "message": motivo or "Liberado para bater ponto.",
        "now": agora.isoformat(),
        "role": user.role,
        "next_action": next_action
    }


@router.post(
    "/bater-ponto",
    response_model=schemas.RegistroPontoResponse,
    summary="Bater ponto (autenticado; estagiário só entrada/saída)"
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

    # 3) Carrega estado atual do dia e decide próxima ação pelo papel
    reg_hoje = _get_reg_hoje(db, colaborador.id, hoje)
    action = _proxima_acao(user.role, reg_hoje)
    if action is None:
        raise HTTPException(status_code=403, detail="Você já registrou todas as batidas permitidas para hoje.")

    # 4) Auditoria
    crud.registrar_auditoria(
        db,
        user.id,
        action=f"marcar_ponto:{action}",
        endpoint="/pontos/bater-ponto",
        detail=f"Horário: {hora_brasilia.isoformat()} code={colaborador.code}"
    )

    # 5) Grava a batida (por ação)
    reg = _registrar_por_acao(db, colaborador_id=colaborador.id, when=hora_brasilia, action=action)
    return reg


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
    summary="Atualizar ponto (somente gestão)"
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
    colaborador = (
        db.query(models.Colaborador)
        .filter(models.Colaborador.user_id == user.id)
        .first()
    )
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não vinculado ao usuário.")

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





@router.post(
    "/inserir-periodo",
    response_model=schemas.BulkInsertResponse,
    summary="Inserir/atualizar pontos em um período (somente gestão)"
)
def inserir_periodo(
    payload: schemas.RegistroPontoPeriodoCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(apenas_gestao)
):
    # 1) localizar colaborador pelo code
    colaborador = (
        db.query(models.Colaborador)
        .filter(models.Colaborador.code == payload.code)
        .first()
    )
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado pelo code.")

    itens: List[schemas.BulkInsertItem] = []
    d = payload.inicio
    sucesso = 0
    pulados = 0
    total = 0

    while d <= payload.fim:
        total += 1
        # 2) regras de pulo (fds/feriados)
        weekday = d.weekday()  # 0=seg ... 5=sab 6=dom
        if weekday == 5 and not payload.incluir_sabado:
            itens.append(schemas.BulkInsertItem(data=d, inserted=False, reason="Sábado (pulado)"))
            pulados += 1
            d += timedelta(days=1)
            continue
        if weekday == 6 and not payload.incluir_domingo:
            itens.append(schemas.BulkInsertItem(data=d, inserted=False, reason="Domingo (pulado)"))
            pulados += 1
            d += timedelta(days=1)
            continue

        if payload.pular_feriados:
            allowed, motivo = validar_dia(datetime(d.year, d.month, d.day, 12, 0, tzinfo=BR_TZ))
            # validar_dia costuma bloquear fds também; como já tratamos acima, aqui o resto é feriado
            if not allowed:
                itens.append(schemas.BulkInsertItem(data=d, inserted=False, reason=motivo or "Feriado"))
                pulados += 1
                d += timedelta(days=1)
                continue

        # 3) montar datetimes
        entrada      = _combine_dt(d, payload.entrada)
        saida_almoco = _combine_dt(d, payload.saida_almoco)
        volta_almoco = _combine_dt(d, payload.volta_almoco)
        saida        = _combine_dt(d, payload.saida)

        # 4) inserir/atualizar
        try:
            crud.inserir_ponto_manual(
                db=db,
                colaborador_id=colaborador.id,
                data=d,
                entrada=entrada,
                saida_almoco=saida_almoco,
                volta_almoco=volta_almoco,
                saida=saida,
                user_id=user.id,
                justificativa=payload.justificativa,
            )
            itens.append(schemas.BulkInsertItem(data=d, inserted=True))
            sucesso += 1
        except Exception as e:
            itens.append(schemas.BulkInsertItem(data=d, inserted=False, reason=str(e)))
            pulados += 1

        d += timedelta(days=1)

    return schemas.BulkInsertResponse(
        total=total, sucesso=sucesso, pulados=pulados, itens=itens
    )



@router.get(
    "/metrics/hoje",
    summary="Métricas resumidas do dia atual (presentes, ausentes, inconsistências, alterados)"
)
def metrics_hoje(
    db: Session = Depends(get_db),
    user: models.User = Depends(apenas_gestao)  # somente gestão vê
):
    hoje = date.today()

    # Todos colaboradores ativos
    total_colabs = db.query(models.Colaborador).count()

    # Registros de hoje
    registros = (
        db.query(models.RegistroPonto)
        .options(joinedload(models.RegistroPonto.alterado_por))
        .filter(models.RegistroPonto.data == hoje)
        .all()
    )

    presentes = len(registros)
    ausentes = total_colabs - presentes

    # Inconsistências = registros incompletos
    inconsistencias = 0
    for r in registros:
        if r.entrada and not r.saida:
            inconsistencias += 1
        if r.saida_almoco and not r.volta_almoco:
            inconsistencias += 1

    # Alterados = tiveram user em alterado_por
    alterados = sum(1 for r in registros if r.alterado_por is not None)

    return {
        "data": hoje.isoformat(),
        "total_colaboradores": total_colabs,
        "presentes": presentes,
        "ausentes": ausentes,
        "inconsistencias": inconsistencias,
        "alterados": alterados,
    }
