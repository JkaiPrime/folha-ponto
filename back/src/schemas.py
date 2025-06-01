from pydantic import BaseModel, StringConstraints
from datetime import date, datetime
from typing import Optional
from typing_extensions import Annotated

ColaboradorID = Annotated[str, StringConstraints(min_length=6, max_length=6)]


class RegistroPontoBase(BaseModel):
    colaborador_id: ColaboradorID


class RegistroPontoCreate(RegistroPontoBase):
    pass


class RegistroPontoResponse(RegistroPontoBase):
    data: date
    entrada: Optional[datetime]
    saida_almoco: Optional[datetime]
    volta_almoco: Optional[datetime]
    saida: Optional[datetime]

    class Config:
        orm_mode = True
