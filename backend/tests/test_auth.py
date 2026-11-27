from app.models import PapelUsuario

LOGIN = "/api/auth/login"
ME = "/api/auth/me"


def _login(client, email, senha):
    return client.post(LOGIN, data={"username": email, "password": senha})


def test_login_e_me(client, criar_usuario):
    criar_usuario(email="dono@muzzi.test", senha="senha-segura-123")

    resp = _login(client, "dono@muzzi.test", "senha-segura-123")
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me = client.get(ME, headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    corpo = me.json()
    assert corpo["email"] == "dono@muzzi.test"
    assert corpo["papel"] == "dono_quadra"
    assert corpo["status"] is True
    assert "senha_hash" not in corpo


def test_login_senha_errada(client, criar_usuario):
    criar_usuario()
    resp = _login(client, "dono@muzzi.test", "errada")
    assert resp.status_code == 401
    assert resp.json()["code"] == "CREDENCIAIS_INVALIDAS"


def test_cliente_sem_senha_nao_faz_login(client, criar_usuario):
    criar_usuario(email="cliente@muzzi.test", senha=None, papel=PapelUsuario.CLIENTE)
    resp = _login(client, "cliente@muzzi.test", "")
    assert resp.status_code in (401, 422)


def test_usuario_inativo_nao_faz_login(client, criar_usuario):
    criar_usuario(status=False)
    resp = _login(client, "dono@muzzi.test", "senha-segura-123")
    assert resp.status_code == 403
    assert resp.json()["code"] == "USUARIO_INATIVO"


def test_token_perde_validade_ao_desativar_usuario(client, db, criar_usuario):
    """CT17: desativação bloqueia o acesso imediatamente."""
    usuario = criar_usuario()
    token = _login(client, "dono@muzzi.test", "senha-segura-123").json()["access_token"]

    usuario.status = False
    db.commit()

    resp = client.get(ME, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert resp.json()["code"] == "USUARIO_INATIVO"


def test_sem_token_retorna_401_no_formato_padrao(client):
    resp = client.get(ME)
    assert resp.status_code == 401
    assert resp.json() == {
        "detail": "Faça login para acessar este recurso.",
        "code": "NAO_AUTENTICADO",
    }
    assert resp.headers["www-authenticate"] == "Bearer"


def test_erros_do_framework_saem_no_formato_padrao(client):
    resp = client.get("/api/nao-existe")
    assert resp.status_code == 404
    assert resp.json()["code"] == "NAO_ENCONTRADO"

    resp = client.put("/api/health")
    assert resp.status_code == 405
    assert resp.json()["code"] == "METODO_NAO_PERMITIDO"


def test_openapi_marca_fotos_como_arquivo(client):
    """O Swagger só mostra o seletor de arquivo com format: binary."""
    esquemas = client.get("/openapi.json").json()["components"]["schemas"]
    corpo = next(v for k, v in esquemas.items() if k.startswith("Body_enviar_fotos"))
    assert corpo["properties"]["fotos"]["items"]["format"] == "binary"


def test_token_invalido_retorna_401(client):
    resp = client.get(ME, headers={"Authorization": "Bearer nao-e-um-jwt"})
    assert resp.status_code == 401
    assert resp.json()["code"] == "NAO_AUTENTICADO"
