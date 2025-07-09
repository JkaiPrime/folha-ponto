from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.routers.auth import get_current_user
from src import models, database, schemas

router = APIRouter(prefix="/me", tags=["me"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/colaborador", response_model=schemas.ColaboradorResponse)
def get_colaborador_vinculado(
    db: Session = Depends(get_db),
    usuario: models.User = Depends(get_current_user)
):
    colaborador = db.query(models.Colaborador).filter(models.Colaborador.user_id == usuario.id).first()
    if not colaborador:
        raise HTTPException(status_code=404, detail="Usuário não está vinculado a um colaborador.")
    return colaborador
