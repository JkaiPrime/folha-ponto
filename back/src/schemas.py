from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import date, datetime
from typing import Optional, Union
from enum import Enum
import re

# — Colaborador: código de 6 dígitos numéricos —
class ColaboradorBase(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
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

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordTempRequest(BaseModel):
    nova_senha: str

class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: str


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

    status: Optional[str] = None
    avaliador: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class ColaboradorCreate(ColaboradorBase):
    email_usuario: Optional[EmailStr] = None


# — Registro de Ponto —
# Agora aceita:
# - int (id do colaborador),
# - str (code de 6 dígitos),
# - None (usa usuário logado para resolver).
class RegistroPontoBase(BaseModel):
    colaborador_id: Optional[Union[int, str]] = None

    @model_validator(mode="after")
    def _validar_colab(self):
        c = self.colaborador_id
        if c is None:
            return self  # OK: será resolvido pela sessão
        if isinstance(c, int):
            if c <= 0:
                raise ValueError("colaborador_id (int) deve ser positivo.")
            return self
        # string -> precisa ser code de 6 dígitos
        if not re.fullmatch(r"^\d{6}$", c):
            raise ValueError("colaborador_id (str) deve ser um code de 6 dígitos.")
        return self

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
    alterado_por: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class RegistroPontoManualCreate(BaseModel):
    code: str
    data: date
    entrada: Optional[datetime] = None
    saida_almoco: Optional[datetime] = None
    volta_almoco: Optional[datetime] = None
    saida: Optional[datetime] = None
    justificativa: Optional[str] = None

    @model_validator(mode="after")
    def _validar_horarios(self):
        if not any([self.entrada, self.saida_almoco, self.volta_almoco, self.saida]):
            raise ValueError(
                "Informe pelo menos um horário (entrada, saída almoço, volta almoço ou saída)."
            )

        def ok(a: Optional[datetime], b: Optional[datetime]) -> bool:
            return a is None or b is None or a <= b

        if not (
            ok(self.entrada, self.saida_almoco)
            and ok(self.saida_almoco, self.volta_almoco)
            and ok(self.volta_almoco, self.saida)
        ):
            raise ValueError(
                "A ordem dos horários está inconsistente: "
                "entrada ≤ saída almoço ≤ volta almoço ≤ saída."
            )
        return self


# — tokens —
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenRefresh(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


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
