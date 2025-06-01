from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src import crud, database, schemas

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/bater-ponto")
def bater_ponto(ponto: schemas.RegistroPontoCreate, db: Session = Depends(get_db)):
    registro = crud.registrar_ponto(db, ponto.colaborador_id)
    return {
        "mensagem": f"Ponto registrado no campo: {registro.__batida_feita__}",
        "registro": registro,
    }


@router.get("/pontos/{colaborador_id}", response_model=schemas.RegistroPontoResponse)
def get_ponto(colaborador_id: str, data: date, db: Session = Depends(get_db)):
    registro = crud.get_registro_por_dia(db, colaborador_id, data)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return registro
