from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src import crud, schemas
from src.database import SessionLocal
from src.routers.auth import get_current_user

router = APIRouter(prefix="/colaboradores", tags=["colaboradores"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=schemas.ColaboradorResponse)
def create_colaborador(
    colab: schemas.ColaboradorCreate,
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    return crud.create_colaborador(db, colab)

@router.get("", response_model=list[schemas.ColaboradorResponse])
def list_colaboradores(
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    return crud.list_colaboradores(db)

@router.delete("/{colaborador_id}", status_code=204)
def delete_colaborador(
    colaborador_id: str,
    db: Session = Depends(get_db),
    _: schemas.UserResponse = Depends(get_current_user)
):
    success = crud.delete_colaborador(db, colaborador_id)
    if not success:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
