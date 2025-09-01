from sqlalchemy import (
    Column, Date, DateTime, Integer, String,
    Boolean, ForeignKey, Text, func
)
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from sqlalchemy.orm import declared_attr


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    nome = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    # Garantir defaults também no servidor para consistência (evita NULL inesperado)
    is_active = Column(Boolean, default=True, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    locked = Column(Boolean, default=False, nullable=False)
    locked_until = Column(Date, nullable=True)
    role = Column(String, nullable=False)      # 'funcionario' | 'gestao' | 'estagiario'

    # cargo deve NUNCA ser NULL (para não quebrar se a coluna for NOT NULL no DB)
    # mesmo que sua migration atual esteja nullable=True, essas defaults blindam o ORM.
    cargo = Column(String, nullable=False, default="Não Definido")

    colaborador = relationship("Colaborador", back_populates="user", uselist=False)


class Colaborador(Base):
    __tablename__ = "colaboradores"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    nome = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="colaborador")
    pontos = relationship("RegistroPonto", back_populates="colaborador")


class RegistroPonto(Base):
    __tablename__ = "registro_ponto"

    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(Integer, ForeignKey("colaboradores.id"))
    data = Column(Date, nullable=False)
    entrada = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    saida_almoco = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    volta_almoco = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    saida = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    justificativa = Column(String, nullable=True)
    arquivo = Column(String, nullable=True)
    alterado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    colaborador = relationship("Colaborador", back_populates="pontos")
    alterado_por = relationship("User", foreign_keys=[alterado_por_id])

    @declared_attr
    def status(self):  # mapeado via orm no response, se necessário
        pass

    @declared_attr
    def avaliador(self):
        pass


class Justificativa(Base):
    __tablename__ = "justificativas"

    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(Integer, ForeignKey("colaboradores.id"), index=True)
    justificativa = Column(String, nullable=False)
    arquivo = Column(String, nullable=True)
    data_envio = Column(DateTime, default=datetime.utcnow)
    data_referente = Column(Date, nullable=False)

    colaborador = relationship("Colaborador", backref="justificativas")
    status = Column(String, default="pendente")
    avaliador_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    avaliado_em = Column(DateTime, nullable=True)

    avaliador = relationship("User", foreign_keys=[avaliador_id])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
