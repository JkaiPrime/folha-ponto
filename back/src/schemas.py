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

class ColaboradorResponse(BaseModel):
    id: int
    nome: str
    code: str

    class Config:
        orm_mode = True

class ColaboradorCreate(ColaboradorBase):
    pass

class UserBase(BaseModel):
    email: EmailStr
    nome: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


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
    colaborador: Optional[ColaboradorResponse] = None  # ADICIONADO

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
