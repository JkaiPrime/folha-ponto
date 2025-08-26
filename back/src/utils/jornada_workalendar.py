from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional, Tuple

try:
    from workalendar.america import Brazil
except Exception:  # pragma: no cover
    Brazil = None


# ========= Helpers de calendário =========
def is_holiday(d: date) -> bool:
    """Retorna True se for feriado (segundo workalendar)."""
    if Brazil is None:
        # Sem a lib, não conseguimos identificar; por segurança, consideramos que NÃO é feriado
        return False
    cal = Brazil()
    return not cal.is_working_day(d) and (d.weekday() < 5)


# ========= Regras =========
def validar_dia(agora: datetime) -> tuple[bool, Optional[str]]:
    """
    Permite batida em qualquer horário,
    mas bloqueia se for sábado, domingo ou feriado.
    """
    hoje = agora.date()

    # Bloqueio final de semana
    if hoje.weekday() >= 5:  # 5 = sábado, 6 = domingo
        return False, "Ponto não permitido em finais de semana."

    # Bloqueio feriado
    if is_holiday(hoje):
        return False, "Ponto não permitido em feriados."

    return True, None


def validar_batida(agora: datetime, batidas_hoje: int) -> tuple[bool, Optional[str]]:
    """
    Regras combinadas:
      1) Permite qualquer batida (1ª, 2ª, 3ª, 4ª...) em QUALQUER horário;
      2) Bloqueia finais de semana;
      3) Bloqueia feriados.
    """
    return validar_dia(agora)


# ====== Mantidos apenas por compatibilidade de import (não usados) ======
def is_business_day(d: date) -> bool:  # pragma: no cover
    """Compat: antes considerávamos seg–sex; agora só bloqueamos fds/feriado."""
    return d.weekday() < 5 and not is_holiday(d)

FIRST_WINDOW_1: Tuple[time, time] = (time(0, 0), time(23, 59, 59))
FIRST_WINDOW_2: Tuple[time, time] = (time(0, 0), time(0, 59))
FREE_UNTIL: time = time(23, 59, 59)
