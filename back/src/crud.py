from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models


def registrar_ponto(db: Session, colaborador_id: str):
    hoje = date.today()
    agora = datetime.now()

    registro = (
        db.query(models.RegistroPonto)
        .filter_by(colaborador_id=colaborador_id, data=hoje)
        .first()
    )

    # 1️⃣ Primeira batida (entrada)
    if not registro:
        registro = models.RegistroPonto(
            colaborador_id=colaborador_id, data=hoje, entrada=agora
        )
        db.add(registro)
        db.commit()
        db.refresh(registro)
        registro.__batida_feita__ = "entrada"
        return registro

    # 2️⃣ Saída para almoço
    if not registro.saida_almoco:
        if agora < registro.entrada:
            raise HTTPException(
                status_code=400,
                detail="Horário inválido: saída para almoço antes da entrada.",
            )
        registro.saida_almoco = agora
        campo = "saida_almoco"

    # 3️⃣ Volta do almoço
    elif not registro.volta_almoco:
        if agora < registro.saida_almoco:
            raise HTTPException(
                status_code=400,
                detail="Horário inválido:\
                    volta do almoço antes da saída para almoço.",
            )
        registro.volta_almoco = agora
        campo = "volta_almoco"

    # 4️⃣ Saída do expediente
    elif not registro.saida:
        if agora < registro.volta_almoco:
            raise HTTPException(
                status_code=400,
                detail="Horário inválido: saída antes da volta do almoço.",
            )
        registro.saida = agora
        campo = "saida"

    # 🛑 Nenhuma batida disponível
    else:
        raise HTTPException(
            status_code=400,
            detail="Todas as batidas de ponto já foram registradas para hoje.",
        )

    db.commit()
    db.refresh(registro)
    registro.__batida_feita__ = campo
    return registro


def get_registro_por_dia(db: Session, colaborador_id: str, dia: date):
    return (
        db.query(models.RegistroPonto)
        .filter_by(colaborador_id=colaborador_id, data=dia)
        .first()
    )
