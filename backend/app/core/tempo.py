"""Data e hora locais da plataforma.

Os horários das quadras (``horarios_quadra.data``/``hora_inicio``) são datas e horas **locais**
de João Monlevade, sem fuso, como o dono as cadastra. Já os registros de auditoria
(``criado_em``, ``expira_em``...) ficam em UTC (``app.db.base.utcnow``). Use estas funções para
comparar algo com um horário de quadra.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.core.config import settings


def agora_local() -> datetime:
    """Agora no fuso configurado (``FUSO_HORARIO``), sem tzinfo, comparável aos horários."""
    return datetime.now(ZoneInfo(settings.fuso_horario)).replace(tzinfo=None)


def hoje_local() -> date:
    return agora_local().date()
