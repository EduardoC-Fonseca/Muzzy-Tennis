# Muzzi Tennis — Pendências

Decisões em aberto, divergências entre artefatos e definições que faltam para concluir tarefas da EAP. A referência são os artefatos de gerenciamento (Documento de Visão, Cronograma/EAP, Riscos e Modelo de Dados). O `README.md` da raiz está desatualizado e não serve de base.

Ao resolver um item, registre a decisão e a data e mova-o para **Resolvidas**.

**Legenda de prioridade:** 🔴 bloqueia uma tarefa próxima · 🟡 precisa estar resolvido antes da entrega · ⚪ ajuste de documentação

## Abertas

### P01 — Ajustar os tipos de piso do front-end ao modelo de dados 🔴

- **Origem:** decisão D4 em [`db/modelo_dados.md`](db/modelo_dados.md).
- **Situação:** o modelo de dados e o backend usam `saibro`, `rapida`, `grama`, `sintetico` no enum `tipo_piso`. O Flutter ([`frontend/lib/models/tipo_superficie.dart`](../frontend/lib/models/tipo_superficie.dart)) usa `saibro`, `dura`, `gramaSintetica`, `carpete`.
- **Ação:** atualizar o enum do Flutter para os valores do modelo de dados. O backend rejeita qualquer valor fora do enum, então o cadastro e a busca de quadras falham enquanto isso não for feito.
- **Responsáveis:** Front-end, com apoio do Backend (risco R4).
- **Bloqueia:** a integração das tarefas 51 (cadastro) e 56 (consulta) com a API.

### P02 — Sincronizar o diagrama no dbdiagram.io ⚪

- **Situação:** o PDF [`db/modelo_dados.pdf`](db/modelo_dados.pdf) foi editado diretamente para refletir D1, D2 e D6. O projeto original no dbdiagram.io continua com a versão antiga.
- **Ação:** aplicar as mesmas mudanças no dbdiagram.io, para que uma nova exportação não desfaça as correções:
  - remover o NN de `usuarios.senha_hash`;
  - trocar o tipo de `usuarios.status` para `boolean`;
  - remover os enums `status_usuario` e `quem_cancelou`.

## Resolvidas

| ID | Decisão | Impacto na implementação | Data |
|---|---|---|---|
| D1 | O cliente não faz login: é gravado em `usuarios` sem senha (`senha_hash` anulável). | Modelo `Usuario`; a reserva cria ou reutiliza o cliente pelo e-mail. | 21/11/2026 |
| D2 | Enum `quem_cancelou` descartado: `cancelado_por_id` identifica quem cancelou e nulo significa o sistema. | Modelo `Cancelamento`. | 21/11/2026 |
| D6 | `usuarios.status` passa a ser boolean (`true` = ativo). | Modelo `Usuario`; enum `status_usuario` removido. | 22/11/2026 |
| Identificação do cliente | Segue o modelo de dados: `nome` e `email` obrigatórios (o e-mail é único e identifica o cliente), `telefone` opcional. | Tarefa 14: schema da reserva. Tarefas 18/49: consulta pelo código da reserva. | 22/11/2026 |
| Pagamento | **Pagamento simulado**, sem provedor externo nesta entrega. Fica isolado em um serviço que pode ser trocado por um provedor real depois. | Tarefas 15, 53 e 54. | 22/11/2026 |
| Estorno | Cancelamento feito com pelo menos 24 horas de antecedência devolve **100%** do valor pago. Com menos de 24 horas, o cancelamento é bloqueado (CT06). | Tarefas 16 e 54. Configuração `ESTORNO_PERCENTUAL_DENTRO_PRAZO`. | 22/11/2026 |
| Validação de fotos (CT09) | Aceitar apenas tipos de arquivo suportados (imagens JPEG, PNG e WebP, até o tamanho máximo). Um arquivo fora da regra é rejeitado e o endpoint devolve um aviso com o motivo. Não há moderação de conteúdo. | Tarefa 12: implementado (verificação pela assinatura do arquivo, 5 MB, até 10 fotos por quadra). | 22/11/2026 |
| Notificação ao dono (CT14) | O dono da quadra recebe um **aviso por e-mail** quando uma reserva é cancelada. | Tarefa 16: serviço de e-mail (SMTP configurável; em desenvolvimento, saída no log). | 22/11/2026 |
| Regras de negócio adicionais | Continuam valendo: horários (slots) de **1 hora** e no máximo **2 reservas por dia por cliente**. | Tarefas 20/52 (slots) e 14 (limite diário). Configurações `DURACAO_SLOT_MINUTOS` e `LIMITE_RESERVAS_DIA_CLIENTE`. | 22/11/2026 |
| Atualizar o PDF do modelo de dados | PDF editado com D1, D2 e D6. | Falta só sincronizar o dbdiagram.io (P02). | 22/11/2026 |
