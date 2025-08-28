from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import AuditLog


router = APIRouter(prefix="/auditoria", tags=["auditoria"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
@router.get("/", response_model=List[dict])
def listar_auditoria(db: Session = Depends(get_db), _: dict = Depends(apenas_rh)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return [
        {
            "usuario": log.user_id,
            "acao": log.action,
            "endpoint": log.endpoint,
            "detalhes": log.detail,
            "quando": log.timestamp.isoformat()
        }
        for log in logs
    ]
"""