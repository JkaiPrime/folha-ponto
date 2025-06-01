from sqlalchemy import Column, Date, DateTime, Integer, String, UniqueConstraint


from .database import Base


class RegistroPonto(Base):
    __tablename__ = "registro_ponto"
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(String(6), index=True)
    data = Column(Date, index=True)

    entrada = Column(DateTime, nullable=True)
    saida_almoco = Column(DateTime, nullable=True)
    volta_almoco = Column(DateTime, nullable=True)
    saida = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("colaborador_id", "data", name="_colab_data_uc"),
    )
