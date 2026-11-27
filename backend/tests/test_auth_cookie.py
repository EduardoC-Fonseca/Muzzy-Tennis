"""Sessão por cookie HttpOnly (front web) com proteção CSRF, convivendo com o Bearer."""

import pytest

from app.core.config import settings
from tests.conftest import SENHA_TESTE
from tests.test_quadras_cadastro import payload

LOGIN = "/api/auth/login"
ME = "/api/auth/me"
CSRF = "/api/auth/csrf"
LOGOUT = "/api/auth/logout"
QUADRAS = "/api/quadras"
ORIGEM_FRONT = "http://localhost:8080"

QUADRA = payload()


@pytest.fixture
def sessao(client, criar_usuario):
    """Faz login como um navegador faria e devolve o token CSRF."""
    criar_usuario(email="dono@muzzi.test", senha=SENHA_TESTE)
    resp = client.post(
        LOGIN,
        data={"username": "dono@muzzi.test", "password": SENHA_TESTE},
        headers={"Origin": ORIGEM_FRONT},
    )
    assert resp.status_code == 200
    return resp.headers["X-CSRF-Token"]


def test_login_grava_cookie_httponly_e_devolve_csrf(client, criar_usuario):
    criar_usuario(email="dono@muzzi.test", senha=SENHA_TESTE)
    resp = client.post(LOGIN, data={"username": "dono@muzzi.test", "password": SENHA_TESTE})
    cookie = resp.headers["set-cookie"]
    assert "muzzi_session=" in cookie and "HttpOnly" in cookie
    assert f"Path={settings.api_prefix}" in cookie
    assert resp.headers["X-CSRF-Token"]
    assert resp.json()["access_token"]
    assert resp.headers["Cache-Control"] == "no-store"


def test_cookie_autentica_leituras_sem_csrf(client, sessao):
    resp = client.get(ME)
    assert resp.status_code == 200
    assert resp.json()["email"] == "dono@muzzi.test"


def test_escrita_por_cookie_sem_csrf_da_403(client, sessao):
    resp = client.post(QUADRAS, json=QUADRA)
    assert resp.status_code == 403
    assert resp.json()["code"] == "CSRF_INVALIDO"


def test_escrita_por_cookie_com_csrf_invalido_da_403(client, sessao):
    resp = client.post(QUADRAS, json=QUADRA, headers={"X-CSRF-Token": "x" * 64})
    assert resp.json()["code"] == "CSRF_INVALIDO"


def test_escrita_por_cookie_com_csrf_funciona(client, sessao):
    resp = client.post(QUADRAS, json=QUADRA, headers={"X-CSRF-Token": sessao})
    assert resp.status_code == 201


def test_rota_csrf_devolve_o_mesmo_token(client, sessao):
    resp = client.get(CSRF)
    assert resp.status_code == 200
    assert resp.json() == {"csrf_token": sessao}


def test_bearer_nao_exige_csrf(client, login):
    _, headers = login()
    assert client.post(QUADRAS, json=QUADRA, headers=headers).status_code == 201


def test_logout_remove_o_cookie(client, sessao):
    resp = client.post(LOGOUT, headers={"X-CSRF-Token": sessao})
    assert resp.status_code == 204
    assert 'muzzi_session=""' in resp.headers["set-cookie"]
    assert client.get(ME).status_code == 401


def test_logout_sem_csrf_da_403(client, sessao):
    assert client.post(LOGOUT).status_code == 403


@pytest.mark.parametrize(
    ("origem", "esperado"),
    [
        (None, 200),  # testes, apps e clientes que não são navegador
        (ORIGEM_FRONT, 200),  # liberada em CORS_ORIGINS
        ("http://testserver", 200),  # mesma origem da API (Swagger)
        ("http://site-malicioso.com", 403),
    ],
)
def test_origem_do_login(client, criar_usuario, origem, esperado):
    criar_usuario(email="dono@muzzi.test", senha=SENHA_TESTE)
    headers = {"Origin": origem} if origem else {}
    resp = client.post(
        LOGIN, data={"username": "dono@muzzi.test", "password": SENHA_TESTE}, headers=headers
    )
    assert resp.status_code == esperado
    if esperado == 403:
        assert resp.json()["code"] == "ORIGEM_NAO_PERMITIDA"
