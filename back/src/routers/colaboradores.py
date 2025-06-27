from fastapi import APIRouter, Depends
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
