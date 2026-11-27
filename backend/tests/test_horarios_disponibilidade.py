"""Tarefa 52 — disponibilidade pública dos horários e validação de conflitos (CT02, RNF01)."""

from datetime import datetime, time, timedelta

import pytest

from app.core.exceptions import ConflitoError, NaoEncontradoError
from app.core.tempo import hoje_local
from app.models import HorarioQuadra, PapelUsuario, StatusHorario
from app.services import horario_service

AMANHA = hoje_local() + timedelta(days=1)


@pytest.fixture
def cenario(login, nova_quadra):
    dono, headers = login()
    quadra = nova_quadra(dono, preco_hora=80)
    return quadra, headers


@pytest.fixture
def agora_meio_dia(monkeypatch):
    """Congela o relógio local em hoje, 12:00."""
    agora = datetime.combine(hoje_local(), time(12))
    monkeypatch.setattr(horario_service, "agora_local", lambda: agora)
    return agora


def _url(quadra, *partes):
    return "/".join([f"/api/quadras/{quadra.id}/horarios", *map(str, partes)])


def _horario(db, quadra, dia=AMANHA, inicio=10, status=StatusHorario.DISPONIVEL, **campos):
    h = HorarioQuadra(
        quadra_id=quadra.id,
        data=dia,
        hora_inicio=time(inicio),
        hora_fim=time(inicio + 1),
        status=status,
        **campos,
    )
    db.add(h)
    db.commit()
    return h


def _inicios(resp):
    assert resp.status_code == 200, resp.text
    return [(h["data"], h["hora_inicio"]) for h in resp.json()]


# --- GET /quadras/{id}/horarios: visão pública ---------------------------------------------


def test_publico_ve_so_os_disponiveis_sem_login(client, db, cenario):
    quadra, _ = cenario
    _horario(db, quadra, inicio=8)
    _horario(db, quadra, inicio=9, status=StatusHorario.RESERVADO)
    _horario(db, quadra, inicio=10, status=StatusHorario.BLOQUEADO)
    _horario(db, quadra, inicio=11, preco=95)

    resp = client.get(_url(quadra))
    assert _inicios(resp) == [(AMANHA.isoformat(), "08:00"), (AMANHA.isoformat(), "11:00")]
    assert all(h["status"] == "disponivel" for h in resp.json())
    assert [h["preco_efetivo"] for h in resp.json()] == [80.0, 95.0]


def test_publico_nao_ve_horarios_que_ja_comecaram(client, db, cenario, agora_meio_dia):
    quadra, _ = cenario
    hoje = hoje_local()
    _horario(db, quadra, dia=hoje, inicio=11)  # 11:00–12:00: já começou
    _horario(db, quadra, dia=hoje, inicio=12)  # começa agora: não dá mais para reservar
    _horario(db, quadra, dia=hoje, inicio=13)
    _horario(db, quadra, dia=hoje - timedelta(days=1), inicio=15)

    resp = client.get(
        _url(quadra),
        params={"data_inicio": (hoje - timedelta(days=1)).isoformat()},
    )
    assert _inicios(resp) == [(hoje.isoformat(), "13:00")]


def test_dono_continua_vendo_tudo(client, db, cenario, agora_meio_dia):
    quadra, headers = cenario
    hoje = hoje_local()
    _horario(db, quadra, dia=hoje, inicio=8)  # passado
    _horario(db, quadra, dia=hoje, inicio=14, status=StatusHorario.RESERVADO)
    _horario(db, quadra, dia=hoje, inicio=15, status=StatusHorario.BLOQUEADO)

    resp = client.get(_url(quadra), headers=headers)
    assert [h["status"] for h in resp.json()] == ["disponivel", "reservado", "bloqueado"]


def test_administrador_ve_tudo(client, db, cenario, login):
    quadra, _ = cenario
    _horario(db, quadra, status=StatusHorario.BLOQUEADO)
    _, admin = login("admin@muzzi.test", papel=PapelUsuario.ADMINISTRADOR)
    assert [h["status"] for h in client.get(_url(quadra), headers=admin).json()] == ["bloqueado"]


def test_outro_dono_logado_tem_a_visao_publica(client, db, cenario, login):
    quadra, _ = cenario
    _horario(db, quadra, inicio=8)
    _horario(db, quadra, inicio=9, status=StatusHorario.BLOQUEADO)
    _, outro = login("outro@muzzi.test")
    assert _inicios(client.get(_url(quadra), headers=outro)) == [(AMANHA.isoformat(), "08:00")]


@pytest.mark.parametrize("status", ["reservado", "bloqueado"])
def test_publico_nao_filtra_status_internos(client, cenario, status):
    quadra, _ = cenario
    resp = client.get(_url(quadra), params={"status": status})
    assert resp.status_code == 403
    assert resp.json()["code"] == "ACESSO_NEGADO"


def test_publico_pode_filtrar_disponivel(client, db, cenario):
    quadra, _ = cenario
    _horario(db, quadra)
    assert len(client.get(_url(quadra), params={"status": "disponivel"}).json()) == 1


def test_dono_filtra_por_status(client, db, cenario):
    quadra, headers = cenario
    _horario(db, quadra, inicio=8)
    _horario(db, quadra, inicio=9, status=StatusHorario.BLOQUEADO)
    resp = client.get(_url(quadra), params={"status": "bloqueado"}, headers=headers)
    assert _inicios(resp) == [(AMANHA.isoformat(), "09:00")]


def test_periodo_padrao_e_de_sete_dias(client, db, cenario):
    quadra, _ = cenario
    hoje = hoje_local()
    _horario(db, quadra, dia=hoje + timedelta(days=6), inicio=20)
    _horario(db, quadra, dia=hoje + timedelta(days=7), inicio=20)
    assert _inicios(client.get(_url(quadra))) == [((hoje + timedelta(days=6)).isoformat(), "20:00")]


def test_periodo_invalido_tambem_vale_para_o_publico(client, cenario):
    quadra, _ = cenario
    resp = client.get(
        _url(quadra),
        params={"data_inicio": AMANHA.isoformat(), "data_fim": hoje_local().isoformat()},
    )
    assert resp.status_code == 422
    assert resp.json()["code"] == "PERIODO_INVALIDO"


def test_quadra_inativa_da_404_para_o_publico(client, db, cenario):
    quadra, headers = cenario
    _horario(db, quadra)
    quadra.ativa = False
    db.commit()
    resp = client.get(_url(quadra))
    assert resp.status_code == 404
    assert resp.json()["code"] == "QUADRA_NAO_ENCONTRADA"
    assert client.get(_url(quadra), headers=headers).status_code == 200  # o dono ainda vê


def test_quadra_de_dono_inativo_da_404_para_o_publico(client, db, nova_quadra, criar_usuario):
    dono = criar_usuario(email="inativo@muzzi.test", status=False)
    quadra = nova_quadra(dono)
    _horario(db, quadra)
    assert client.get(_url(quadra)).status_code == 404


def test_quadra_inexistente_da_404(client):
    resp = client.get("/api/quadras/999/horarios")
    assert resp.status_code == 404
    assert resp.json()["code"] == "QUADRA_NAO_ENCONTRADA"


def test_token_invalido_continua_dando_401(client, cenario):
    quadra, _ = cenario
    resp = client.get(_url(quadra), headers={"Authorization": "Bearer invalido"})
    assert resp.status_code == 401


# --- obter_horario_para_reserva: validação de conflitos usada pela reserva (tarefa 14) -----


def test_horario_livre_pode_ser_reservado(db, cenario):
    quadra, _ = cenario
    h = _horario(db, quadra)
    assert horario_service.obter_horario_para_reserva(db, quadra.id, h.id) is h


@pytest.mark.parametrize("status", [StatusHorario.RESERVADO, StatusHorario.BLOQUEADO])
def test_horario_ocupado_nao_pode_ser_reservado(db, cenario, status):
    """CT02: horário já reservado (ou bloqueado pelo dono) não pode ser reservado de novo."""
    quadra, _ = cenario
    h = _horario(db, quadra, status=status)
    with pytest.raises(ConflitoError) as erro:
        horario_service.obter_horario_para_reserva(db, quadra.id, h.id)
    assert erro.value.code == "HORARIO_INDISPONIVEL"


def test_segunda_reserva_do_mesmo_horario_e_recusada(db, cenario):
    """RNF01: depois que a primeira reserva marca o horário, a segunda recebe conflito."""
    quadra, _ = cenario
    h = _horario(db, quadra)
    primeiro = horario_service.obter_horario_para_reserva(db, quadra.id, h.id)
    primeiro.status = StatusHorario.RESERVADO
    db.commit()
    with pytest.raises(ConflitoError) as erro:
        horario_service.obter_horario_para_reserva(db, quadra.id, h.id)
    assert erro.value.code == "HORARIO_INDISPONIVEL"


def test_horario_que_ja_comecou_nao_pode_ser_reservado(db, cenario, agora_meio_dia):
    quadra, _ = cenario
    h = _horario(db, quadra, dia=hoje_local(), inicio=12)
    with pytest.raises(ConflitoError) as erro:
        horario_service.obter_horario_para_reserva(db, quadra.id, h.id)
    assert erro.value.code == "HORARIO_PASSADO"


def test_horario_de_outra_quadra_nao_e_encontrado(db, cenario, nova_quadra, criar_usuario):
    quadra, _ = cenario
    outra = nova_quadra(criar_usuario(email="x@muzzi.test"))
    h = _horario(db, outra)
    with pytest.raises(NaoEncontradoError) as erro:
        horario_service.obter_horario_para_reserva(db, quadra.id, h.id)
    assert erro.value.code == "HORARIO_NAO_ENCONTRADO"


def test_horario_inexistente_nao_e_encontrado(db, cenario):
    quadra, _ = cenario
    with pytest.raises(NaoEncontradoError):
        horario_service.obter_horario_para_reserva(db, quadra.id, 999)


def test_horario_de_quadra_inativa_nao_pode_ser_reservado(db, cenario):
    quadra, _ = cenario
    h = _horario(db, quadra)
    quadra.ativa = False
    db.commit()
    with pytest.raises(NaoEncontradoError):
        horario_service.obter_horario_para_reserva(db, quadra.id, h.id)
