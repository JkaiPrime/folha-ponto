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

@router.get("/colaborador")
def get_colaborador_vinculado(
    db: Session = Depends(get_db),
    usuario: models.User = Depends(get_current_user)
):
    print("[DEBUG] /me/colaborador chamado por:", usuario.email)
    colaborador = db.query(models.Colaborador).filter(models.Colaborador.user_id == usuario.id).first()
    if not colaborador:
        raise HTTPException(status_code=404, detail="Usuário não está vinculado a um colaborador.")
    print("[DEBUG] Retornando dados do colaborador:", colaborador.code, "Role:", usuario.role)

    return {
        "id": colaborador.id,
        "code": colaborador.code,
        "nome": colaborador.nome,
        "email": usuario.email,
        "role": usuario.role  # ✅ Adiciona a role
    }
