from datetime import datetime, timedelta, timezone
from pytz import timezone

def now_sp():
    return datetime.now(timezone('America/Sao_Paulo'))



def get_hora_brasilia():
    tz_brasilia = timezone(timedelta(hours=-3))
    return datetime.now(tz=tz_brasilia)

