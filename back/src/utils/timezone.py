from datetime import datetime, timedelta, timezone
from pytz import timezone

def now_sp():
    return datetime.now(timezone('America/Sao_Paulo'))



def get_hora_brasilia():
    return datetime.now(timezone.utc) - timedelta(hours=3)

