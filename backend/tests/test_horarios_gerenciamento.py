"""Tarefa 20 — gerenciamento de horários pelo dono (HU04, CT12). Visão pública: tarefa 52."""

from datetime import datetime, time, timedelta
from decimal import Decimal

import pytest

from app.core.tempo import hoje_local
from app.models import HorarioQuadra, PapelUsuario, Reserva, StatusHorario
from app.services import horario_service


def _proxima_segunda(semanas: int = 1):
    hoje = hoje_local()
    return hoje + timedelta(days=(7 - hoje.weekday()) + 7 * (semanas - 1))


SEG = _proxima_segunda()  # sempre no futuro
TER, QUA, DOM = SEG + timedelta(days=1), SEG + timedelta(days=2), SEG + timedelta(days=6)


@pytest.fixture
def cenario(login, nova_quadra):
    dono, headers = login()
    quadra = nova_quadra(dono, preco_hora=80)
    return quadra, headers


def _url(quadra, *partes):
    return "/".join([f"/api/quadras/{quadra.id}/horarios", *map(str, partes)])


def _gerar(client, quadra, headers, **campos):
    corpo = {
        "data_inicio": SEG.isoformat(),
        "data_fim": SEG.isoformat(),
        "hora_abertura": "08:00",
        "hora_fechamento": "11:00",
    }
    corpo.update(campos)
    return client.post(_url(quadra), json=corpo, headers=headers)


def _horario(db, quadra, dia=SEG, inicio=10, status=StatusHorario.DISPONIVEL, **campos):
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


def _erros(resp):
    assert resp.status_code == 422, resp.text
    return {e["campo"]: e["mensagem"] for e in resp.json()["erros"]}


# --- POST /quadras/{id}/horarios ---------------------------------------------------------


def test_gera_horarios_de_uma_hora(client, cenario):
    quadra, headers = cenario
    resp = _gerar(client, quadra, headers, data_fim=TER.isoformat())
    assert resp.status_code == 201, resp.text
    corpo = resp.json()
    assert corpo["ignorados"] == []
    assert [(h["data"], h["hora_inicio"], h["hora_fim"]) for h in corpo["criados"]] == [
        (d.isoformat(), f"{i:02d}:00", f"{i + 1:02d}:00") for d in (SEG, TER) for i in (8, 9, 10)
    ]
    primeiro = corpo["criados"][0]
    assert primeiro["status"] == "disponivel"
    assert primeiro["preco"] is None
    assert primeiro["preco_efetivo"] == 80.0
    assert primeiro["quadra_id"] == quadra.id


def test_gera_so_nos_dias_da_semana_escolhidos(client, cenario):
    quadra, headers = cenario
    resp = _gerar(
        client,
        quadra,
        headers,
        data_fim=DOM.isoformat(),
        dias_semana=[3, 1, 1],
        hora_abertura="18:00",
        hora_fechamento="19:00",
    )
    assert resp.status_code == 201
    assert [h["data"] for h in resp.json()["criados"]] == [SEG.isoformat(), QUA.isoformat()]


def test_preco_proprio_do_horario(client, cenario):
    quadra, headers = cenario
    resp = _gerar(client, quadra, headers, preco="120.50", hora_fechamento="09:00")
    h = resp.json()["criados"][0]
    assert h["preco"] == 120.5 and h["preco_efetivo"] == 120.5


def test_sobra_menor_que_uma_hora_e_descartada(client, cenario):
    quadra, headers = cenario
    resp = _gerar(client, quadra, headers, hora_abertura="08:00", hora_fechamento="10:45")
    assert [h["hora_inicio"] for h in resp.json()["criados"]] == ["08:00", "09:00"]


def test_aceita_hora_com_segundos_e_minutos_quebrados(client, cenario):
    quadra, headers = cenario
    resp = _gerar(client, quadra, headers, hora_abertura="07:30:59", hora_fechamento="09:30")
    assert [(h["hora_inicio"], h["hora_fim"]) for h in resp.json()["criados"]] == [
        ("07:30", "08:30"),
        ("08:30", "09:30"),
    ]


def test_repetir_a_geracao_nao_duplica(client, cenario):
    quadra, headers = cenario
    _gerar(client, quadra, headers)
    resp = _gerar(client, quadra, headers, hora_fechamento="12:00")
    assert resp.status_code == 201
    corpo = resp.json()
    assert [h["hora_inicio"] for h in corpo["criados"]] == ["11:00"]
    assert [i["code"] for i in corpo["ignorados"]] == ["HORARIO_JA_CADASTRADO"] * 3
    assert corpo["ignorados"][0]["motivo"] == "Já existe um horário com este início."


def test_nao_cria_horario_sobreposto(client, db, cenario):
    """RNF01 / D3: 10:30–11:30 existente bloqueia 10:00–11:00 e 11:00–12:00."""
    quadra, headers = cenario
    db.add(
        HorarioQuadra(
            quadra_id=quadra.id, data=SEG, hora_inicio=time(10, 30), hora_fim=time(11, 30)
        )
    )
    db.commit()
    resp = _gerar(client, quadra, headers, hora_abertura="09:00", hora_fechamento="12:00")
    corpo = resp.json()
    assert [h["hora_inicio"] for h in corpo["criados"]] == ["09:00"]
    assert [(i["hora_inicio"], i["code"]) for i in corpo["ignorados"]] == [
        ("10:00", "HORARIO_SOBREPOSTO"),
        ("11:00", "HORARIO_SOBREPOSTO"),
    ]
    assert corpo["ignorados"][0]["motivo"] == "Sobrepõe o horário 10:30–11:30."


def test_horarios_de_hoje_que_ja_passaram_sao_ignorados(client, cenario, monkeypatch):
    quadra, headers = cenario
    hoje = hoje_local()
    monkeypatch.setattr(horario_service, "agora_local", lambda: datetime.combine(hoje, time(12, 0)))
    resp = _gerar(
        client,
        quadra,
        headers,
        data_inicio=hoje.isoformat(),
        data_fim=hoje.isoformat(),
        hora_abertura="10:00",
        hora_fechamento="14:00",
    )
    corpo = resp.json()
    assert [h["hora_inicio"] for h in corpo["criados"]] == ["13:00"]
    assert [i["code"] for i in corpo["ignorados"]] == ["HORARIO_PASSADO"] * 3


def test_periodo_sem_nenhuma_data_nos_dias_escolhidos(client, cenario):
    quadra, headers = cenario
    resp = _gerar(client, quadra, headers, dias_semana=[2])  # só a segunda no período
    assert resp.status_code == 422
    assert resp.json()["code"] == "PERIODO_SEM_DATAS"


@pytest.mark.parametrize(
    ("campos", "campo"),
    [
        ({"data_inicio": (hoje_local() - timedelta(days=1)).isoformat()}, "data_inicio"),
        ({"data_fim": (SEG - timedelta(days=1)).isoformat()}, "data_fim"),
        ({"data_fim": (SEG + timedelta(days=92)).isoformat()}, "data_fim"),
        ({"hora_abertura": "10:00", "hora_fechamento": "10:30"}, "hora_fechamento"),
        ({"hora_abertura": "10:00", "hora_fechamento": "09:00"}, "hora_fechamento"),
        ({"hora_abertura": "25:00"}, "hora_abertura"),
        ({"dias_semana": [0]}, "dias_semana.0"),
        ({"dias_semana": [8]}, "dias_semana.0"),
        ({"dias_semana": []}, "dias_semana"),
        ({"preco": 0}, "preco"),
        ({"status": "bloqueado"}, "status"),
    ],
)
def test_validacoes_da_geracao(client, cenario, campos, campo):
    quadra, headers = cenario
    assert campo in _erros(_gerar(client, quadra, headers, **campos))


def test_mensagens_das_validacoes_de_periodo(client, cenario):
    quadra, headers = cenario
    erros = _erros(_gerar(client, quadra, headers, data_fim=(SEG + timedelta(days=92)).isoformat()))
    assert erros["data_fim"] == "O período pode ter no máximo 92 dias."
    erros = _erros(_gerar(client, quadra, headers, hora_fechamento="08:30"))
    assert erros["hora_fechamento"] == "Deve ser pelo menos 60 minutos depois da abertura."


def test_permissoes_da_geracao(client, login, cenario):
    quadra, _ = cenario
    _, outro = login("outro@muzzi.test")
    _, admin = login("admin@muzzi.test", papel=PapelUsuario.ADMINISTRADOR)

    assert _gerar(client, quadra, {}).status_code == 401
    assert _gerar(client, quadra, outro).json()["code"] == "ACESSO_NEGADO"
    assert _gerar(client, quadra, admin).status_code == 201


def test_quadra_inexistente(client, login):
    _, headers = login()
    resp = client.get("/api/quadras/999/horarios", headers=headers)
    assert resp.status_code == 404
    assert resp.json()["code"] == "QUADRA_NAO_ENCONTRADA"


# --- GET /quadras/{id}/horarios ----------------------------------------------------------


def test_lista_todos_os_status_ordenados(client, db, cenario):
    quadra, headers = cenario
    _horario(db, quadra, dia=TER, inicio=9)
    _horario(db, quadra, dia=SEG, inicio=15, status=StatusHorario.BLOQUEADO)
    _horario(db, quadra, dia=SEG, inicio=8, status=StatusHorario.RESERVADO)

    resp = client.get(_url(quadra), headers=headers, params={"data_inicio": SEG, "data_fim": TER})
    assert resp.status_code == 200
    assert [(h["data"], h["hora_inicio"], h["status"]) for h in resp.json()] == [
        (SEG.isoformat(), "08:00", "reservado"),
        (SEG.isoformat(), "15:00", "bloqueado"),
        (TER.isoformat(), "09:00", "disponivel"),
    ]

    so_bloqueados = client.get(
        _url(quadra),
        headers=headers,
        params={"data_inicio": SEG, "data_fim": TER, "status": "bloqueado"},
    )
    assert [h["hora_inicio"] for h in so_bloqueados.json()] == ["15:00"]


def test_lista_padrao_e_de_hoje_a_seis_dias(client, db, cenario):
    quadra, headers = cenario
    hoje = hoje_local()
    _horario(db, quadra, dia=hoje + timedelta(days=6), inicio=20)
    _horario(db, quadra, dia=hoje + timedelta(days=7), inicio=20)
    assert [h["data"] for h in client.get(_url(quadra), headers=headers).json()] == [
        (hoje + timedelta(days=6)).isoformat()
    ]


@pytest.mark.parametrize(
    "params",
    [
        {"data_inicio": TER.isoformat(), "data_fim": SEG.isoformat()},
        {"data_inicio": SEG.isoformat(), "data_fim": (SEG + timedelta(days=92)).isoformat()},
    ],
)
def test_lista_periodo_invalido(client, cenario, params):
    quadra, headers = cenario
    resp = client.get(_url(quadra), headers=headers, params=params)
    assert resp.status_code == 422
    assert resp.json()["code"] == "PERIODO_INVALIDO"


# --- PATCH /quadras/{id}/horarios/{horario_id} -------------------------------------------


def test_bloquear_e_desbloquear(client, db, cenario):
    quadra, headers = cenario
    h = _horario(db, quadra)
    resp = client.patch(_url(quadra, h.id), json={"status": "bloqueado"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "bloqueado"
    resp = client.patch(_url(quadra, h.id), json={"status": "disponivel"}, headers=headers)
    assert resp.json()["status"] == "disponivel"


def test_mudar_e_zerar_preco(client, db, cenario):
    quadra, headers = cenario
    h = _horario(db, quadra)
    resp = client.patch(_url(quadra, h.id), json={"preco": 99.9}, headers=headers)
    assert resp.json()["preco"] == 99.9 and resp.json()["preco_efetivo"] == 99.9
    assert resp.json()["status"] == "disponivel"  # não mexe no que não foi enviado

    resp = client.patch(_url(quadra, h.id), json={"preco": None}, headers=headers)
    assert resp.json()["preco"] is None and resp.json()["preco_efetivo"] == 80.0


def test_horario_reservado_nao_pode_ser_alterado(client, db, cenario):
    """CT12: atualizar horários preserva as reservas já feitas."""
    quadra, headers = cenario
    h = _horario(db, quadra, status=StatusHorario.RESERVADO)
    resp = client.patch(_url(quadra, h.id), json={"status": "bloqueado"}, headers=headers)
    assert resp.status_code == 409
    assert resp.json()["code"] == "HORARIO_RESERVADO"
    db.refresh(h)
    assert h.status == StatusHorario.RESERVADO


def test_horario_que_ja_passou_nao_pode_ser_alterado(client, db, cenario):
    quadra, headers = cenario
    h = _horario(db, quadra, dia=hoje_local() - timedelta(days=1))
    resp = client.patch(_url(quadra, h.id), json={"status": "bloqueado"}, headers=headers)
    assert resp.status_code == 409
    assert resp.json()["code"] == "HORARIO_PASSADO"


@pytest.mark.parametrize(
    ("corpo", "campo"),
    [
        ({}, "corpo"),
        ({"status": "reservado"}, "status"),
        ({"status": None}, "status"),
        ({"preco": -1}, "preco"),
        ({"data": "2030-01-01"}, "data"),
    ],
)
def test_validacoes_da_atualizacao(client, db, cenario, corpo, campo):
    quadra, headers = cenario
    h = _horario(db, quadra)
    assert campo in _erros(client.patch(_url(quadra, h.id), json=corpo, headers=headers))


def test_status_do_patch_e_enum_no_openapi(client):
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert schemas["HorarioAtualizar"]["properties"]["status"] == {
        "$ref": "#/components/schemas/StatusHorarioAlteravel"
    }
    assert schemas["StatusHorarioAlteravel"]["enum"] == ["disponivel", "bloqueado"]


def test_status_invalido_lista_as_opcoes(client, db, cenario):
    quadra, headers = cenario
    h = _horario(db, quadra)
    resp = client.patch(_url(quadra, h.id), json={"status": "reservado"}, headers=headers)
    mensagem = resp.json()["erros"][0]["mensagem"]
    assert "disponivel" in mensagem and "bloqueado" in mensagem


def test_horario_de_outra_quadra_da_404(client, db, cenario, nova_quadra, criar_usuario):
    quadra, headers = cenario
    outra = nova_quadra(criar_usuario(email="x@muzzi.test"))
    h = _horario(db, outra)
    resp = client.patch(_url(quadra, h.id), json={"status": "bloqueado"}, headers=headers)
    assert resp.status_code == 404
    assert resp.json()["code"] == "HORARIO_NAO_ENCONTRADO"


# --- DELETE /quadras/{id}/horarios/{horario_id} ------------------------------------------


def test_remover_horario_livre(client, db, cenario):
    quadra, headers = cenario
    h = _horario(db, quadra)
    horario_id = h.id
    assert client.delete(_url(quadra, horario_id), headers=headers).status_code == 204
    db.expire_all()
    assert db.get(HorarioQuadra, horario_id) is None


def test_nao_remove_horario_reservado(client, db, cenario):
    quadra, headers = cenario
    h = _horario(db, quadra, status=StatusHorario.RESERVADO)
    resp = client.delete(_url(quadra, h.id), headers=headers)
    assert resp.status_code == 409 and resp.json()["code"] == "HORARIO_RESERVADO"


def test_nao_remove_horario_com_historico_de_reservas(client, db, cenario, criar_usuario):
    quadra, headers = cenario
    h = _horario(db, quadra)  # reserva cancelada: o horário voltou a ficar disponível
    cliente = criar_usuario(email="cliente@muzzi.test", senha=None, papel=PapelUsuario.CLIENTE)
    db.add(
        Reserva(
            codigo="MZ-H1",
            cliente_id=cliente.id,
            quadra_id=quadra.id,
            horario_id=h.id,
            quantidade_jogadores=2,
            valor_total=Decimal("80.00"),
            status="cancelada",
        )
    )
    db.commit()
    resp = client.delete(_url(quadra, h.id), headers=headers)
    assert resp.status_code == 409
    assert resp.json()["code"] == "HORARIO_COM_HISTORICO"


def test_remover_exige_dono(client, db, login, cenario):
    quadra, _ = cenario
    _, outro = login("outro@muzzi.test")
    h = _horario(db, quadra)
    assert client.delete(_url(quadra, h.id), headers=outro).status_code == 403
