from datetime import datetime
from pytz import timezone

def now_sp():
    return datetime.now(timezone('America/Sao_Paulo'))
