"""Fixtures de teste.

Por padrão os testes usam SQLite em memória (rápido, sem dependências). Para rodar contra o
MySQL — recomendado antes de entregar, pois valida ENUMs, CHECKs e travas reais — defina:

    TEST_DATABASE_URL=mysql+pymysql://muzzi:muzzi@localhost:3306/muzzi_tennis_test pytest

(o banco de teste precisa existir; as tabelas são recriadas a cada sessão de testes).
"""

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import hash_senha
from app.db.session import get_db
from app.main import app
from app.models import Base, PapelUsuario, Quadra, TipoPiso, Usuario

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite://")


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    if TEST_DATABASE_URL.startswith("sqlite"):
        eng = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        # Receita do SQLAlchemy: o pysqlite não emite BEGIN sozinho, o que quebra SAVEPOINTs
        # (e, portanto, o isolamento entre testes). Assumimos o controle da transação.
        @event.listens_for(eng, "connect")
        def _on_connect(dbapi_conn, _):
            dbapi_conn.isolation_level = None
            dbapi_conn.execute("PRAGMA foreign_keys=ON")  # SQLite só aplica FKs com isto

        @event.listens_for(eng, "begin")
        def _on_begin(conn):
            conn.exec_driver_sql("BEGIN")
    else:
        eng = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def db(engine: Engine) -> Iterator[Session]:
    """Sessão isolada por teste: tudo roda numa transação desfeita ao final."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def criar_usuario(db: Session):
    def _criar(
        *,
        email: str = "dono@muzzi.test",
        senha: str | None = "senha-segura-123",
        papel: PapelUsuario = PapelUsuario.DONO_QUADRA,
        status: bool = True,
        nome: str = "Usuário Teste",
    ) -> Usuario:
        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_senha(senha) if senha else None,
            papel=papel,
            status=status,
        )
        db.add(usuario)
        db.commit()
        return usuario

    return _criar


SENHA_TESTE = "senha-segura-123"


@pytest.fixture
def login(client, criar_usuario):
    """Cria um usuário e devolve (usuario, headers com o token)."""

    def _login(email="dono@muzzi.test", papel=PapelUsuario.DONO_QUADRA, status=True):
        usuario = criar_usuario(email=email, senha=SENHA_TESTE, papel=papel, status=status)
        token = client.post(
            "/api/auth/login", data={"username": email, "password": SENHA_TESTE}
        ).json()
        # O login também grava o cookie de sessão; limpa para que só o Bearer autentique e
        # requisições "sem token" continuem anônimas. O fluxo por cookie: test_auth_cookie.py.
        client.cookies.clear()
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
