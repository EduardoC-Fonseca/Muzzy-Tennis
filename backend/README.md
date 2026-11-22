# Muzzi Tennis — Backend

API REST do Muzzi Tennis. **FastAPI** + **SQLAlchemy 2** + **Alembic** + **MySQL 8**.

Artefatos de referência (fonte da verdade para regras de negócio):

- [Documento de Visão](../docs/gerenciamento/documento_visao.md) — requisitos, histórias (HU) e cenários de teste (CT)
- [Modelo de Dados](../docs/db/modelo_dados.md) — tabelas, enums e **decisões de implementação (D1–D6)**
- [Cronograma / EAP](../docs/gerenciamento/cronograma.md) — tarefas do backend e status
- [Riscos](../docs/gerenciamento/documento_riscos.md)
- [Pendências](../docs/pendencias.md) — decisões em aberto que bloqueiam tarefas

## Como rodar (desenvolvimento)

Pré-requisitos: Python 3.12+, Docker.

```bash
cd backend
cp .env.example .env
docker compose up -d db                 # MySQL 8.4 em localhost:3306
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head                    # cria as tabelas
python -m app.scripts.criar_admin --nome "Admin" --email admin@muzzi.local
uvicorn app.main:app --reload
```

- Swagger: <http://localhost:8000/docs> · ReDoc: <http://localhost:8000/redoc>
- Saúde: `GET /api/v1/health`

Para subir a API também em container: `docker compose --profile api up --build`.

## Estrutura

```
app/
  main.py            # cria a aplicação: CORS, handlers de erro, rotas, /uploads
  core/              # config (.env), segurança (JWT, Argon2), erros de domínio
  db/                # Base declarativa, mixins de timestamp, sessão
  models/            # um arquivo por tabela do modelo de dados + enums
  schemas/           # Pydantic: contratos de entrada/saída da API
  services/          # regras de negócio (não conhecem HTTP)
  api/
    deps.py          # sessão do banco, usuário atual, exigir_papel(...)
    router.py        # agrega as rotas sob /api/v1
    routes/          # um módulo por recurso
  scripts/           # utilitários de linha de comando
alembic/versions/    # migrações
tests/
```

Fluxo de uma requisição: **rota** (valida com schema) → **service** (regras, lança `AppError`) → **models/sessão**. As rotas não contêm regra de negócio; os serviços não importam nada do FastAPI.

## Convenções

- **Erros:** os serviços lançam subclasses de `AppError` (`NaoEncontradoError`, `ConflitoError`, `RegraNegocioError`, `AcessoNegadoError`...). A API responde `{"detail": "...", "code": "CODIGO"}`; o front-end deve se basear em `code` (risco R4).
- **Autorização:** `UsuarioAtual`, `AdminAtual`, `DonoQuadraAtual` ou `Depends(exigir_papel(...))` em `app/api/deps.py`. Usuário inativo perde acesso na hora, mesmo com token válido (CT17).
- **Datas:** tudo em **UTC** no banco (`app.db.base.utcnow`).
- **Clientes não fazem login:** são gravados em `usuarios` sem senha a partir dos dados da reserva (decisão D1).
- **Erros de banco no MySQL:** violação de `CHECK` chega como `OperationalError` (código 3819), não `IntegrityError`; violação de `UNIQUE`/FK chega como `IntegrityError`.

## Migrações

```bash
alembic revision --autogenerate -m "descricao da mudanca"   # revise o arquivo gerado!
alembic upgrade head
alembic downgrade -1
alembic check            # falha se os models divergirem do banco
```

No MySQL, o `downgrade` autogerado tenta remover índices de FK antes da tabela, o que falha. Remova esses `drop_index` quando a tabela inteira for removida (veja a migração inicial).

## Testes e qualidade

```bash
pytest                   # SQLite em memória
TEST_DATABASE_URL="mysql+pymysql://muzzi:muzzi@localhost:3306/muzzi_tennis_test?charset=utf8mb4" pytest
ruff check . && ruff format .
```

Rode contra o MySQL antes de entregar: o SQLite não reproduz ENUMs, travas nem todos os códigos de erro. O banco `muzzi_tennis_test` precisa existir (`CREATE DATABASE muzzi_tennis_test; GRANT ALL ON muzzi_tennis_test.* TO 'muzzi'@'%';`).
