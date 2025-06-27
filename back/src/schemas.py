from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional

# — Colaborador: código de 6 dígitos numéricos —
class ColaboradorBase(BaseModel):
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )
    nome: Optional[str] = None

class ColaboradorCreate(ColaboradorBase):
    pass

class ColaboradorResponse(ColaboradorBase):
    id: int
    class Config:
        orm_mode = True

# — Registro de Ponto —
class RegistroPontoBase(BaseModel):
    colaborador_id: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )

class RegistroPontoCreate(RegistroPontoBase):
    pass

class RegistroPontoUpdate(BaseModel):
    entrada: Optional[datetime] = None
    saida_almoco: Optional[datetime] = None
    volta_almoco: Optional[datetime] = None
    saida: Optional[datetime] = None

class RegistroPontoResponse(RegistroPontoBase):
    id: int
    data: date
    entrada: Optional[datetime] = None
    saida_almoco: Optional[datetime] = None
    volta_almoco: Optional[datetime] = None
    saida: Optional[datetime] = None
    class Config:
        orm_mode = True

# — Auth / User (RH) —
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: EmailStr
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
