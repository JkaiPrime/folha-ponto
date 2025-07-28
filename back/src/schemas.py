from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum



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
        from_attributes = True
        

class UserBase(BaseModel):
    email: EmailStr
    nome: str
    role: str = "funcionario"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    locked: bool
    class Config:
        from_attributes = True


       
class RegistroComColaboradorResponse(BaseModel):
    id: Optional[int]
    data: date
    entrada: Optional[datetime]
    saida_almoco: Optional[datetime]
    volta_almoco: Optional[datetime]
    saida: Optional[datetime]
    justificativa: Optional[str] = None
    arquivo: Optional[str] = None
    colaborador: Optional[ColaboradorResponse] = None
    alterado_por: Optional[UserResponse] = None

    # 🔽 Campos adicionais
    status: Optional[str] = None
    avaliador: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class ColaboradorCreate(ColaboradorBase):
    email_usuario: Optional[EmailStr] = None




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

class RegistroPontoResponse(BaseModel):
    id: Optional[int]
    data: date
    entrada: Optional[datetime]
    saida_almoco: Optional[datetime]
    volta_almoco: Optional[datetime]
    saida: Optional[datetime]
    justificativa: Optional[str] = None
    arquivo: Optional[str] = None
    colaborador: Optional[ColaboradorResponse] = None
    alterado_por: Optional[UserResponse] = None  # <-- Adicionado aqui

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# — Justificativas —
class JustificativaCreate(BaseModel):
    colaborador_id: int
    justificativa: str
    data_referente: date
    arquivo: Optional[str] = None

class StatusJustificativa(str, Enum):
    pendente = "pendente"
    aprovada = "aprovada"
    rejeitada = "rejeitada"

class AvaliacaoJustificativa(BaseModel):
    status: StatusJustificativa
    comentario: Optional[str] = None

class JustificativaResponse(BaseModel):
    id: int
    colaborador_id: int
    justificativa: str
    arquivo: Optional[str]
    data_envio: datetime
    data_referente: date
    status: str
    avaliado_em: Optional[datetime]
    avaliador: Optional[UserResponse]

    class Config:
        from_attributes = True



class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenRefresh(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str