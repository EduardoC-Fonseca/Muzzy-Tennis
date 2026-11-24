"""Tarefa 12 — cadastro de quadras e fotos (HU03, CT07–CT10)."""

from pathlib import Path

import pytest

from app.core.config import settings
from app.models import FotoQuadra, PapelUsuario

QUADRAS = "/api/v1/quadras"
SENHA = "senha-segura-123"

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 64


def payload(**sobrescrever):
    dados = {
        "nome": "Quadra Central",
        "descricao": "Quadra de saibro coberta, com iluminação.",
        "tipo_piso": "saibro",
        "coberta": True,
        "limite_jogadores": 4,
        "preco_hora": 80,
        "endereco": "Rua das Flores",
        "numero": "100",
        "bairro": "Centro",
        "cidade": "João Monlevade",
        "estado": "mg",
        "cep": "35930000",
    }
    dados.update(sobrescrever)
    return dados


@pytest.fixture(autouse=True)
def uploads_temporarios(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    return tmp_path


@pytest.fixture
def auth(client, criar_usuario):
    """Cria um usuário e devolve os headers com o token dele."""

    def _auth(email="dono@muzzi.test", papel=PapelUsuario.DONO_QUADRA):
        criar_usuario(email=email, senha=SENHA, papel=papel)
        resp = client.post("/api/v1/auth/login", data={"username": email, "password": SENHA})
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    return _auth


@pytest.fixture
def dono(auth):
    return auth()


@pytest.fixture
def quadra_id(client, dono):
    return client.post(QUADRAS, json=payload(), headers=dono).json()["id"]


def enviar(client, quadra_id, headers, *arquivos):
    files = [("fotos", (nome, conteudo, "application/octet-stream")) for nome, conteudo in arquivos]
    return client.post(f"{QUADRAS}/{quadra_id}/fotos", files=files, headers=headers)


def erros_por_campo(resp):
    return {e["campo"]: e["mensagem"] for e in resp.json()["erros"]}


# --- cadastro (CT07, CT08, CT10) -------------------------------------------------------------


def test_cadastra_quadra_com_dados_validos(client, dono):
    resp = client.post(QUADRAS, json=payload(), headers=dono)

    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["id"] > 0
    assert corpo["nome"] == "Quadra Central"
    assert corpo["tipo_piso"] == "saibro"
    assert corpo["estado"] == "MG"  # normalizado
    assert corpo["cep"] == "35930-000"  # normalizado
    assert corpo["preco_hora"] == 80.0  # número no JSON
    assert corpo["ativa"] is True
    assert corpo["fotos"] == []
    assert corpo["criado_em"].endswith("Z")  # UTC explícito


def test_campos_obrigatorios_ausentes_sao_listados(client, dono):
    resp = client.post(QUADRAS, json={}, headers=dono)

    assert resp.status_code == 422
    assert resp.json()["code"] == "VALIDACAO"
    erros = erros_por_campo(resp)
    for campo in ("nome", "descricao", "tipo_piso", "limite_jogadores", "preco_hora",
                  "endereco", "bairro", "cidade", "estado", "cep"):  # fmt: skip
        assert erros[campo] == "Campo obrigatório."
    assert "coberta" not in erros and "numero" not in erros  # opcionais


def test_descricao_acima_do_limite_e_rejeitada(client, dono):
    resp = client.post(QUADRAS, json=payload(descricao="x" * 501), headers=dono)
    assert resp.status_code == 422
    assert erros_por_campo(resp)["descricao"] == "Máximo de 500 caracteres."


def test_descricao_no_limite_e_aceita(client, dono):
    resp = client.post(QUADRAS, json=payload(descricao="x" * 500), headers=dono)
    assert resp.status_code == 201


@pytest.mark.parametrize(
    ("campo", "valor", "trecho"),
    [
        ("tipo_piso", "carpete", "Opções: 'saibro', 'rapida', 'grama' ou 'sintetico'"),
        ("estado", "XX", "UF inválida"),
        ("cep", "3593-000", "CEP inválido"),
        ("limite_jogadores", 0, "maior que 0"),
        ("preco_hora", -10, "maior que 0"),
        ("preco_hora", "80.123", "casas decimais"),
        ("nome", "   ", "pelo menos 1"),
    ],
)
def test_valores_invalidos_informam_o_campo(client, dono, campo, valor, trecho):
    resp = client.post(QUADRAS, json=payload(**{campo: valor}), headers=dono)
    assert resp.status_code == 422
    assert trecho in erros_por_campo(resp)[campo]


def test_campo_desconhecido_e_rejeitado(client, dono):
    resp = client.post(QUADRAS, json=payload(dono_id=999), headers=dono)
    assert resp.status_code == 422
    assert "dono_id" in erros_por_campo(resp)


def test_numero_vazio_vira_nulo(client, dono):
    resp = client.post(QUADRAS, json=payload(numero=""), headers=dono)
    assert resp.json()["numero"] is None


def test_cadastro_exige_login(client):
    assert client.post(QUADRAS, json=payload()).status_code == 401


@pytest.mark.parametrize("papel", [PapelUsuario.ADMINISTRADOR, PapelUsuario.CLIENTE])
def test_somente_dono_de_quadra_cadastra(client, auth, papel):
    headers = auth(email="outro@muzzi.test", papel=papel)
    resp = client.post(QUADRAS, json=payload(), headers=headers)
    assert resp.status_code == 403
    assert resp.json()["code"] == "ACESSO_NEGADO"


# --- fotos (CT09) ----------------------------------------------------------------------------


def test_envia_fotos_validas(client, dono, quadra_id, uploads_temporarios):
    resp = enviar(client, quadra_id, dono, ("a.jpg", JPEG), ("b.png", PNG), ("c.webp", WEBP))

    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["rejeitadas"] == []
    fotos = corpo["fotos"]
    assert [f["tipo_arquivo"] for f in fotos] == ["image/jpeg", "image/png", "image/webp"]
    assert [f["principal"] for f in fotos] == [True, False, False]
    assert [f["ordem"] for f in fotos] == [0, 1, 2]
    assert fotos[0]["url"].startswith(f"/uploads/quadras/{quadra_id}/")
    arquivo = Path(uploads_temporarios) / fotos[0]["url"].removeprefix("/uploads/")
    assert arquivo.read_bytes() == JPEG


def test_arquivo_invalido_volta_como_aviso_e_os_validos_sao_salvos(client, dono, quadra_id):
    resp = enviar(client, quadra_id, dono, ("ok.jpg", JPEG), ("doc.pdf", b"%PDF-1.4 conteudo"))

    assert resp.status_code == 201
    corpo = resp.json()
    assert len(corpo["fotos"]) == 1
    assert corpo["rejeitadas"] == [
        {
            "nome_arquivo": "doc.pdf",
            "code": "TIPO_NAO_SUPORTADO",
            "motivo": "Tipo de arquivo não suportado. Envie imagens JPEG, PNG ou WebP.",
        }
    ]


def test_extensao_falsa_e_detectada_pelo_conteudo(client, dono, quadra_id):
    resp = enviar(client, quadra_id, dono, ("foto.jpg", b"nao sou uma imagem"))
    assert resp.status_code == 422
    corpo = resp.json()
    assert corpo["code"] == "FOTOS_REJEITADAS"
    assert corpo["rejeitadas"][0]["code"] == "TIPO_NAO_SUPORTADO"


def test_arquivo_vazio_e_rejeitado(client, dono, quadra_id):
    resp = enviar(client, quadra_id, dono, ("vazio.jpg", b""))
    assert resp.json()["rejeitadas"][0]["code"] == "ARQUIVO_VAZIO"


def test_arquivo_grande_demais_e_rejeitado(client, dono, quadra_id, monkeypatch):
    monkeypatch.setattr(settings, "upload_max_bytes", 50)
    resp = enviar(client, quadra_id, dono, ("grande.jpg", JPEG))  # 68 bytes
    assert resp.status_code == 422
    assert resp.json()["rejeitadas"][0]["code"] == "ARQUIVO_MUITO_GRANDE"


def test_limite_de_fotos_por_quadra(client, dono, quadra_id, monkeypatch):
    monkeypatch.setattr(settings, "fotos_max_por_quadra", 2)
    resp = enviar(client, quadra_id, dono, ("1.jpg", JPEG), ("2.jpg", JPEG), ("3.jpg", JPEG))
    assert len(resp.json()["fotos"]) == 2
    assert resp.json()["rejeitadas"][0]["code"] == "LIMITE_FOTOS"

    resp = enviar(client, quadra_id, dono, ("4.jpg", JPEG))
    assert resp.status_code == 422
    assert resp.json()["rejeitadas"][0]["code"] == "LIMITE_FOTOS"


def test_novas_fotos_continuam_a_ordem(client, dono, quadra_id):
    enviar(client, quadra_id, dono, ("1.jpg", JPEG))
    fotos = enviar(client, quadra_id, dono, ("2.jpg", JPEG)).json()["fotos"]
    assert fotos[0]["ordem"] == 1
    assert fotos[0]["principal"] is False


def test_outro_dono_nao_envia_fotos(client, auth, quadra_id):
    outro = auth(email="outro@muzzi.test")
    resp = enviar(client, quadra_id, outro, ("a.jpg", JPEG))
    assert resp.status_code == 403


def test_administrador_pode_enviar_fotos(client, auth, quadra_id):
    admin = auth(email="admin@muzzi.test", papel=PapelUsuario.ADMINISTRADOR)
    assert enviar(client, quadra_id, admin, ("a.jpg", JPEG)).status_code == 201


def test_quadra_inexistente(client, dono):
    resp = enviar(client, 99999, dono, ("a.jpg", JPEG))
    assert resp.status_code == 404
    assert resp.json()["code"] == "QUADRA_NAO_ENCONTRADA"


def test_requisicao_sem_arquivos(client, dono, quadra_id):
    resp = client.post(f"{QUADRAS}/{quadra_id}/fotos", headers=dono)
    assert resp.status_code == 422
    assert erros_por_campo(resp)["fotos"] == "Campo obrigatório."


# --- remoção de fotos ------------------------------------------------------------------------


def test_remover_foto_principal_promove_a_proxima(client, db, dono, quadra_id, uploads_temporarios):
    fotos = enviar(client, quadra_id, dono, ("1.jpg", JPEG), ("2.png", PNG)).json()["fotos"]
    principal, segunda = fotos

    resp = client.delete(f"{QUADRAS}/{quadra_id}/fotos/{principal['id']}", headers=dono)

    assert resp.status_code == 204
    assert not (Path(uploads_temporarios) / principal["url"].removeprefix("/uploads/")).exists()
    restante = db.get(FotoQuadra, segunda["id"])
    db.refresh(restante)
    assert restante.principal is True
    assert db.get(FotoQuadra, principal["id"]) is None


def test_outro_dono_nao_remove_foto(client, auth, dono, quadra_id):
    foto = enviar(client, quadra_id, dono, ("1.jpg", JPEG)).json()["fotos"][0]
    outro = auth(email="outro@muzzi.test")
    resp = client.delete(f"{QUADRAS}/{quadra_id}/fotos/{foto['id']}", headers=outro)
    assert resp.status_code == 403


def test_remover_foto_inexistente(client, dono, quadra_id):
    resp = client.delete(f"{QUADRAS}/{quadra_id}/fotos/99999", headers=dono)
    assert resp.status_code == 404
    assert resp.json()["code"] == "FOTO_NAO_ENCONTRADA"
