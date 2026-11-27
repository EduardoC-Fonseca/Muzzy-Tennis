"""Horários das quadras: gerenciamento pelo dono (tarefa 20) e disponibilidade pública
(tarefa 52)."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.deps import DbSession, UsuarioAtual, UsuarioOpcional
from app.core.exceptions import AcessoNegadoError
from app.models import StatusHorario
from app.schemas.horario import (
    HorarioAtualizar,
    HorarioPublico,
    HorariosGerados,
    HorariosGerar,
)
from app.services import horario_service, quadra_service

router = APIRouter(prefix="/quadras/{quadra_id}/horarios", tags=["Horários"])


@router.post(
    "",
    response_model=HorariosGerados,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar horários em lote (dono da quadra ou administrador)",
)
def gerar_horarios(
    quadra_id: int, dados: HorariosGerar, db: DbSession, usuario: UsuarioAtual
) -> HorariosGerados:
    """Cria horários de 1 hora para cada data do período, nos dias da semana escolhidos, da
    abertura ao fechamento. Os que já existem, se sobrepõem ou já passaram voltam em
    ``ignorados`` com o motivo; os demais voltam em ``criados``."""
    quadra = quadra_service.obter_quadra_para_gerenciar(db, quadra_id, usuario)
    criados, ignorados = horario_service.gerar_horarios(db, quadra, dados)
    return HorariosGerados(
        criados=[HorarioPublico.model_validate(h) for h in criados], ignorados=ignorados
    )


@router.get(
    "",
    response_model=list[HorarioPublico],
    summary="Listar horários da quadra (disponibilidade pública ou visão do dono)",
)
def listar_horarios(
    quadra_id: int,
    db: DbSession,
    usuario: UsuarioOpcional,
    data_inicio: Annotated[date | None, Query(description="Padrão: hoje")] = None,
    data_fim: Annotated[date | None, Query(description="Padrão: data_inicio + 6 dias")] = None,
    status: Annotated[
        StatusHorario | None,
        Query(description="Só para o dono e o administrador; o público vê só os disponíveis"),
    ] = None,
) -> list[HorarioPublico]:
    """Horários do período, por data e hora.

    - **Público** (sem login, ou logado sem ser dono desta quadra): só horários **disponíveis**
      que ainda não começaram, de quadras ativas. É a disponibilidade para o cliente reservar.
    - **Dono da quadra ou administrador**: todos os status (disponíveis, reservados e
      bloqueados), inclusive os que já passaram, com filtro opcional por ``status``.
    """
    quadra = quadra_service.obter_quadra_visivel(db, quadra_id, usuario)
    gerencia = quadra_service.pode_gerenciar(quadra, usuario)
    if not gerencia and status not in (None, StatusHorario.DISPONIVEL):
        raise AcessoNegadoError("Só o dono da quadra vê horários reservados ou bloqueados.")
    horarios = horario_service.listar_horarios(
        db,
        quadra,
        data_inicio=data_inicio,
        data_fim=data_fim,
        status=status,
        somente_disponiveis=not gerencia,
    )
    return [HorarioPublico.model_validate(h) for h in horarios]


@router.patch(
    "/{horario_id}",
    response_model=HorarioPublico,
    summary="Bloquear, desbloquear ou mudar o preço de um horário",
)
def atualizar_horario(
    quadra_id: int,
    horario_id: int,
    dados: HorarioAtualizar,
    db: DbSession,
    usuario: UsuarioAtual,
) -> HorarioPublico:
    """Horários reservados ou que já passaram não podem ser alterados (CT12)."""
    quadra = quadra_service.obter_quadra_para_gerenciar(db, quadra_id, usuario)
    horario = horario_service.atualizar_horario(db, quadra, horario_id, dados)
    return HorarioPublico.model_validate(horario)


@router.delete(
    "/{horario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover um horário livre",
)
def remover_horario(
    quadra_id: int, horario_id: int, db: DbSession, usuario: UsuarioAtual
) -> Response:
    """Só remove horários livres, futuros e sem histórico de reservas; os demais podem ser
    bloqueados."""
    quadra = quadra_service.obter_quadra_para_gerenciar(db, quadra_id, usuario)
    horario_service.remover_horario(db, quadra, horario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
