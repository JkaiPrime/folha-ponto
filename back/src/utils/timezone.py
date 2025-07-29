from datetime import datetime
from pytz import timezone
import pytz
def now_sp():
    return datetime.now(timezone('America/Sao_Paulo'))


def get_hora_brasilia():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz)
