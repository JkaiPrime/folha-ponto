from datetime import datetime
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from fastapi.responses import FileResponse
from src import schemas, crud, models
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
def enviar_justificativa(
    justificativa: str = Form(...),
    datas: str = Form(...),  # Ex: "2025-07-01,2025-07-02"
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    colab = crud.get_colaborador_by_user_id(db, user.id)
    if not colab:
        raise HTTPException(status_code=404, detail="Colaborador não vinculado ao usuário")

    filename = f"{datetime.now().isoformat()}_{arquivo.filename}".replace(':', '-')
    caminho = os.path.join(UPLOAD_DIR, filename)
    with open(caminho, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    datas_list = [d.strip() for d in datas.split(',') if d.strip()]
    if not datas_list:
        raise HTTPException(status_code=400, detail="Nenhuma data válida fornecida")

    ids_justificadas = []
    for data_str in datas_list:
        try:
            data_ref = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Data inválida: {data_str}")

        nova = schemas.JustificativaCreate(
            colaborador_id=colab.code,
            justificativa=justificativa,
            arquivo=filename,
            data_referente=data_ref
        )
        just = crud.salvar_justificativa(db, nova)
        ids_justificadas.append(just.id)

    return {
        "mensagem": f"{len(ids_justificadas)} justificativas salvas com sucesso.",
        "ids": ids_justificadas
    }

@router.get("/{colaborador_id}", response_model=List[schemas.JustificativaResponse])
def listar_justificativas_por_colaborador(
    colaborador_id: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    justificativas = (
        db.query(models.Justificativa)
        .filter(models.Justificativa.colaborador_id == colaborador_id)
        .order_by(models.Justificativa.data_envio.desc())
        .all()
    )
    return justificativas

@router.get("/arquivo/{nome_arquivo}")
def baixar_arquivo_justificativa(nome_arquivo: str):
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)
    if not os.path.isfile(caminho):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(caminho, filename=nome_arquivo)