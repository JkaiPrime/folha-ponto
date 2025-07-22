from sqlalchemy import (
    Column, Date, DateTime, Integer, String,
    Boolean, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nome = Column(String, nullable=False)  # <-- NOVO
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    failed_attempts = Column(Integer, default=0, nullable=False)
    locked = Column(Boolean, default=False, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    role = Column(String, default="funcionario", nullable=False)

class Colaborador(Base):
    __tablename__ = "colaboradores"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, index=True, nullable=False)
    nome = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    usuario = relationship("User")
    registros = relationship("RegistroPonto", back_populates="colaborador")

class RegistroPonto(Base):
    __tablename__ = "registro_ponto"
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(String(6), ForeignKey("colaboradores.code"), index=True)
    data = Column(Date, index=True)
    entrada = Column(DateTime, nullable=True)
    saida_almoco = Column(DateTime, nullable=True)
    volta_almoco = Column(DateTime, nullable=True)
    saida = Column(DateTime, nullable=True)

    colaborador = relationship("Colaborador", back_populates="registros")

    __table_args__ = (
        UniqueConstraint("colaborador_id", "data", name="_colab_data_uc"),
    )



class Justificativa(Base):
    __tablename__ = "justificativas"
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(String(6), ForeignKey("colaboradores.code"), index=True)
    justificativa = Column(String, nullable=False)
    arquivo = Column(String, nullable=True)
    data_envio = Column(DateTime, default=datetime.utcnow)
    data_referente = Column(Date, nullable=False)
    colaborador = relationship("Colaborador", backref="justificativas")





class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)