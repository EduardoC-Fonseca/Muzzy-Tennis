# Muzzi Tennis — Backend

API REST do Muzzi Tennis. **FastAPI** + **SQLAlchemy 2** + **Alembic** + **MySQL 8**.

Artefatos de referência (fonte da verdade para regras de negócio):

- [Documento de Visão](../docs/gerenciamento/documento_visao.md) — requisitos, histórias (HU) e cenários de teste (CT)
- [Modelo de Dados](../docs/db/modelo_dados.md) — tabelas, enums e **decisões de implementação (D1–D6)**
- [Cronograma / EAP](../docs/gerenciamento/cronograma.md) — tarefas do backend e status
- [Riscos](../docs/gerenciamento/documento_riscos.md)
- [Pendências](../docs/pendencias.md) — decisões em aberto que bloqueiam tarefas
- [Contrato de integração com o front-end](../docs/integracao_frontend.md) — **atualize junto com qualquer mudança de endpoint, campo, validação, erro ou enum**

## Como rodar (desenvolvimento)

Pré-requisitos: Docker e, para a opção B, Python 3.12+. O **banco sempre roda no Docker**; a API pode rodar no Docker (A) ou no venv (B).

| | A — API no Docker | B — API no venv |
|---|---|---|
| Indicado para | Testar como na entrega, sem instalar Python | Desenvolver: recarrega a cada alteração (`--reload`) e permite depurar |
| Alterou o código? | Precisa de `--build` de novo | Recarrega sozinho |

As duas usam a porta **8000**: rode **uma de cada vez**.

### 1. Banco de dados (comum às duas)

```bash
cd backend
cp .env.example .env            # só na primeira vez
docker compose up -d db         # MySQL 8.4 em localhost:3306
```

### 2A. API no Docker

```bash
docker compose --profile api up -d --build    # aplica as migrações e sobe em :8000
docker compose --profile api logs -f api      # acompanhar os logs (Ctrl+C sai)
docker compose --profile api stop api         # parar a API (o banco continua)
```

Para rodar os scripts dentro do container, prefixe com `docker compose exec api`, como no passo 3.

### 2B. API no venv

```bash
python3 -m venv .venv && source .venv/bin/activate     # só na primeira vez
pip install -e ".[dev]"                                 # só na primeira vez / ao mudar dependências
alembic upgrade head                                    # aplica as migrações
uvicorn app.main:app --reload                           # sobe em :8000
```

### 3. Usuários para teste

Clientes não fazem login. **Donos de quadra** podem se cadastrar pela API (`POST /api/v1/auth/registro`, passo 2 do roteiro do Swagger) ou pelo script. **Administradores** só são criados pelo script. A senha é pedida no terminal. Se o e-mail já existir, o script atualiza o usuário: troca a senha, aplica o papel informado e reativa a conta. Isso serve para redefinir a senha de um usuário de teste.

```bash
# venv:
python -m app.scripts.criar_usuario --papel dono_quadra --nome "Dono Teste" --email dono@muzzi.local
python -m app.scripts.criar_usuario --papel administrador --nome "Admin" --email admin@muzzi.local
# Docker: o mesmo comando com o prefixo
docker compose exec api python -m app.scripts.criar_usuario --papel dono_quadra --nome "Dono Teste" --email dono@muzzi.local
```

## Teste manual pelo Swagger

Abra <http://localhost:8000/docs>. O contrato de cada endpoint está em [`docs/integracao_frontend.md`](../docs/integracao_frontend.md).

1. **Saúde:** `GET /api/v1/health` → *Try it out* → *Execute*. Esperado: `{"status": "ok", "banco": "ok"}`.
2. **Cadastro de dono:** `POST /api/v1/auth/registro` com `{"nome": "Maria Souza", "email": "maria@muzzi.local", "telefone": "(31) 99999-9999", "senha": "senha-segura-123"}`. Esperado: `201` com `papel = dono_quadra`. Repetir o mesmo e-mail dá `409 EMAIL_JA_CADASTRADO`; uma senha curta dá `422`.
3. **Login:** clique em **Authorize** (cadeado, no topo), preencha `username` com o e-mail do dono e `password` com a senha e confirme. Daqui em diante o Swagger envia o token sozinho.
4. **Conferir o usuário:** `GET /api/v1/auth/me` deve devolver o papel `dono_quadra`.
5. **Cadastrar quadra (CT07):** `POST /api/v1/quadras` com o corpo abaixo. Esperado: `201`, com `estado` em maiúsculas e o `cep` formatado.
   ```json
   {
     "nome": "Quadra Central", "descricao": "Quadra coberta com iluminação.",
     "tipo_piso": "saibro", "coberta": true, "limite_jogadores": 4, "preco_hora": 80,
     "endereco": "Rua das Flores", "numero": "100", "bairro": "Centro",
     "cidade": "João Monlevade", "estado": "mg", "cep": "35930000"
   }
   ```
6. **Validações (CT08, CT10):** reenvie com `{}`, com uma `descricao` de 501 caracteres, `"tipo_piso": "carpete"` ou `"cep": "123"`. Esperado: `422`, `code = VALIDACAO` e a lista `erros` indicando cada campo.
7. **Fotos (CT09):** `POST /api/v1/quadras/{quadra_id}/fotos` com o `id` da quadra. Em `fotos`, clique em **Escolher arquivo**. Para mandar mais de um arquivo, use *Add string item*: cada clique cria um novo seletor. Misture uma imagem (JPEG/PNG/WebP) com um PDF ou TXT. Esperado: `201`, a imagem em `fotos` e o outro arquivo em `rejeitadas`, com o motivo. Abra `http://localhost:8000` + a `url` devolvida para ver a imagem. Só arquivos inválidos dão `422 FOTOS_REJEITADAS`.
8. **Permissões:** faça login como administrador (Authorize → *Logout* → login de novo) e tente `POST /quadras`: `403`. Sem login: `401`.
9. **Remover foto:** `DELETE /api/v1/quadras/{quadra_id}/fotos/{foto_id}` → `204`. Se era a principal, a próxima foto vira a principal (confira no banco).
10. **Consultar quadras (tarefa 13):** sem login (Authorize → *Logout*), `GET /api/v1/quadras` com `cidade = joao monlevade` (sem acento) e `tipo_piso = saibro`: a quadra cadastrada aparece. `GET /api/v1/quadras/{quadra_id}` traz o detalhe com as fotos. Logado como dono, `GET /api/v1/quadras/minhas` lista as quadras dele, inclusive as inativas.

## Acessar o banco (DBeaver ou outro cliente)

Com o container `db` rodando, crie uma conexão **MySQL** no DBeaver:

| Campo | Valor |
|---|---|
| Host / Porta | `localhost` / `3306` |
| Database | `muzzi_tennis` (o banco dos testes automatizados é `muzzi_tennis_test`) |
| Usuário / Senha | `muzzi` / `muzzi` (ou `root` / `root`, valores do `.env`) |
| Driver properties | `allowPublicKeyRetrieval = true` e `useSSL = false` |

As *driver properties* evitam o erro **"Public Key Retrieval is not allowed"**, comum ao conectar no MySQL 8 sem SSL. Ficam na aba *Driver properties* da conexão.

Pelo terminal, sem cliente gráfico: `docker compose exec db mysql -umuzzi -pmuzzi muzzi_tennis`.

### Recomeçar do zero

```bash
docker compose --profile api down -v    # remove containers E o volume do banco (apaga todos os dados)
rm -rf uploads/                         # fotos enviadas
```
Depois, repita os passos 1 a 3.

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

- **Erros de validação** de entrada saem como `422` com `code = VALIDACAO` e `erros[{campo, mensagem}]` em português (`app/core/exceptions.py`).
- **Erros:** os serviços lançam subclasses de `AppError` (`NaoEncontradoError`, `ConflitoError`, `RegraNegocioError`, `AcessoNegadoError`...). A API responde `{"detail": "...", "code": "CODIGO"}`; o front-end deve se basear em `code` (risco R4).
- **Autorização:** `UsuarioAtual`, `AdminAtual`, `DonoQuadraAtual` ou `Depends(exigir_papel(...))` em `app/api/deps.py`. Usuário inativo perde acesso na hora, mesmo com token válido (CT17).
- **Datas:** tudo em **UTC** no banco (`app.db.base.utcnow`); nas respostas use `DataHoraUTC` (sai com `Z`) e, para dinheiro, `Dinheiro` (sai como número) — `app/schemas/common.py`.
- **Clientes não fazem login:** são gravados em `usuarios` sem senha a partir dos dados da reserva (decisão D1).
- **Busca por texto:** usa `ILIKE` com curingas escapados. Ignorar acentos depende da collation `utf8mb4_0900_ai_ci` do MySQL: no SQLite dos testes, só maiúsculas são ignoradas (os testes de acento rodam só no MySQL).
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
