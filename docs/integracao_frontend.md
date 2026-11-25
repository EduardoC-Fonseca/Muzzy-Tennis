# Muzzi Tennis — Contrato de Integração Front-end ↔ Backend

Contrato da API REST consumida pelo front-end Flutter: convenções, autenticação, formato de erros, enums, endpoints e o mapeamento dos campos das telas. Mitiga o risco **R4** (falhas na integração entre front-end e backend) de [`gerenciamento/documento_riscos.md`](gerenciamento/documento_riscos.md).

> **Regra de manutenção:** este documento é atualizado **no mesmo commit** de qualquer mudança no backend que afete a integração: endpoint novo ou alterado, campo, regra de validação, código de erro ou enum. Cada mudança entra no [Histórico de alterações](#histórico-de-alterações).
>
> A referência executável é o OpenAPI gerado pela API (`/docs` e `/openapi.json`). Se houver divergência entre ele e este documento, o código vale e o documento deve ser corrigido.

**Versão do contrato:** 0.3.0 · **Última atualização:** 24/11/2026

---

## 1. Ambiente

| Item | Valor (desenvolvimento) |
|---|---|
| URL base da API | `http://localhost:8000/api/v1` |
| Documentação interativa (Swagger) | `http://localhost:8000/docs` |
| Especificação OpenAPI | `http://localhost:8000/openapi.json` |
| Arquivos enviados (fotos) | `http://localhost:8000` + campo `url` (ex.: `http://localhost:8000/uploads/quadras/1/abc.jpg`) |
| CORS | Origens liberadas por `CORS_ORIGINS` no `.env` do backend (padrão: `localhost:3000`, `localhost:8080`, `127.0.0.1:8080`) |

> **Flutter web:** rode com uma porta fixa liberada no CORS, por exemplo `flutter run -d chrome --web-port 8080`. Para usar outra porta, inclua a origem em `CORS_ORIGINS`.

Recomendação: centralizar a URL base num único lugar do app (ex.: `const apiBaseUrl = String.fromEnvironment('API_URL', defaultValue: 'http://localhost:8000/api/v1');`).

## 2. Convenções

| Assunto | Regra |
|---|---|
| Formato | JSON UTF-8 (`Content-Type: application/json`), exceto o login (form-urlencoded) e o envio de fotos (multipart). |
| Nomes de campos | `snake_case`, iguais ao [modelo de dados](db/modelo_dados.md). |
| IDs | Inteiros. |
| Datas e horas | ISO 8601 em **UTC** com sufixo `Z` (ex.: `2026-11-23T23:03:57.621568Z`). Converta para o horário local na exibição (`DateTime.parse(s).toLocal()`). |
| Valores monetários | Na resposta, sempre **número** (ex.: `95.5`). Na requisição, aceita número ou texto (`80`, `"80.00"`), com no máximo 2 casas decimais. |
| Enums | Texto minúsculo, exatamente como na [seção 5](#5-enums). Qualquer outro valor é rejeitado. |
| Campos opcionais | Podem ser omitidos ou enviados como `null`. Na resposta, o campo sempre aparece (com `null` quando vazio). |
| Campos desconhecidos | Nos corpos de criação, campos fora do contrato são **rejeitados** (422), o que evita erros de digitação silenciosos. |
| Espaços | O backend remove espaços no início e no fim dos textos. Um texto só de espaços conta como vazio. |

## 3. Autenticação

| Perfil | Faz login? | Como acessa |
|---|---|---|
| `cliente` | **Não** | Reserva informando os dados de identificação (próximas tarefas). |
| `dono_quadra` | Sim | Cria a própria conta em `POST /auth/registro` (ver 6.4) e depois faz login. Token JWT. |
| `administrador` | Sim | Conta criada só pela equipe, por script (não há cadastro público). Token JWT. |

### Fluxo

1. `POST /auth/login` com `username` (e-mail) e `password` em **form-urlencoded** (padrão OAuth2), não JSON.
2. Guarde o `access_token` e envie em toda rota protegida: `Authorization: Bearer <token>`.
3. O token expira em **60 minutos** (`ACCESS_TOKEN_EXPIRE_MINUTES`). Ao receber `401`, mande o usuário para o login.
4. Conta desativada pelo administrador recebe `403` com `code = USUARIO_INATIVO`, **mesmo com um token ainda válido** (CT17). Mostre a mensagem e encerre a sessão.

```dart
final resp = await http.post(
  Uri.parse('$apiBaseUrl/auth/login'),
  body: {'username': email, 'password': senha}, // Map → form-urlencoded
);
final token = jsonDecode(resp.body)['access_token'];
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
| 401 | `NAO_AUTENTICADO` | Sem token, token inválido ou expirado | Redirecionar para o login |
| 401 | `CREDENCIAIS_INVALIDAS` | Login com e-mail ou senha errados | Mensagem no formulário de login |
| 403 | `USUARIO_INATIVO` | Conta desativada (login ou token válido) | Mensagem e logout |
| 403 | `ACESSO_NEGADO` | Perfil sem permissão, ou recurso de outro proprietário | Mensagem "sem permissão" |
| 404 | `NAO_ENCONTRADO` | Recurso genérico inexistente | — |
| 404 | `QUADRA_NAO_ENCONTRADA` | Quadra inexistente | — |
| 404 | `FOTO_NAO_ENCONTRADA` | Foto inexistente ou de outra quadra | — |
| 409 | `EMAIL_JA_CADASTRADO` | Cadastro de dono com e-mail já usado por outra conta (ver 6.4) | Erro no campo e-mail, com link para o login |
| 422 | `VALIDACAO` | Campos inválidos ou ausentes (ver 4.1) | Erro em cada campo |
| 422 | `FOTOS_REJEITADAS` | Nenhuma foto do envio foi aceita (ver 6.6) | Listar `rejeitadas[].motivo` |

## 5. Enums

| Enum | Valores | Rótulo sugerido na tela |
|---|---|---|
| `papel_usuario` | `cliente`, `dono_quadra`, `administrador` | Cliente, Dono de quadra, Administrador |
| `tipo_piso` | `saibro`, `rapida`, `grama`, `sintetico` | Saibro, Rápida, Grama, Sintética |
| `status_horario` | `disponivel`, `reservado`, `bloqueado` | *(próximas tarefas)* |
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
Erros: `401 CREDENCIAIS_INVALIDAS`, `403 USUARIO_INATIVO`, `422 VALIDACAO`.

### 6.3 `GET /auth/me` ✅

Requer token. Devolve o usuário autenticado (`UsuarioPublico`):

```json
200 {
  "id": 1, "nome": "Admin Dev", "email": "admin@muzzi.local", "telefone": null,
  "papel": "administrador", "status": true, "criado_em": "2026-11-22T02:02:20Z"
}
```
Use `papel` para decidir quais telas exibir.

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
  ..headers['Authorization'] = 'Bearer $token';
for (final f in arquivosSelecionados) {          // ex.: file_picker com withData: true
  req.files.add(http.MultipartFile.fromBytes('fotos', f.bytes!, filename: f.name));
}
final resp = await http.Response.fromStream(await req.send());
```

### 6.7 `DELETE /quadras/{quadra_id}/fotos/{foto_id}` ✅ — Remover foto

Requer token do dono da quadra ou de um administrador. Responde **`204`** sem corpo. Se a foto removida era a `principal`, a próxima (menor `ordem`) é promovida automaticamente.

Erros: `401`, `403 ACESSO_NEGADO`, `404 QUADRA_NAO_ENCONTRADA`, `404 FOTO_NAO_ENCONTRADA`.

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
    └─ 201 → POST /auth/login com o mesmo e-mail e senha → guardar token → área do dono
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

## 8. Endpoints planejados

Ainda **não disponíveis**. Os caminhos são indicativos e podem mudar; este documento será atualizado quando cada um for implementado.

| Tarefa (EAP) | Funcionalidade | Endpoint previsto |
|---|---|---|
| 13 | Consulta dos dados da quadra | `GET /quadras`, `GET /quadras/{id}` |
| 20 | Gerenciamento de datas/horários | `POST/PUT/DELETE /quadras/{id}/horarios` |
| 52 | Consulta de disponibilidade | `GET /quadras/{id}/horarios` |
| 14 | Criação da reserva (cliente sem login) | `POST /reservas` |
| 15, 53 | Pagamento simulado e expiração | `POST /reservas/{codigo}/pagamento` |
| 16, 54 | Cancelamento e estorno | `POST /reservas/{codigo}/cancelamento` |
| 18, 49 | Consulta de reservas | `GET /reservas/{codigo}`, `GET /quadras/{id}/reservas` |
| 19, 21, 55 | Gestão de usuários (admin) | `GET /usuarios`, `PATCH /usuarios/{id}/status` |
| 24, 25 | Avaliações | `POST /reservas/{codigo}/avaliacao`, `GET /quadras/{id}/avaliacoes` |

## Histórico de alterações

| Versão | Data | Alteração |
|---|---|---|
| 0.3.0 | 24/11/2026 | Cadastro público de dono de quadra (`POST /auth/registro`, pendência P03), com o erro `409 EMAIL_JA_CADASTRADO`. Seções 6.4 a 6.6 renumeradas para 6.5 a 6.7. Fluxo e mapeamento da tela `/cadastro-login` (7.3 e 7.4). |
| 0.2.0 | 23/11/2026 | Cadastro de quadras (`POST /quadras`) e envio/remoção de fotos (tarefa 12). Padronização dos erros de validação (`code = VALIDACAO` com `erros[]` em português). Datas passam a sair em UTC com `Z`; valores monetários como número. |
| 0.1.0 | 22/11/2026 | Primeira versão: `GET /health`, `POST /auth/login`, `GET /auth/me`, formato de erro `{detail, code}`. |
