from typing import List
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from src import schemas, crud , models

from src.database import SessionLocal
from src.routers.auth import get_current_user

router = APIRouter(prefix="/justificativas", tags=["justificativas"])

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("")
async def enviar_justificativa(
    colaborador_id: str = Form(...),
    justificativa: str = Form(...),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    # Verifica extensão
    ext = os.path.splitext(arquivo.filename)[1]
    if ext.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Arquivo deve ser PDF ou imagem")

    # Salva arquivo
    filename = f"{uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        buffer.write(await arquivo.read())

    nova = schemas.JustificativaCreate(
        colaborador_id=colaborador_id,
        justificativa=justificativa,
        arquivo=filename
    )

    just = crud.salvar_justificativa(db, nova)

    return {"mensagem": "Justificativa salva com sucesso", "id": just.id}


@router.get("/{colaborador_id}", response_model=List[schemas.JustificativaResponse])
def listar_justificativas_por_colaborador(
    colaborador_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)  # qualquer user autenticado pode ver as suas
):
    justificativas = (
        db.query(models.Justificativa)
        .filter(models.Justificativa.colaborador_id == colaborador_id)
        .order_by(models.Justificativa.data_envio.desc())
        .all()
    )
    return justificativas