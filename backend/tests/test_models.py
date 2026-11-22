"""Garante que o esquema reflete o modelo de dados e suas regras de integridade."""

from datetime import date, time
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from app.models import (
    Avaliacao,
    HorarioQuadra,
    PapelUsuario,
    Quadra,
    Reserva,
    StatusHorario,
    StatusReserva,
    TipoPiso,
)

# O MySQL reporta violação de CHECK como OperationalError (3819); o SQLite, como IntegrityError.
VIOLACAO_CHECK = (IntegrityError, OperationalError)


@pytest.fixture
def quadra(db, criar_usuario):
    dono = criar_usuario()
    q = Quadra(
        dono=dono,
        nome="Quadra Central",
        descricao="Quadra de saibro coberta",
        tipo_piso=TipoPiso.SAIBRO,
        coberta=True,
        limite_jogadores=4,
        preco_hora=Decimal("80.00"),
        endereco="Rua A",
        bairro="Centro",
        cidade="João Monlevade",
        estado="MG",
        cep="35930-000",
    )
    db.add(q)
    db.commit()
    return q


def _horario(quadra, inicio=time(10), fim=time(11)):
    return HorarioQuadra(quadra=quadra, data=date(2026, 12, 1), hora_inicio=inicio, hora_fim=fim)


def test_cadeia_completa_de_relacionamentos(db, quadra, criar_usuario):
    cliente = criar_usuario(email="cliente@muzzi.test", senha=None, papel=PapelUsuario.CLIENTE)
    horario = _horario(quadra)
    reserva = Reserva(
        codigo="MZ-0001",
        cliente=cliente,
        quadra=quadra,
        horario=horario,
        quantidade_jogadores=2,
        valor_total=Decimal("80.00"),
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)

    assert reserva.status == StatusReserva.AGUARDANDO_PAGAMENTO
    assert horario.status == StatusHorario.DISPONIVEL
    assert quadra.ativa is True
    assert reserva.criado_em is not None
    assert cliente.senha_hash is None  # decisão D1


def test_horario_duplicado_na_mesma_quadra_e_rejeitado(db, quadra):
    db.add(_horario(quadra))
    db.commit()
    db.add(_horario(quadra))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_horario_com_fim_antes_do_inicio_e_rejeitado(db, quadra):
    db.add(_horario(quadra, inicio=time(11), fim=time(10)))
    with pytest.raises(VIOLACAO_CHECK):
        db.commit()
    db.rollback()


@pytest.mark.parametrize("nota", [0, 6])
def test_nota_fora_de_1_a_5_e_rejeitada(db, quadra, criar_usuario, nota):
    cliente = criar_usuario(email="c@muzzi.test", senha=None, papel=PapelUsuario.CLIENTE)
    reserva = Reserva(
        codigo=f"MZ-N{nota}",
        cliente=cliente,
        quadra=quadra,
        horario=_horario(quadra),
        quantidade_jogadores=2,
        valor_total=Decimal("80.00"),
        status=StatusReserva.CONCLUIDA,
    )
    db.add(Avaliacao(reserva=reserva, quadra=quadra, cliente=cliente, nota=nota))
    with pytest.raises(VIOLACAO_CHECK):
        db.commit()
    db.rollback()


def test_email_unico(db, criar_usuario):
    criar_usuario(email="mesmo@muzzi.test")
    with pytest.raises(IntegrityError):
        criar_usuario(email="mesmo@muzzi.test")
    db.rollback()
