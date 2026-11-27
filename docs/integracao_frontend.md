# Muzzi Tennis — Contrato de Integração Front-end ↔ Backend

Contrato da API REST consumida pelo front-end Flutter: convenções, autenticação, formato de erros, enums, endpoints e o mapeamento dos campos das telas. Mitiga o risco **R4** (falhas na integração entre front-end e backend) de [`gerenciamento/documento_riscos.md`](gerenciamento/documento_riscos.md).

> **Regra de manutenção:** este documento é atualizado **no mesmo commit** de qualquer mudança no backend que afete a integração: endpoint novo ou alterado, campo, regra de validação, código de erro ou enum. Cada mudança entra no [Histórico de alterações](#histórico-de-alterações).
>
> A referência executável é o OpenAPI gerado pela API (`/docs` e `/openapi.json`). Se houver divergência entre ele e este documento, o código vale e o documento deve ser corrigido.

**Versão do contrato:** 0.8.0 · **Última atualização:** 27/11/2026

---

## 1. Ambiente

| Item | Valor (desenvolvimento) |
|---|---|
| URL base da API | `http://localhost:8000/api` (sem versão no caminho) |
| Front pelo `docker-compose.yml` da raiz | `http://localhost:8080`. O nginx do front repassa `/api/` e `/uploads/` para a API, então o app usa caminhos relativos (`Uri.base.resolve('/api/...')`) e fica na mesma origem da API |
| Documentação interativa (Swagger) | `http://localhost:8000/docs` |
| Especificação OpenAPI | `http://localhost:8000/openapi.json` |
| Arquivos enviados (fotos) | `http://localhost:8000` + campo `url` (ex.: `http://localhost:8000/uploads/quadras/1/abc.jpg`) |
| CORS | Origens liberadas por `CORS_ORIGINS` no `.env` do backend (padrão: `localhost:3000`, `localhost:8080`, `127.0.0.1:8080`) |

> **Flutter web:** rode com uma porta fixa liberada no CORS, por exemplo `flutter run -d chrome --web-port 8080`. Para usar outra porta, inclua a origem em `CORS_ORIGINS`.

Recomendação: centralizar a URL base num único lugar do app (ex.: `const apiBaseUrl = String.fromEnvironment('API_URL', defaultValue: 'http://localhost:8000/api');`).

## 2. Convenções

| Assunto | Regra |
|---|---|
| Formato | JSON UTF-8 (`Content-Type: application/json`), exceto o login (form-urlencoded) e o envio de fotos (multipart). |
| Nomes de campos | `snake_case`, iguais ao [modelo de dados](db/modelo_dados.md). |
| IDs | Inteiros. |
| Datas e horas (registros) | Momentos como `criado_em` vêm em ISO 8601 **UTC** com sufixo `Z` (ex.: `2026-11-23T23:03:57.621568Z`). Converta para o horário local na exibição (`DateTime.parse(s).toLocal()`). |
| Datas e horas dos horários de quadra | `data` em `AAAA-MM-DD` e `hora_inicio`/`hora_fim` em `HH:MM`, **sem fuso**: já são o horário local da quadra (`America/Sao_Paulo`). **Não converta**. Na entrada, a hora aceita `HH:MM` ou `HH:MM:SS` (os segundos são descartados). |
| Valores monetários | Na resposta, sempre **número** (ex.: `95.5`). Na requisição, aceita número ou texto (`80`, `"80.00"`), com no máximo 2 casas decimais. |
| Enums | Texto minúsculo, exatamente como na [seção 5](#5-enums). Qualquer outro valor é rejeitado. |
| Listagens paginadas | Parâmetros `pagina` (a partir de 1, padrão 1) e `por_pagina` (1–100, padrão 20). Resposta: `{"itens": [...], "total": 42, "pagina": 1, "por_pagina": 20, "total_paginas": 3}`. Uma página além da última devolve `itens: []`, não erro. |
| Campos opcionais | Podem ser omitidos ou enviados como `null`. Na resposta, o campo sempre aparece (com `null` quando vazio). |
| Campos desconhecidos | Nos corpos de criação, campos fora do contrato são **rejeitados** (422), o que evita erros de digitação silenciosos. |
| Espaços | O backend remove espaços no início e no fim dos textos. Um texto só de espaços conta como vazio. |

## 3. Autenticação

| Perfil | Faz login? | Como acessa |
|---|---|---|
| `cliente` | **Não** | Reserva informando os dados de identificação (próximas tarefas). |
| `dono_quadra` | Sim | Cria a própria conta em `POST /auth/registro` (ver 6.4) e depois faz login. Sessão JWT. |
| `administrador` | Sim | Conta criada só pela equipe, por script (não há cadastro público). Sessão JWT. |

O JWT pode chegar à API de **duas formas**. Se as duas vierem, vale o cabeçalho `Authorization`.

| Forma | Quem usa | CSRF |
|---|---|---|
| Cookie HttpOnly `muzzi_session`, gravado pelo login | **Front web (Flutter)**. O navegador envia o cookie sozinho; o app não lê nem guarda o token | Escritas (`POST`, `PUT`, `PATCH`, `DELETE`) exigem o cabeçalho `X-CSRF-Token` |
| Cabeçalho `Authorization: Bearer <token>`, com o `access_token` do corpo do login | Swagger (botão *Authorize*), testes, clientes que não são navegador | Não exigido (não há cookie) |

### Fluxo do front web (cookie)

1. `POST /auth/login` com `username` (e-mail) e `password` em **form-urlencoded** (padrão OAuth2), não JSON. A resposta grava o cookie e traz o token CSRF no cabeçalho `X-CSRF-Token`.
2. Leituras (`GET`) só precisam do cookie, que o navegador envia sozinho.
3. Escritas: envie `X-CSRF-Token: <token>`. Se o app recarregar e perder o token, recupere com `GET /auth/csrf` (6.3.1). Sem ele, a resposta é `403 CSRF_INVALIDO`.
4. A sessão expira em **60 minutos** (`ACCESS_TOKEN_EXPIRE_MINUTES`). Ao receber `401`, mande o usuário para o login.
5. Conta desativada pelo administrador recebe `403` com `code = USUARIO_INATIVO`, **mesmo com uma sessão ainda válida** (CT17). Mostre a mensagem e encerre a sessão.
6. Sair: `POST /auth/logout` com `X-CSRF-Token` (6.3.2).

O login recusa navegadores em origens não liberadas (`403 ORIGEM_NAO_PERMITIDA`). São aceitas: a mesma origem da API, as origens de `CORS_ORIGINS` e requisições sem cabeçalho `Origin`.

```dart
final resp = await http.post(
  Uri.parse('$apiBaseUrl/auth/login'),
  body: {'username': email, 'password': senha}, // Map → form-urlencoded
);
final csrf = resp.headers['x-csrf-token']; // guardar em memória para as escritas
// Fora do navegador (sem cookie): jsonDecode(resp.body)['access_token'] → Authorization: Bearer
```

## 4. Formato de erros

Toda resposta de erro (4xx) tem o mesmo formato:

```json
{ "detail": "Mensagem legível para o usuário.", "code": "CODIGO_ESTAVEL" }
```

- `detail`: mensagem em português, pronta para exibir.
- `code`: identificador estável. **Decida o comportamento da tela pelo `code`**, nunca pelo texto do `detail`, que pode mudar.
- Alguns erros trazem campos extras, como `erros` e `rejeitadas`, descritos abaixo.

### 4.1 Erro de validação (`422`, `code = VALIDACAO`)

Indica quais campos corrigir (CT08). `campo` é o nome do campo do contrato; em listas, inclui o índice (ex.: `fotos.0`).

```json
{
  "detail": "Dados inválidos.",
  "code": "VALIDACAO",
  "erros": [
    { "campo": "descricao", "mensagem": "Máximo de 500 caracteres." },
    { "campo": "cep", "mensagem": "CEP inválido. Use o formato 00000-000." }
  ]
}
```

Sugestão: converter `erros` num `Map<String, String>` e usar como `errorText` de cada `TextFormField`.

### 4.2 Códigos de erro

| HTTP | `code` | Quando | Sugestão na interface |
|---|---|---|---|
| 401 | `NAO_AUTENTICADO` | Sem token (`"Faça login para acessar este recurso."`), token inválido ou expirado | Redirecionar para o login |
| 401 | `CREDENCIAIS_INVALIDAS` | Login com e-mail ou senha errados | Mensagem no formulário de login |
| 403 | `USUARIO_INATIVO` | Conta desativada (login ou token válido) | Mensagem e logout |
| 403 | `ACESSO_NEGADO` | Perfil sem permissão, ou recurso de outro proprietário | Mensagem "sem permissão" |
| 403 | `CSRF_INVALIDO` | Escrita autenticada por cookie sem `X-CSRF-Token` válido | Buscar o token em `GET /auth/csrf` e repetir |
| 403 | `ORIGEM_NAO_PERMITIDA` | Login vindo de uma origem fora de `CORS_ORIGINS` | Erro de configuração: liberar a origem no backend |
| 404 | `NAO_ENCONTRADO` | Recurso genérico ou endereço inexistente | — |
| 405 | `METODO_NAO_PERMITIDO` | Método HTTP errado para o endereço (ex.: `PUT` onde só há `GET`) | Erro de programação: revisar a chamada |
| 404 | `QUADRA_NAO_ENCONTRADA` | Quadra inexistente | — |
| 404 | `HORARIO_NAO_ENCONTRADO` | Horário inexistente ou de outra quadra | — |
| 409 | `HORARIO_RESERVADO` | Tentativa de alterar ou remover um horário reservado (CT12) | Explicar que horários reservados são preservados |
| 409 | `HORARIO_PASSADO` | Tentativa de alterar, remover ou reservar um horário que já começou | Esconder as ações de horários passados |
| 409 | `HORARIO_INDISPONIVEL` | Reserva de um horário que outro cliente reservou ou que o dono bloqueou (CT02; com `POST /reservas`, tarefa 14) | Recarregar a disponibilidade e pedir outro horário |
| 409 | `HORARIO_COM_HISTORICO` | Remover um horário que já teve reservas (canceladas ou expiradas) | Sugerir bloquear o horário |
| 409 | `HORARIO_JA_CADASTRADO` | Geração simultânea criou o mesmo horário (raro) | Repetir a operação |
| 422 | `PERIODO_SEM_DATAS` | Nenhuma data do período cai nos dias da semana escolhidos | Mensagem no formulário |
| 422 | `PERIODO_INVALIDO` | Na listagem, `data_fim` antes de `data_inicio` ou período acima de 92 dias | Ajustar o filtro |
| 404 | `FOTO_NAO_ENCONTRADA` | Foto inexistente ou de outra quadra | — |
| 409 | `EMAIL_JA_CADASTRADO` | Cadastro de dono com e-mail já usado por outra conta (ver 6.4) | Erro no campo e-mail, com link para o login |
| 422 | `VALIDACAO` | Campos inválidos ou ausentes (ver 4.1) | Erro em cada campo |
| 422 | `FOTOS_REJEITADAS` | Nenhuma foto do envio foi aceita (ver 6.6) | Listar `rejeitadas[].motivo` |

## 5. Enums

| Enum | Valores | Rótulo sugerido na tela |
|---|---|---|
| `papel_usuario` | `cliente`, `dono_quadra`, `administrador` | Cliente, Dono de quadra, Administrador |
| `tipo_piso` | `saibro`, `rapida`, `grama`, `sintetico` | Saibro, Rápida, Grama, Sintética |
| `status_horario` | `disponivel`, `reservado`, `bloqueado` | Disponível, Reservado, Bloqueado |
| `status_reserva` | `aguardando_pagamento`, `confirmada`, `cancelada`, `expirada`, `concluida` | *(próximas tarefas)* |
| `status_pagamento` | `pendente`, `pago`, `falhou`, `estornado`, `estornado_parcialmente` | *(próximas tarefas)* |
| `metodo_pagamento` | `pix`, `cartao_credito`, `cartao_debito` | *(próximas tarefas)* |
| `status_estorno` | `pendente`, `processado`, `recusado` | *(próximas tarefas)* |

> ⚠️ **Pendência P01** ([`pendencias.md`](pendencias.md)): o enum `TipoSuperficie` do Flutter (`saibro`, `dura`, `gramaSintetica`, `carpete`) **não** corresponde a `tipo_piso`. Sugestão de substituição:
>
> ```dart
> enum TipoPiso {
>   saibro('saibro', 'Saibro'),
>   rapida('rapida', 'Rápida'),
>   grama('grama', 'Grama'),
>   sintetico('sintetico', 'Sintética');
>
>   final String api;        // valor enviado/recebido na API
>   final String descricao;  // rótulo exibido
>   const TipoPiso(this.api, this.descricao);
>
>   static TipoPiso fromApi(String v) => values.firstWhere((e) => e.api == v);
> }
> ```

`usuarios.status` é **boolean** (`true` = ativo), não um enum.

## 6. Endpoints

Legenda: ✅ disponível · 🕒 planejado (ver [seção 8](#8-endpoints-planejados))

### 6.1 `GET /health` ✅

Verifica a API e o banco. Público.

```json
200 { "status": "ok", "banco": "ok" }
```
`banco` vale `"indisponivel"` se o MySQL não responder.

### 6.2 `POST /auth/login` ✅

Público. Corpo **`application/x-www-form-urlencoded`**:

| Campo | Tipo | Obrigatório | Observação |
|---|---|---|---|
| `username` | texto | sim | E-mail do usuário |
| `password` | texto | sim | Senha |

```json
200 { "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```
Cabeçalhos da resposta: `Set-Cookie: muzzi_session=...; HttpOnly; Path=/api; SameSite=lax` e `X-CSRF-Token: <token>`. O front web usa o cookie e o `X-CSRF-Token`; o `access_token` do corpo serve para o Bearer.

Erros: `401 CREDENCIAIS_INVALIDAS`, `403 USUARIO_INATIVO`, `403 ORIGEM_NAO_PERMITIDA`, `422 VALIDACAO`.

### 6.3 `GET /auth/me` ✅

Requer token. Devolve o usuário autenticado (`UsuarioPublico`):

```json
200 {
  "id": 1, "nome": "Admin Dev", "email": "admin@muzzi.local", "telefone": null,
  "papel": "administrador", "status": true, "criado_em": "2026-11-22T02:02:20Z"
}
```
Use `papel` para decidir quais telas exibir.

#### 6.3.1 `GET /auth/csrf` ✅ — Token CSRF da sessão

Requer sessão. Devolve o mesmo token do cabeçalho `X-CSRF-Token` do login, para quando o app recarrega a página.

```json
200 { "csrf_token": "3f9a..." }
```

#### 6.3.2 `POST /auth/logout` ✅ — Encerrar sessão

Requer sessão e, pelo cookie, o cabeçalho `X-CSRF-Token`. Resposta `204`, apagando o cookie. Com Bearer, basta descartar o token no cliente.

### 6.4 `POST /auth/registro` ✅ — Cadastro de dono de quadra

Público (sem token). Usado pela tela `/cadastro-login`, aberta pelo link "Cadastre-se aqui" do login. Cria sempre uma conta de **dono de quadra**, já ativa, sem aprovação do administrador. Administradores não se cadastram por aqui.

Corpo JSON:

| Campo | Tipo | Obrigatório | Regras | Exemplo |
|---|---|---|---|---|
| `nome` | texto | sim | 1–150 caracteres; espaços repetidos viram um só | `"Maria Souza"` |
| `email` | texto | sim | formato de e-mail, até 150; gravado em minúsculas; **único** | `"maria@email.com"` |
| `telefone` | texto | não | DDD + número (10 a 13 dígitos); aceita `( ) - +` e espaços; `""` vira `null` | `"(31) 99999-9999"` |
| `senha` | texto | sim | **8 a 128** caracteres; não pode ser só espaços; não é aparada | `"minha-senha-123"` |

Não há campo `papel`: enviá-lo dá `422` ("Campo não permitido."). A **confirmação de senha** é validada só na tela; não envie esse campo.

```json
201 {
  "id": 4, "nome": "Maria Souza", "email": "maria@email.com", "telefone": "(31) 99999-9999",
  "papel": "dono_quadra", "status": true, "criado_em": "2026-11-24T14:10:00Z"
}
```
A resposta **não traz token**. Para entrar direto após o cadastro, chame `POST /auth/login` com o e-mail e a senha digitados.

Erros:
- `422 VALIDACAO`: campos ausentes ou inválidos, com `erros[]` por campo.
- `409 EMAIL_JA_CADASTRADO`: o e-mail já pertence a outra conta. Isso inclui um **cliente que já reservou** com esse e-mail, porque o e-mail é único em `usuarios`.

### 6.5 `POST /quadras` ✅ — Cadastrar quadra

**Tarefa 12 · HU03 · CT07, CT08, CT10.** Requer token de **`dono_quadra`**; administrador e cliente recebem `403 ACESSO_NEGADO`. A quadra fica vinculada ao dono autenticado (não envie `dono_id`).

**Corpo (JSON):**

| Campo | Tipo | Obrigatório | Regras | Exemplo |
|---|---|---|---|---|
| `nome` | texto | sim | 1–150 caracteres | `"Quadra Central"` |
| `descricao` | texto | sim | 1–**500** caracteres (CT10) | `"Quadra coberta com iluminação."` |
| `tipo_piso` | enum `tipo_piso` | sim | ver seção 5 | `"saibro"` |
| `coberta` | boolean | não (padrão `false`) | | `true` |
| `limite_jogadores` | inteiro | sim | > 0 (capacidade máxima) | `4` |
| `preco_hora` | número | sim | > 0, até 2 casas decimais (valor do aluguel por hora) | `80.00` |
| `endereco` | texto | sim | 1–255 (logradouro) | `"Rua das Flores"` |
| `numero` | texto | não | até 20; `""` vira `null` | `"100"` |
| `bairro` | texto | sim | 1–100 | `"Centro"` |
| `cidade` | texto | sim | 1–100 | `"João Monlevade"` |
| `estado` | texto | sim | sigla de UF válida; aceita minúsculas e devolve em maiúsculas | `"MG"` |
| `cep` | texto | sim | `00000-000` ou `00000000`; devolve sempre `00000-000` | `"35930-000"` |

**Resposta `201` (`QuadraPublica`):**

```json
{
  "id": 1, "dono_id": 2, "nome": "Quadra Central",
  "descricao": "Quadra coberta com iluminação.", "tipo_piso": "saibro", "coberta": true,
  "limite_jogadores": 4, "preco_hora": 80.0,
  "endereco": "Rua das Flores", "numero": "100", "bairro": "Centro",
  "cidade": "João Monlevade", "estado": "MG", "cep": "35930-000",
  "ativa": true, "fotos": [],
  "criado_em": "2026-11-23T23:03:57.621568Z", "atualizado_em": "2026-11-23T23:03:57.621575Z"
}
```

**Erros:** `401 NAO_AUTENTICADO`, `403 ACESSO_NEGADO`, `422 VALIDACAO`.

Mensagens de validação mais comuns: `Campo obrigatório.` · `Máximo de 500 caracteres.` · `Deve ser maior que 0.` · `Use no máximo 2 casas decimais.` · `UF inválida. Use a sigla do estado, ex.: MG.` · `CEP inválido. Use o formato 00000-000.` · `Valor inválido. Opções: 'saibro', 'rapida', 'grama' ou 'sintetico'.`

### 6.6 `POST /quadras/{quadra_id}/fotos` ✅ — Enviar fotos

**Tarefa 12 · CT09.** Requer token do **dono da quadra** ou de um **administrador**. Corpo **`multipart/form-data`** com um ou mais arquivos no campo **`fotos`** (repita o campo para cada arquivo).

**Regras de validação** (o tipo é verificado pelo **conteúdo** do arquivo, não pela extensão):

| Regra | `code` da rejeição | Motivo devolvido |
|---|---|---|
| Tipos aceitos: JPEG, PNG, WebP | `TIPO_NAO_SUPORTADO` | Tipo de arquivo não suportado. Envie imagens JPEG, PNG ou WebP. |
| Tamanho máximo: **5 MB** por arquivo (`UPLOAD_MAX_BYTES`) | `ARQUIVO_MUITO_GRANDE` | O arquivo excede o tamanho máximo de 5 MB. |
| Arquivo não pode estar vazio | `ARQUIVO_VAZIO` | O arquivo está vazio. |
| Máximo de **10 fotos por quadra** (`FOTOS_MAX_POR_QUADRA`) | `LIMITE_FOTOS` | A quadra já atingiu o limite de 10 fotos. |

**Comportamento:** os arquivos válidos são salvos mesmo quando outros são rejeitados. Os rejeitados voltam em `rejeitadas`, que funciona como aviso para o usuário.

**Resposta `201`** (pelo menos uma foto aceita):

```json
{
  "fotos": [
    { "id": 1, "url": "/uploads/quadras/1/6434b98...png", "nome_arquivo": "frente.png",
      "tipo_arquivo": "image/png", "tamanho_bytes": 183204, "principal": true, "ordem": 0 }
  ],
  "rejeitadas": [
    { "nome_arquivo": "contrato.pdf", "code": "TIPO_NAO_SUPORTADO",
      "motivo": "Tipo de arquivo não suportado. Envie imagens JPEG, PNG ou WebP." }
  ]
}
```

**Resposta `422`** (nenhuma foto aceita): `code = FOTOS_REJEITADAS`, com a mesma lista `rejeitadas`.

- `url` é relativa ao servidor; monte a URL completa com o host da API (seção 1).
- A primeira foto de uma quadra vira a `principal` (capa). `ordem` começa em 0 e continua nos próximos envios.
- Outros erros: `401`, `403 ACESSO_NEGADO` (quadra de outro dono), `404 QUADRA_NAO_ENCONTRADA`, `422 VALIDACAO` (requisição sem arquivos: `campo = "fotos"`).

```dart
final req = http.MultipartRequest('POST', Uri.parse('$apiBaseUrl/quadras/$id/fotos'))
  ..headers['X-CSRF-Token'] = csrf; // web: o cookie vai sozinho. Fora do navegador: Authorization: Bearer
for (final f in arquivosSelecionados) {          // ex.: file_picker com withData: true
  req.files.add(http.MultipartFile.fromBytes('fotos', f.bytes!, filename: f.name));
}
final resp = await http.Response.fromStream(await req.send());
```

### 6.7 `DELETE /quadras/{quadra_id}/fotos/{foto_id}` ✅ — Remover foto

Requer token do dono da quadra ou de um administrador. Responde **`204`** sem corpo. Se a foto removida era a `principal`, a próxima (menor `ordem`) é promovida automaticamente.

Erros: `401`, `403 ACESSO_NEGADO`, `404 QUADRA_NAO_ENCONTRADA`, `404 FOTO_NAO_ENCONTRADA`.

### 6.8 `GET /quadras` ✅ — Buscar quadras

Público (sem token). Lista as quadras **ativas de donos ativos**, ordenadas por `nome`, paginadas. Atende a barra de busca da página inicial e a tela `/quadras` (tarefas 45 e 56 do front-end).

Parâmetros de consulta (todos opcionais):

| Parâmetro | Tipo | Regras | Exemplo |
|---|---|---|---|
| `cidade` | texto | até 100. Casa **por palavras**: cada palavra precisa aparecer no nome da cidade, em qualquer ordem. Não diferencia maiúsculas e **ignora acentos** (`joao monlevade` encontra "João Monlevade"). Espaços extras são ignorados. | `monlevade` |
| `tipo_piso` | enum `tipo_piso` | ver seção 5; omitir = qualquer tipo | `saibro` |
| `coberta` | boolean | `true` / `false`; omitir = todas | `true` |
| `pagina` | inteiro | ≥ 1, padrão 1 | `1` |
| `por_pagina` | inteiro | 1–100, padrão 20 | `20` |

Exemplo: `GET /quadras?cidade=monlevade&tipo_piso=saibro`

```json
200 {
  "itens": [
    {
      "id": 1, "nome": "Quadra Central", "tipo_piso": "saibro", "coberta": true,
      "limite_jogadores": 4, "preco_hora": 80.0, "bairro": "Centro",
      "cidade": "João Monlevade", "estado": "MG", "ativa": true,
      "foto_principal": "/uploads/quadras/1/abc.jpg"
    }
  ],
  "total": 1, "pagina": 1, "por_pagina": 20, "total_paginas": 1
}
```
`foto_principal` é `null` quando a quadra não tem fotos. Para exibir, use `http://localhost:8000` + o valor. A lista **não** traz a descrição, o endereço completo nem todas as fotos: busque o detalhe (6.9) ao abrir a quadra.

Erros: `422 VALIDACAO` (ex.: `tipo_piso` fora do enum, `por_pagina` acima de 100).

> Enquanto a pendência **P01** não for resolvida, o enum `TipoSuperficie` do Flutter (`dura`, `gramaSintetica`, `carpete`) gera `422` no filtro `tipo_piso`. Use os valores da seção 5.

### 6.9 `GET /quadras/{quadra_id}` ✅ — Detalhes da quadra

Público. Devolve a quadra completa no mesmo formato do `201` de `POST /quadras` (6.5): descrição, endereço, `cep`, `dono_id`, `ativa`, datas e **todas as fotos** (`fotos[]`, ordenadas por `ordem`, com a `principal` marcada).

- Quadra **inativa** ou de dono desativado responde `404` para quem não está logado e para outros donos. O **próprio dono** e o **administrador** a veem normalmente se enviarem o token.
- O token é opcional, mas, se for enviado e estiver inválido ou expirado, a resposta é `401 NAO_AUTENTICADO`, não a versão pública. Ao receber `401`, descarte o token e repita sem ele (ou mande para o login).

Erros: `404 QUADRA_NAO_ENCONTRADA`, `401 NAO_AUTENTICADO` (token inválido), `422 VALIDACAO` (`quadra_id` não numérico).

> A disponibilidade de horários fica em `GET /quadras/{id}/horarios` (6.11.2). A nota média das avaliações (tarefa 25) terá endpoint próprio; ver a seção 8.

### 6.10 `GET /quadras/minhas` ✅ — Quadras do dono autenticado

Requer token de **dono de quadra** (administrador recebe `403 ACESSO_NEGADO`). Mesmos parâmetros e mesmo formato de resposta de `GET /quadras` (6.8), mas lista **só as quadras do dono, inclusive as inativas** (veja `ativa` em cada item). Use na área do dono para listar as quadras e abrir o detalhe ou o envio de fotos (tarefa 35 do front-end).

Erros: `401`, `403 ACESSO_NEGADO`, `422 VALIDACAO`.

### 6.11 Horários da quadra ✅ — gerenciamento pelo dono (tarefa 20) e disponibilidade (tarefa 52)

Cada horário é um intervalo de **1 hora** (`DURACAO_SLOT_MINUTOS`) numa data, com status `disponivel`, `reservado` ou `bloqueado`. A listagem (6.11.2) é **pública** e mostra ao cliente os horários livres. As demais rotas exigem token do **dono da quadra** ou de um **administrador**: outro dono recebe `403 ACESSO_NEGADO`, e quadra inexistente dá `404 QUADRA_NAO_ENCONTRADA`.

Objeto **`HorarioPublico`**:

```json
{
  "id": 10, "quadra_id": 1, "data": "2026-12-07", "hora_inicio": "08:00", "hora_fim": "09:00",
  "preco": null, "preco_efetivo": 80.0, "status": "disponivel"
}
```
`preco` é o preço próprio do horário. Quando é `null`, vale o preço da quadra. **`preco_efetivo`** é o que o cliente paga; exiba sempre esse campo.

#### 6.11.1 `POST /quadras/{quadra_id}/horarios` — Gerar horários em lote

Para cada data do período cujo dia da semana esteja em `dias_semana`, cria horários consecutivos de 1 hora, da abertura até o fechamento. Uma sobra menor que 1 hora é descartada: por exemplo, de 08:00 a 10:45 são criados 08:00 e 09:00. Para criar **um único horário**, use a mesma data no início e no fim e um intervalo de 1 hora.

| Campo | Tipo | Obrigatório | Regras | Exemplo |
|---|---|---|---|---|
| `data_inicio` | data | sim | `AAAA-MM-DD`, hoje ou depois | `"2026-12-07"` |
| `data_fim` | data | sim | ≥ `data_inicio`; período de até **92 dias** | `"2026-12-31"` |
| `dias_semana` | lista de inteiros | não (padrão: todos) | **1 = segunda … 7 = domingo**, igual ao `DateTime.weekday` do Dart; repetições são ignoradas | `[1, 2, 3, 4, 5]` |
| `hora_abertura` | hora | sim | `HH:MM` | `"08:00"` |
| `hora_fechamento` | hora | sim | `HH:MM`, pelo menos 1 hora depois da abertura (no mesmo dia) | `"22:00"` |
| `preco` | número | não | > 0, até 2 casas. Omitir = usa o preço da quadra | `100` |

```json
201 {
  "criados": [ HorarioPublico, ... ],
  "ignorados": [
    { "data": "2026-12-07", "hora_inicio": "10:00", "hora_fim": "11:00",
      "code": "HORARIO_JA_CADASTRADO", "motivo": "Já existe um horário com este início." }
  ]
}
```
Horários que não podem ser criados **não impedem os outros**. Eles voltam em `ignorados`, com um destes `code`:

| `code` | Motivo |
|---|---|
| `HORARIO_JA_CADASTRADO` | Já existe um horário com este início. |
| `HORARIO_SOBREPOSTO` | Sobrepõe o horário HH:MM–HH:MM (ex.: já existe 10:30–11:30). |
| `HORARIO_PASSADO` | O horário já passou (só ocorre para a data de hoje). |

Por isso a geração pode ser **repetida sem duplicar** nada. `criados` pode até vir vazio, se tudo já existia.

Erros:
- `422 VALIDACAO`: data no passado, período invertido ou maior que 92 dias, fechamento menos de 1 hora depois da abertura, dia da semana fora de 1–7 ou preço ≤ 0.
- `422 PERIODO_SEM_DATAS`: o período não contém nenhum dos dias escolhidos.

#### 6.11.2 `GET /quadras/{quadra_id}/horarios` — Disponibilidade (público) ou horários (dono)

Parâmetros: `data_inicio` (padrão: hoje), `data_fim` (padrão: `data_inicio` + 6 dias; período de até 92 dias) e `status` (opcional). Devolve uma **lista** de `HorarioPublico`, ordenada por data e hora. Não é paginada, porque o período já limita o tamanho.

O conteúdo depende de quem pergunta:

| Quem | O que vem |
|---|---|
| **Público**: sem login, ou logado sem ser dono desta quadra | Só horários **`disponivel`** que **ainda não começaram**. É a disponibilidade para o cliente escolher e reservar |
| **Dono da quadra ou administrador** | Todos os status (`disponivel`, `reservado`, `bloqueado`), inclusive os que já passaram |

- Quadra inativa, ou de dono inativo, dá `404 QUADRA_NAO_ENCONTRADA` para o público. O dono e o administrador continuam vendo os horários dela.
- O público pode enviar `status=disponivel`. Com `reservado` ou `bloqueado`, a resposta é `403 ACESSO_NEGADO`.
- Um horário que começa agora (ex.: 14:00 às 14:00) já não aparece para o público.

Erros: `404 QUADRA_NAO_ENCONTRADA`, `403 ACESSO_NEGADO` (público filtrando status internos), `401 NAO_AUTENTICADO` (token enviado, mas inválido), `422 PERIODO_INVALIDO`, `422 VALIDACAO` (data ou status mal formatados).

> **Conflitos na reserva (CT02, RNF01).** A disponibilidade é uma fotografia do momento: entre a consulta e a reserva, outro cliente pode reservar o mesmo horário. A criação da reserva (tarefa 14) revalida e trava o horário no banco. Se ele não estiver mais livre, a resposta será `409 HORARIO_INDISPONIVEL`; se já tiver começado, `409 HORARIO_PASSADO`. Nesses casos, recarregue a disponibilidade e peça outro horário.

#### 6.11.3 `PATCH /quadras/{quadra_id}/horarios/{horario_id}` — Bloquear, desbloquear ou mudar o preço

Envie **só o que muda**:

| Campo | Tipo | Regras |
|---|---|---|
| `status` | enum `StatusHorarioAlteravel` | `disponivel` ou `bloqueado`. `reservado` é definido só pelas reservas. Omitir mantém o status; `null` é rejeitado |
| `preco` | número ou `null` | > 0; `null` volta a usar o preço da quadra |

Resposta `200` com o `HorarioPublico` atualizado.

Erros:
- `409 HORARIO_RESERVADO`: horários reservados são preservados (CT12).
- `409 HORARIO_PASSADO`.
- `404 HORARIO_NAO_ENCONTRADO`.
- `422 VALIDACAO`: corpo vazio, `status` inválido ou campo desconhecido.

#### 6.11.4 `DELETE /quadras/{quadra_id}/horarios/{horario_id}` — Remover horário

Remove um horário **livre e futuro**. Responde `204`.

Erros:
- `409 HORARIO_RESERVADO`.
- `409 HORARIO_PASSADO`.
- `409 HORARIO_COM_HISTORICO`: o horário já teve reservas, canceladas ou expiradas, e o histórico precisa ser mantido. Nesse caso, **bloqueie** o horário com o PATCH.
- `404 HORARIO_NAO_ENCONTRADO`.

## 7. Fluxos das telas

### 7.1 Cadastro de quadra (tarefas 32 e 51 do front-end)

```
[Formulário preenchido] → POST /quadras
    ├─ 422 VALIDACAO → mostrar erros[] nos campos; parar
    └─ 201 → guardar id
         └─ havia fotos selecionadas? → POST /quadras/{id}/fotos
               ├─ 201 → sucesso; se rejeitadas[] não estiver vazio, avisar quais fotos foram recusadas e por quê
               └─ 422 FOTOS_REJEITADAS → a quadra foi criada sem fotos; mostrar motivos e permitir novo envio
```

Validações recomendadas também na interface, para feedback imediato e espelhando o backend:
- contador e limite de **500** caracteres na descrição (`maxLength: 500`) — CT10;
- seletor de arquivos restrito a `jpg/jpeg/png/webp`, com aviso para arquivos acima de 5 MB;
- máscara de CEP (`00000-000`) e lista de UFs.

### 7.2 Mapeamento de campos — formulário de cadastro de quadra

| Campo na tela (sugestão) | Widget sugerido | Campo da API |
|---|---|---|
| Nome da quadra | `TextFormField` (máx. 150) | `nome` |
| Descrição | `TextFormField` multilinha, `maxLength: 500` | `descricao` |
| Tipo de piso | `DropdownButtonFormField<TipoPiso>` | `tipo_piso` (`TipoPiso.api`) |
| Quadra coberta | `Switch` / `Checkbox` | `coberta` |
| Capacidade máxima de jogadores | `TextFormField` numérico | `limite_jogadores` |
| Valor do aluguel (R$/hora) | `TextFormField` monetário | `preco_hora` |
| Endereço (rua) | `TextFormField` | `endereco` |
| Número | `TextFormField` (opcional) | `numero` |
| Bairro | `TextFormField` | `bairro` |
| Cidade | `TextFormField` | `cidade` |
| Estado | `DropdownButtonFormField` com as UFs | `estado` |
| CEP | `TextFormField` com máscara | `cep` |
| Fotos | seletor múltiplo de imagens | enviadas depois, em `POST /quadras/{id}/fotos` (campo `fotos`) |

### 7.3 Cadastro de dono de quadra (tela `/cadastro-login`)

```
[Login] → "Cadastre-se aqui" → [/cadastro-login preenchido] → POST /auth/registro
    ├─ 422 VALIDACAO → mostrar erros[] nos campos; parar
    ├─ 409 EMAIL_JA_CADASTRADO → erro no e-mail + link "Já tem conta? Entrar"
    └─ 201 → POST /auth/login com o mesmo e-mail e senha → guardar o X-CSRF-Token → área do dono
            (ou: mensagem de sucesso e voltar para /login)
```

Validações recomendadas também na interface: e-mail com `TextInputType.emailAddress`, senha com pelo menos 8 caracteres, confirmação de senha igual à senha e máscara de telefone opcional.

### 7.4 Mapeamento de campos — formulário de cadastro de dono

| Campo na tela (sugestão) | Widget sugerido | Campo da API |
|---|---|---|
| Nome completo | `TextFormField` (máx. 150) | `nome` |
| E-mail | `TextFormField`, `keyboardType: emailAddress` | `email` |
| Telefone (opcional) | `TextFormField` com máscara `(00) 00000-0000` | `telefone` |
| Senha | `TextFormField`, `obscureText`, mín. 8 | `senha` |
| Confirmar senha | `TextFormField`, `obscureText` | *(só na tela, não é enviado)* |

### 7.5 Busca e detalhes de quadras (página inicial → `/quadras`, tarefas 45 e 56)

```
[Barra de busca: cidade + superfície] → "BUSCAR QUADRAS"
    → GET /quadras?cidade=<texto>&tipo_piso=<valor ou omitir>
        ├─ 422 VALIDACAO → valor de filtro inválido (ver P01)
        └─ 200 → navegar para /quadras com a página de resultados
              ├─ itens vazio → "Nenhuma quadra encontrada."
              ├─ pagina < total_paginas → botão "carregar mais" (pagina + 1)
              └─ tocar num card → GET /quadras/{id} → tela de detalhes (fotos, descrição, endereço, preço)
```

Hoje a barra de busca filtra uma lista fixa no próprio Flutter, normalizando acentos com `normalizarCidade`. Com a API, **envie o texto digitado como está**: a busca por palavras, sem diferenciar maiúsculas nem acentos, já é feita no backend. "Qualquer tipo" no seletor de superfície = **não enviar** `tipo_piso`.

### 7.6 Mapeamento de campos — card de resultado e detalhes

| Elemento na tela (sugestão) | Campo da API |
|---|---|
| Imagem do card | `foto_principal` (lista) ou `fotos[]` (detalhe); `null` → imagem padrão |
| Nome | `nome` |
| Superfície | `tipo_piso` → rótulo da seção 5 |
| Coberta / descoberta | `coberta` |
| Preço (R$/hora) | `preco_hora` (número) |
| Capacidade | `limite_jogadores` |
| Localização no card | `bairro`, `cidade` - `estado` |
| Endereço completo (detalhe) | `endereco`, `numero`, `bairro`, `cidade`, `estado`, `cep` |
| Descrição (detalhe) | `descricao` |

### 7.7 Gerenciamento de horários (área do dono)

```
[Minhas quadras] → escolher quadra → GET /quadras/{id}/horarios?data_inicio=..&data_fim=..
    → grade (dias × horas) colorida por status

[Gerar horários: período, dias da semana, abertura, fechamento, preço opcional]
    → POST /quadras/{id}/horarios
        ├─ 422 → erros nos campos / PERIODO_SEM_DATAS
        └─ 201 → "N horários criados"; se ignorados[] não estiver vazio: "M ignorados" (listar motivos)
              → recarregar a grade

[Tocar num horário]
    ├─ disponivel → ações: Bloquear (PATCH status=bloqueado), Alterar preço (PATCH preco), Remover (DELETE)
    ├─ bloqueado  → ações: Desbloquear (PATCH status=disponivel), Remover (DELETE)
    └─ reservado ou passado → sem ações (o backend responde 409)
         DELETE com 409 HORARIO_COM_HISTORICO → oferecer "Bloquear" no lugar
```

### 7.8 Mapeamento de campos — formulário de geração de horários

| Campo na tela (sugestão) | Widget sugerido | Campo da API |
|---|---|---|
| Período | `showDateRangePicker` (início ≥ hoje, até 92 dias) | `data_inicio`, `data_fim` (`AAAA-MM-DD`) |
| Dias da semana | `FilterChip` de Seg a Dom | `dias_semana` (`DateTime.monday` = 1 … `DateTime.sunday` = 7) |
| Abre às | `showTimePicker` | `hora_abertura` (`HH:MM`) |
| Fecha às | `showTimePicker` | `hora_fechamento` (`HH:MM`) |
| Preço por hora (opcional) | `TextFormField` monetário; vazio = preço da quadra | `preco` |

### 7.9 Disponibilidade para o cliente (detalhes da quadra → reserva)

```
[Detalhes da quadra] → GET /quadras/{id}/horarios?data_inicio=..&data_fim=..   (sem login)
    → agrupar por data (ex.: abas ou calendário dos próximos 7 dias)
    → cada horário: "HH:MM–HH:MM · R$ preco_efetivo"
    ├─ lista vazia → "Sem horários disponíveis neste período"
    └─ tocar num horário → formulário da reserva (tarefa 14) com o id do horário
           └─ 409 HORARIO_INDISPONIVEL / HORARIO_PASSADO → avisar, recarregar a lista
```

## 8. Endpoints planejados

Ainda **não disponíveis**. Os caminhos são indicativos e podem mudar; este documento será atualizado quando cada um for implementado.

| Tarefa (EAP) | Funcionalidade | Endpoint previsto |
|---|---|---|
| 14 | Criação da reserva (cliente sem login) | `POST /reservas` |
| 15, 53 | Pagamento simulado e expiração | `POST /reservas/{codigo}/pagamento` |
| 16, 54 | Cancelamento e estorno | `POST /reservas/{codigo}/cancelamento` |
| 18, 49 | Consulta de reservas | `GET /reservas/{codigo}`, `GET /quadras/{id}/reservas` |
| 19, 21, 55 | Gestão de usuários (admin) | `GET /usuarios`, `PATCH /usuarios/{id}/status` |
| 24, 25 | Avaliações | `POST /reservas/{codigo}/avaliacao`, `GET /quadras/{id}/avaliacoes` |

## Histórico de alterações

| Versão | Data | Alteração |
|---|---|---|
| 0.8.0 | 27/11/2026 | Disponibilidade pública (tarefa 52): `GET /quadras/{id}/horarios` passa a aceitar o cliente sem login e mostra só horários disponíveis que ainda não começaram; o dono e o administrador continuam vendo todos (6.11.2). Validação de conflitos para a reserva, com o novo código `409 HORARIO_INDISPONIVEL` (CT02). Fluxo da disponibilidade para o cliente (7.9). |
| 0.7.0 | 27/11/2026 | Sessão por cookie HttpOnly `muzzi_session` com proteção CSRF (front web), convivendo com o `Authorization: Bearer` (Swagger, testes). O login continua `200` com `access_token` e passa a gravar o cookie e devolver `X-CSRF-Token`. Novas rotas `GET /auth/csrf` e `POST /auth/logout` (6.3.1 e 6.3.2). Novos códigos `403 CSRF_INVALIDO` e `403 ORIGEM_NAO_PERMITIDA`. Front pelo compose da raiz em `localhost:8080`, com `/api/` e `/uploads/` repassados pelo nginx. |
| 0.6.0 | 27/11/2026 | Gerenciamento de horários (tarefa 20): `POST`, `GET`, `PATCH` e `DELETE` em `/quadras/{id}/horarios` (seção 6.11), com geração em lote, horários ignorados com motivo e preservação dos reservados (CT12); no `PATCH`, `status` é o enum `StatusHorarioAlteravel`. Convenção de data e hora dos horários (local, `HH:MM`). Novos códigos de erro `HORARIO_*`, `PERIODO_SEM_DATAS` e `PERIODO_INVALIDO`. Fluxo e mapeamento da tela de horários (7.7 e 7.8). |
| 0.5.0 | 27/11/2026 | **Mudança incompatível:** a URL base passa de `/api/v1` para `/api`, sem versão no caminho (ex.: `POST /api/auth/login`). |
| 0.4.1 | 26/11/2026 | Correção: requisição sem token agora responde `401` no formato padrão, com `code = NAO_AUTENTICADO` (antes vinha `{"detail": "Not authenticated"}`, sem `code`). Erros do próprio framework (endereço inexistente, método não permitido) também saem com `code`. Novo código `405 METODO_NAO_PERMITIDO`. |
| 0.4.0 | 25/11/2026 | Consulta de quadras (tarefa 13): `GET /quadras` (busca pública por cidade, tipo de piso e coberta, paginada), `GET /quadras/{id}` (detalhe público; inativa só para o dono e o administrador) e `GET /quadras/minhas` (quadras do dono). Convenção de listagens paginadas. Fluxo e mapeamento da busca (7.5 e 7.6). |
| 0.3.0 | 24/11/2026 | Cadastro público de dono de quadra (`POST /auth/registro`, pendência P03), com o erro `409 EMAIL_JA_CADASTRADO`. Seções 6.4 a 6.6 renumeradas para 6.5 a 6.7. Fluxo e mapeamento da tela `/cadastro-login` (7.3 e 7.4). |
| 0.2.0 | 23/11/2026 | Cadastro de quadras (`POST /quadras`) e envio/remoção de fotos (tarefa 12). Padronização dos erros de validação (`code = VALIDACAO` com `erros[]` em português). Datas passam a sair em UTC com `Z`; valores monetários como número. |
| 0.1.0 | 22/11/2026 | Primeira versão: `GET /health`, `POST /auth/login`, `GET /auth/me`, formato de erro `{detail, code}`. |
