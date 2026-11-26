"""Tarefa 13 — consulta de quadras: busca pública, detalhe e quadras do dono."""

import pytest

from app.models import FotoQuadra, PapelUsuario, Quadra, TipoPiso

QUADRAS = "/api/v1/quadras"
MINHAS = "/api/v1/quadras/minhas"
SENHA = "senha-segura-123"


@pytest.fixture
def login(client, criar_usuario):
    """Cria um usuário e devolve (usuario, headers com o token)."""

    def _login(email="dono@muzzi.test", papel=PapelUsuario.DONO_QUADRA, status=True):
        usuario = criar_usuario(email=email, senha=SENHA, papel=papel, status=status)
        token = client.post(
            "/api/v1/auth/login", data={"username": email, "password": SENHA}
        ).json()
        headers = {"Authorization": f"Bearer {token.get('access_token')}"}
        return usuario, headers

    return _login


@pytest.fixture
def nova_quadra(db):
    def _nova(dono, **campos):
        dados = {
            "nome": "Quadra Central",
            "descricao": "Quadra coberta.",
            "tipo_piso": TipoPiso.SAIBRO,
            "coberta": True,
            "limite_jogadores": 4,
            "preco_hora": 80,
            "endereco": "Rua das Flores",
            "bairro": "Centro",
            "cidade": "João Monlevade",
            "estado": "MG",
            "cep": "35930-000",
        }
        dados.update(campos)
        quadra = Quadra(dono_id=dono.id, **dados)
        db.add(quadra)
        db.commit()
        return quadra

    return _nova


@pytest.fixture
def dono(criar_usuario):
    return criar_usuario(email="outro.dono@muzzi.test")


def _nomes(resp):
    assert resp.status_code == 200, resp.text
    return [q["nome"] for q in resp.json()["itens"]]


# --- GET /quadras ----------------------------------------------------------------------


def test_lista_publica_sem_login_e_formato_do_item(client, dono, nova_quadra, db):
    quadra = nova_quadra(dono, preco_hora="95.50")
    db.add_all(
        [
            FotoQuadra(quadra_id=quadra.id, url="/uploads/a.jpg", principal=False, ordem=0),
            FotoQuadra(quadra_id=quadra.id, url="/uploads/b.jpg", principal=True, ordem=1),
        ]
    )
    db.commit()

    resp = client.get(QUADRAS)
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["total"] == 1
    assert corpo["pagina"] == 1 and corpo["por_pagina"] == 20 and corpo["total_paginas"] == 1
    item = corpo["itens"][0]
    assert item == {
        "id": quadra.id,
        "nome": "Quadra Central",
        "tipo_piso": "saibro",
        "coberta": True,
        "limite_jogadores": 4,
        "preco_hora": 95.5,
        "bairro": "Centro",
        "cidade": "João Monlevade",
        "estado": "MG",
        "ativa": True,
        "foto_principal": "/uploads/b.jpg",
    }


def test_lista_sem_foto_devolve_foto_principal_nula(client, dono, nova_quadra):
    nova_quadra(dono)
    assert client.get(QUADRAS).json()["itens"][0]["foto_principal"] is None


def test_lista_ordenada_por_nome(client, dono, nova_quadra):
    for nome in ["Zeta", "Alfa", "Meio"]:
        nova_quadra(dono, nome=nome)
    assert _nomes(client.get(QUADRAS)) == ["Alfa", "Meio", "Zeta"]


def test_lista_esconde_quadra_inativa_e_de_dono_inativo(client, criar_usuario, nova_quadra):
    ativo = criar_usuario(email="ativo@muzzi.test")
    inativo = criar_usuario(email="inativo@muzzi.test", status=False)
    nova_quadra(ativo, nome="Visível")
    nova_quadra(ativo, nome="Desativada", ativa=False)
    nova_quadra(inativo, nome="De dono inativo")
    assert _nomes(client.get(QUADRAS)) == ["Visível"]


@pytest.mark.parametrize(
    ("busca", "esperado"),
    [
        ("Monlevade", ["Monlevade"]),
        ("monlevade", ["Monlevade"]),
        ("  MONLEVADE   joão ", ["Monlevade"]),  # espaços extras são ignorados
        ("João Monlevade", ["Monlevade"]),
        ("monlevade joão", ["Monlevade"]),  # palavras em qualquer ordem
        ("Horizonte", ["BH"]),
        ("Itabira", []),
        ("%", []),  # curingas do LIKE são tratados como texto
        ("", ["BH", "Monlevade"]),
    ],
)
def test_filtro_por_cidade(client, dono, nova_quadra, busca, esperado):
    nova_quadra(dono, nome="Monlevade", cidade="João Monlevade")
    nova_quadra(dono, nome="BH", cidade="Belo Horizonte")
    assert _nomes(client.get(QUADRAS, params={"cidade": busca})) == esperado


@pytest.mark.parametrize("busca", ["joao monlevade", "JOAO", "monlevadé"])
def test_filtro_por_cidade_ignora_acentos_no_mysql(client, dono, nova_quadra, db, busca):
    if db.bind.dialect.name != "mysql":
        pytest.skip("acentos são ignorados pela collation do MySQL (utf8mb4_0900_ai_ci)")
    nova_quadra(dono, nome="Monlevade", cidade="João Monlevade")
    assert _nomes(client.get(QUADRAS, params={"cidade": busca})) == ["Monlevade"]


def test_filtro_por_tipo_de_piso_e_coberta(client, dono, nova_quadra):
    nova_quadra(dono, nome="Saibro coberta", tipo_piso=TipoPiso.SAIBRO, coberta=True)
    nova_quadra(dono, nome="Saibro aberta", tipo_piso=TipoPiso.SAIBRO, coberta=False)
    nova_quadra(dono, nome="Rápida", tipo_piso=TipoPiso.RAPIDA, coberta=True)

    assert _nomes(client.get(QUADRAS, params={"tipo_piso": "saibro"})) == [
        "Saibro aberta",
        "Saibro coberta",
    ]
    assert _nomes(client.get(QUADRAS, params={"tipo_piso": "saibro", "coberta": False})) == [
        "Saibro aberta"
    ]
    assert _nomes(client.get(QUADRAS, params={"coberta": "true"})) == ["Rápida", "Saibro coberta"]


def test_paginacao(client, dono, nova_quadra):
    for i in range(5):
        nova_quadra(dono, nome=f"Quadra {i}")
    resp = client.get(QUADRAS, params={"pagina": 2, "por_pagina": 2})
    corpo = resp.json()
    assert [q["nome"] for q in corpo["itens"]] == ["Quadra 2", "Quadra 3"]
    assert corpo["total"] == 5 and corpo["total_paginas"] == 3

    alem = client.get(QUADRAS, params={"pagina": 9, "por_pagina": 2}).json()
    assert alem["itens"] == [] and alem["total"] == 5


def test_lista_vazia(client):
    corpo = client.get(QUADRAS).json()
    assert corpo == {"itens": [], "total": 0, "pagina": 1, "por_pagina": 20, "total_paginas": 0}


@pytest.mark.parametrize(
    ("params", "campo"),
    [
        ({"tipo_piso": "carpete"}, "tipo_piso"),
        ({"pagina": 0}, "pagina"),
        ({"por_pagina": 101}, "por_pagina"),
        ({"coberta": "talvez"}, "coberta"),
        ({"cidade": "x" * 101}, "cidade"),
    ],
)
def test_parametros_invalidos(client, params, campo):
    resp = client.get(QUADRAS, params=params)
    assert resp.status_code == 422
    assert resp.json()["code"] == "VALIDACAO"
    assert [e["campo"] for e in resp.json()["erros"]] == [campo]


# --- GET /quadras/{id} -------------------------------------------------------------------


def test_detalhe_publico_com_fotos(client, dono, nova_quadra, db):
    quadra = nova_quadra(dono, numero="100")
    db.add(FotoQuadra(quadra_id=quadra.id, url="/uploads/a.jpg", principal=True, ordem=0))
    db.commit()

    resp = client.get(f"{QUADRAS}/{quadra.id}")
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["id"] == quadra.id
    assert corpo["descricao"] == "Quadra coberta."
    assert corpo["endereco"] == "Rua das Flores" and corpo["numero"] == "100"
    assert corpo["cep"] == "35930-000"
    assert [f["url"] for f in corpo["fotos"]] == ["/uploads/a.jpg"]
    assert corpo["criado_em"].endswith("Z")


def test_detalhe_inexistente(client):
    resp = client.get(f"{QUADRAS}/999")
    assert resp.status_code == 404
    assert resp.json()["code"] == "QUADRA_NAO_ENCONTRADA"


def test_detalhe_de_quadra_inativa(client, login, nova_quadra):
    dono, headers_dono = login("dono@muzzi.test")
    _, headers_admin = login("admin@muzzi.test", papel=PapelUsuario.ADMINISTRADOR)
    _, headers_outro = login("outro@muzzi.test")
    quadra = nova_quadra(dono, ativa=False)
    url = f"{QUADRAS}/{quadra.id}"

    assert client.get(url).status_code == 404
    assert client.get(url, headers=headers_outro).status_code == 404
    assert client.get(url, headers=headers_dono).json()["ativa"] is False
    assert client.get(url, headers=headers_admin).status_code == 200


def test_detalhe_de_quadra_de_dono_inativo(client, criar_usuario, nova_quadra):
    inativo = criar_usuario(email="inativo@muzzi.test", status=False)
    quadra = nova_quadra(inativo)
    assert client.get(f"{QUADRAS}/{quadra.id}").status_code == 404


def test_detalhe_com_token_invalido_da_401(client, dono, nova_quadra):
    quadra = nova_quadra(dono)
    resp = client.get(f"{QUADRAS}/{quadra.id}", headers={"Authorization": "Bearer lixo"})
    assert resp.status_code == 401
    assert resp.json()["code"] == "NAO_AUTENTICADO"


# --- GET /quadras/minhas -----------------------------------------------------------------


def test_minhas_quadras_lista_so_as_do_dono_inclusive_inativas(client, login, nova_quadra, dono):
    eu, headers = login()
    nova_quadra(eu, nome="Minha ativa")
    nova_quadra(eu, nome="Minha inativa", ativa=False)
    nova_quadra(dono, nome="De outro dono")

    resp = client.get(MINHAS, headers=headers)
    assert _nomes(resp) == ["Minha ativa", "Minha inativa"]
    assert [q["ativa"] for q in resp.json()["itens"]] == [True, False]
    assert _nomes(client.get(MINHAS, headers=headers, params={"cidade": "belo"})) == []


def test_minhas_quadras_exige_dono(client, login):
    assert client.get(MINHAS).status_code == 401
    _, headers_admin = login("admin@muzzi.test", papel=PapelUsuario.ADMINISTRADOR)
    resp = client.get(MINHAS, headers=headers_admin)
    assert resp.status_code == 403
    assert resp.json()["code"] == "ACESSO_NEGADO"
