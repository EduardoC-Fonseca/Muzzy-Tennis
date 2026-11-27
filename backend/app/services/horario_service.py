"""Horários das quadras: gerenciamento pelo dono (tarefa 20 — HU04, CT12) e disponibilidade
para o cliente com validação de conflitos (tarefa 52 — CT02, RNF01).

Os horários são datas/horas locais (``app.core.tempo``). Cada horário dura
``DURACAO_SLOT_MINUTOS`` e não pode se sobrepor a outro da mesma quadra (RNF01, decisão D3).
Horários reservados nunca são alterados nem removidos por aqui (CT12).
"""

from collections import defaultdict
from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, exists, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.exceptions import ConflitoError, NaoEncontradoError, RegraNegocioError
from app.core.tempo import agora_local, hoje_local
from app.models import HorarioQuadra, Quadra, Reserva, StatusHorario
from app.schemas.horario import HorarioAtualizar, HorarioIgnorado, HorariosGerar
from app.services import quadra_service


def _intervalos_do_dia(abertura: time, fechamento: time) -> list[tuple[time, time]]:
    duracao = timedelta(minutes=settings.duracao_slot_minutos)
    base = date(2000, 1, 1)  # só para somar horas
    inicio, limite = datetime.combine(base, abertura), datetime.combine(base, fechamento)
    intervalos = []
    while inicio + duracao <= limite:
        intervalos.append((inicio.time(), (inicio + duracao).time()))
        inicio += duracao
    return intervalos


def _datas(dados: HorariosGerar) -> list[date]:
    dias = set(dados.dias_semana or range(1, 8))
    total = (dados.data_fim - dados.data_inicio).days + 1
    datas = (dados.data_inicio + timedelta(days=i) for i in range(total))
    return [d for d in datas if d.isoweekday() in dias]


def gerar_horarios(
    db: Session, quadra: Quadra, dados: HorariosGerar
) -> tuple[list[HorarioQuadra], list[HorarioIgnorado]]:
    """Cria os horários do período. Os que já existem, se sobrepõem a outro ou já passaram são
    ignorados e voltam com o motivo; os demais são criados."""
    datas = _datas(dados)
    if not datas:
        raise RegraNegocioError(
            "Nenhuma data do período cai nos dias da semana escolhidos.",
            code="PERIODO_SEM_DATAS",
        )

    existentes: dict[date, list[HorarioQuadra]] = defaultdict(list)
    for h in db.scalars(
        select(HorarioQuadra).where(
            HorarioQuadra.quadra_id == quadra.id,
            HorarioQuadra.data.between(dados.data_inicio, dados.data_fim),
        )
    ):
        existentes[h.data].append(h)

    agora = agora_local()
    criados: list[HorarioQuadra] = []
    ignorados: list[HorarioIgnorado] = []
    for dia in datas:
        for inicio, fim in _intervalos_do_dia(dados.hora_abertura, dados.hora_fechamento):

            def ignorar(code: str, motivo: str, dia=dia, inicio=inicio, fim=fim) -> None:
                ignorados.append(
                    HorarioIgnorado(
                        data=dia, hora_inicio=inicio, hora_fim=fim, code=code, motivo=motivo
                    )
                )

            if datetime.combine(dia, inicio) <= agora:
                ignorar("HORARIO_PASSADO", "O horário já passou.")
                continue
            mesmo = next((h for h in existentes[dia] if h.hora_inicio == inicio), None)
            if mesmo is not None:
                ignorar("HORARIO_JA_CADASTRADO", "Já existe um horário com este início.")
                continue
            conflito = next(
                (h for h in existentes[dia] if h.hora_inicio < fim and inicio < h.hora_fim), None
            )
            if conflito is not None:
                ignorar(
                    "HORARIO_SOBREPOSTO",
                    f"Sobrepõe o horário {conflito.hora_inicio:%H:%M}–{conflito.hora_fim:%H:%M}.",
                )
                continue
            criados.append(
                HorarioQuadra(
                    quadra_id=quadra.id,
                    data=dia,
                    hora_inicio=inicio,
                    hora_fim=fim,
                    preco=dados.preco,
                    status=StatusHorario.DISPONIVEL,
                )
            )

    if criados:
        db.add_all(criados)
        try:
            db.commit()
        except IntegrityError:  # outro pedido criou o mesmo horário ao mesmo tempo
            db.rollback()
            raise ConflitoError(
                "Outro cadastro de horários foi feito ao mesmo tempo. Tente novamente.",
                code="HORARIO_JA_CADASTRADO",
            ) from None
        for h in criados:
            h.quadra = quadra
    return criados, ignorados


def _ainda_nao_comecou(agora: datetime):
    """Filtro SQL: horários que começam depois de ``agora`` (datas e horas locais)."""
    return or_(
        HorarioQuadra.data > agora.date(),
        and_(HorarioQuadra.data == agora.date(), HorarioQuadra.hora_inicio > agora.time()),
    )


def listar_horarios(
    db: Session,
    quadra: Quadra,
    *,
    data_inicio: date | None,
    data_fim: date | None,
    status: StatusHorario | None,
    somente_disponiveis: bool = False,
) -> list[HorarioQuadra]:
    """Horários do período, por data e hora.

    ``somente_disponiveis`` é a visão do cliente (tarefa 52): só horários livres que ainda não
    começaram. Sem ele, a visão do dono: todos os status, inclusive os que já passaram.
    """
    inicio = data_inicio or hoje_local()
    fim = data_fim or inicio + timedelta(days=6)
    if fim < inicio:
        raise RegraNegocioError(
            "A data final deve ser igual ou posterior à inicial.", code="PERIODO_INVALIDO"
        )
    if (fim - inicio).days + 1 > settings.horarios_max_dias_por_operacao:
        raise RegraNegocioError(
            f"O período pode ter no máximo {settings.horarios_max_dias_por_operacao} dias.",
            code="PERIODO_INVALIDO",
        )
    consulta = select(HorarioQuadra).where(
        HorarioQuadra.quadra_id == quadra.id, HorarioQuadra.data.between(inicio, fim)
    )
    if somente_disponiveis:
        consulta = consulta.where(
            HorarioQuadra.status == StatusHorario.DISPONIVEL, _ainda_nao_comecou(agora_local())
        )
    elif status is not None:
        consulta = consulta.where(HorarioQuadra.status == status)
    horarios = db.scalars(
        consulta.options(selectinload(HorarioQuadra.quadra)).order_by(
            HorarioQuadra.data, HorarioQuadra.hora_inicio
        )
    ).all()
    return list(horarios)


def _obter_horario_alteravel(db: Session, quadra: Quadra, horario_id: int) -> HorarioQuadra:
    horario = db.get(HorarioQuadra, horario_id)
    if horario is None or horario.quadra_id != quadra.id:
        raise NaoEncontradoError("Horário não encontrado.", code="HORARIO_NAO_ENCONTRADO")
    if horario.status == StatusHorario.RESERVADO:
        raise ConflitoError(
            "Este horário tem uma reserva e não pode ser alterado nem removido.",
            code="HORARIO_RESERVADO",
        )
    if datetime.combine(horario.data, horario.hora_inicio) <= agora_local():
        raise ConflitoError(
            "Este horário já passou e não pode ser alterado.", code="HORARIO_PASSADO"
        )
    return horario


def atualizar_horario(
    db: Session, quadra: Quadra, horario_id: int, dados: HorarioAtualizar
) -> HorarioQuadra:
    """Bloqueia/desbloqueia o horário ou muda o preço dele (CT12)."""
    horario = _obter_horario_alteravel(db, quadra, horario_id)
    if "status" in dados.model_fields_set:
        horario.status = StatusHorario(dados.status)
    if "preco" in dados.model_fields_set:
        horario.preco = dados.preco
    db.commit()
    return horario


def remover_horario(db: Session, quadra: Quadra, horario_id: int) -> None:
    """Remove um horário livre. Se ele já teve reservas (canceladas ou expiradas), o histórico
    precisa ser mantido: nesse caso, bloqueie o horário em vez de removê-lo."""
    horario = _obter_horario_alteravel(db, quadra, horario_id)
    if db.scalar(select(exists().where(Reserva.horario_id == horario.id))):
        raise ConflitoError(
            "Este horário tem histórico de reservas. Bloqueie-o em vez de removê-lo.",
            code="HORARIO_COM_HISTORICO",
        )
    db.delete(horario)
    db.commit()


def obter_horario_para_reserva(db: Session, quadra_id: int, horario_id: int) -> HorarioQuadra:
    """Valida que o horário pode ser reservado agora e o trava até o fim da transação.

    Usado pela criação da reserva (tarefa 14). O ``SELECT ... FOR UPDATE`` faz pedidos
    simultâneos para o mesmo horário esperarem um pelo outro: o segundo já encontra o horário
    reservado e recebe ``409 HORARIO_INDISPONIVEL`` (CT02, RNF01). Quem chama deve marcar o
    horário como ``reservado`` e fazer o commit na mesma transação.
    """
    horario = db.scalar(
        select(HorarioQuadra).where(HorarioQuadra.id == horario_id).with_for_update()
    )
    if (
        horario is None
        or horario.quadra_id != quadra_id
        or not quadra_service.visivel_ao_publico(horario.quadra)
    ):
        raise NaoEncontradoError("Horário não encontrado.", code="HORARIO_NAO_ENCONTRADO")
    if datetime.combine(horario.data, horario.hora_inicio) <= agora_local():
        raise ConflitoError("Este horário já passou.", code="HORARIO_PASSADO")
    if horario.status != StatusHorario.DISPONIVEL:
        raise ConflitoError(
            "Este horário não está disponível. Escolha outro.", code="HORARIO_INDISPONIVEL"
        )
    return horario
