from datetime import datetime
import pytz

def get_hora_brasilia():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz)
