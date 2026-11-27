"""Cadastro público de dono de quadra: POST /auth/registro (pendência P03)."""

import pytest

from app.models import PapelUsuario

REGISTRO = "/api/auth/registro"
LOGIN = "/api/auth/login"
ME = "/api/auth/me"


def _dados(**sobrescrever):
    dados = {
        "nome": "Maria Souza",
        "email": "maria@muzzi.test",
        "telefone": "(31) 99999-9999",
        "senha": "senha-segura-123",
    }
    dados.update(sobrescrever)
    return dados


def _erros(resp):
    return {e["campo"]: e["mensagem"] for e in resp.json()["erros"]}


def test_registro_cria_dono_ativo_e_permite_login(client):
    resp = client.post(REGISTRO, json=_dados())
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["papel"] == "dono_quadra"
    assert corpo["status"] is True
    assert corpo["email"] == "maria@muzzi.test"
    assert corpo["telefone"] == "(31) 99999-9999"
    assert corpo["criado_em"].endswith("Z")
    assert "senha" not in corpo and "senha_hash" not in corpo

    credenciais = {"username": "maria@muzzi.test", "password": "senha-segura-123"}
    login = client.post(LOGIN, data=credenciais)
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = client.get(ME, headers={"Authorization": f"Bearer {token}"})
    assert me.json()["id"] == corpo["id"]


def test_registro_normaliza_email_e_nome(client):
    resp = client.post(REGISTRO, json=_dados(email="  Maria@MUZZI.test ", nome="  Maria   Souza "))
    assert resp.status_code == 201
    assert resp.json()["email"] == "maria@muzzi.test"
    assert resp.json()["nome"] == "Maria Souza"


@pytest.mark.parametrize("telefone", [None, ""])
def test_registro_telefone_opcional(client, telefone):
    resp = client.post(REGISTRO, json=_dados(telefone=telefone))
    assert resp.status_code == 201
    assert resp.json()["telefone"] is None


def test_registro_sem_telefone_no_corpo(client):
    dados = _dados()
    del dados["telefone"]
    assert client.post(REGISTRO, json=dados).status_code == 201


def test_registro_campos_obrigatorios(client):
    resp = client.post(REGISTRO, json={})
    assert resp.status_code == 422
    assert resp.json()["code"] == "VALIDACAO"
    assert set(_erros(resp)) == {"nome", "email", "senha"}


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("email", "sem-arroba"),
        ("email", "a@b"),
        ("senha", "curta"),
        ("senha", "          "),
        ("telefone", "123"),
        ("telefone", "abc-defg-hijk"),
        ("nome", "   "),
        ("nome", "x" * 151),
    ],
)
def test_registro_valores_invalidos(client, campo, valor):
    resp = client.post(REGISTRO, json=_dados(**{campo: valor}))
    assert resp.status_code == 422
    assert campo in _erros(resp)


def test_registro_nao_aceita_papel(client):
    """O papel é sempre dono_quadra: o corpo não pode escolher administrador."""
    resp = client.post(REGISTRO, json=_dados(papel="administrador"))
    assert resp.status_code == 422
    assert _erros(resp)["papel"] == "Campo não permitido."


def test_registro_email_duplicado(client, criar_usuario):
    criar_usuario(email="maria@muzzi.test")
    resp = client.post(REGISTRO, json=_dados(email="MARIA@muzzi.test"))
    assert resp.status_code == 409
    assert resp.json()["code"] == "EMAIL_JA_CADASTRADO"


def test_registro_email_de_cliente_existente(client, criar_usuario):
    criar_usuario(email="maria@muzzi.test", senha=None, papel=PapelUsuario.CLIENTE)
    resp = client.post(REGISTRO, json=_dados())
    assert resp.status_code == 409
    assert resp.json()["code"] == "EMAIL_JA_CADASTRADO"


def test_registro_nao_exige_login(client):
    """Rota pública: funciona sem Authorization."""
    assert client.post(REGISTRO, json=_dados()).status_code == 201
