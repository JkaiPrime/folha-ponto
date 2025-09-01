# src/schemas.py
from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union, Literal

from pydantic import BaseModel, EmailStr, Field, model_validator
import re

# ====== Roles ======
Role = Literal["funcionario", "gestao", "estagiario"]

# ====== Usuário ======
class UserBase(BaseModel):
    email: EmailStr
    nome: str
    role: Role = "funcionario"
    cargo: Optional[str] = None  # texto livre (fonte de verdade em users)

class UserCreate(UserBase):
    password: str
    # Se 'code' vier, o backend CRIA o Colaborador já vinculado a este user
    code: Optional[str] = Field(
        default=None, min_length=6, max_length=6, pattern=r"^\d{6}$"
    )

class UserResponse(UserBase):
    id: int
    is_active: bool
    locked: bool

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cargo: Optional[str] = None

class PasswordTempRequest(BaseModel):
    nova_senha: str

class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: str

# ====== Colaborador ======
class ColaboradorBase(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    nome: Optional[str] = None

class ColaboradorCreate(ColaboradorBase):
    email_usuario: Optional[EmailStr] = None
    cargo: Optional[str] = None  # será salvo em users.cargo

class ColaboradorUpsert(BaseModel):
    code: Optional[str] = Field(None, min_length=6, max_length=6, pattern=r"^\d{6}$")
    cargo: Optional[str] = None
    nome: Optional[str] = None

class ColaboradorResponse(BaseModel):
    id: int
    nome: str
    code: str

    class Config:
        from_attributes = True

# >>> NOVO: resposta com role (join com users)
class ColaboradorWithRoleResponse(BaseModel):
    id: int
    nome: str
    code: str
    role: Role

    class Config:
        from_attributes = True

# ====== Registro de Ponto ======
class RegistroPontoBase(BaseModel):
    # Pode ser:
    # - int (id do colaborador)
    # - str (code de 6 dígitos)
    # - None (resolve via sessão do usuário logado)
    colaborador_id: Optional[Union[int, str]] = None

    @model_validator(mode="after")
    def _validar_colab(self):
        c = self.colaborador_id
        if c is None:
            return self
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

# ====== Tokens ======
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

# ====== Justificativas ======
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

    class Config:
        from_attributes = True

class RegistroComColaboradorResponse(BaseModel):
    id: Optional[int]
    data: date
    entrada: Optional[datetime] = None
    saida_almoco: Optional[datetime] = None
    volta_almoco: Optional[datetime] = None
    saida: Optional[datetime] = None
    justificativa: Optional[str] = None
    arquivo: Optional[str] = None

    # enriquecido
    colaborador: Optional[ColaboradorResponse] = None
    alterado_por: Optional[UserResponse] = None

    # campos calculados/derivados (se aplicável)
    status: Optional[str] = None
    avaliador: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class RegistroPontoPeriodoCreate(BaseModel):
    code: str
    inicio: date
    fim: date
    # horários no formato HH:MM (opcionais)
    entrada: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    saida_almoco: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    volta_almoco: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    saida: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")

    incluir_sabado: bool = False
    incluir_domingo: bool = False
    pular_feriados: bool = True

    justificativa: Optional[str] = None

    @model_validator(mode="after")
    def _valida_periodo_e_ordem(self):
        if self.inicio > self.fim:
            raise ValueError("Data inicial não pode ser maior que a final.")
        if not any([self.entrada, self.saida_almoco, self.volta_almoco, self.saida]):
            raise ValueError("Informe ao menos um horário (entrada/saída etc.).")

        # valida ordem se todos os envolvidos estiverem presentes
        def _to_min(hhmm: Optional[str]) -> Optional[int]:
            if not hhmm:
                return None
            h, m = hhmm.split(":")
            return int(h) * 60 + int(m)

        t0 = _to_min(self.entrada)
        t1 = _to_min(self.saida_almoco)
        t2 = _to_min(self.volta_almoco)
        t3 = _to_min(self.saida)

        def ok(a, b): return (a is None or b is None or a <= b)
        if not (ok(t0, t1) and ok(t1, t2) and ok(t2, t3)):
            raise ValueError("A ordem dos horários está inconsistente (entrada ≤ saída almoço ≤ volta almoço ≤ saída).")
        return self

class BulkInsertItem(BaseModel):
    data: date
    inserted: bool
    reason: Optional[str] = None  # motivo de ter pulado ou erro

class BulkInsertResponse(BaseModel):
    total: int
    sucesso: int
    pulados: int
    itens: List[BulkInsertItem]
