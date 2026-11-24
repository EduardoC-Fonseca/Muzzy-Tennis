# Muzzi Tennis — Planejamento do Projeto (Cronograma / EAP)

> Convertido de [`cronograma.pdf`](cronograma.pdf) (gerado em 29/10/2026 a partir de [`cronograma_grafico.gan`](cronograma_grafico.gan), GanttProject). O PDF/`.gan` continuam sendo a fonte oficial.
>
> A coluna **Dependências** foi extraída do `.gan` (todas do tipo término→início, exceto onde indicado). A coluna **Status backend** é acompanhamento do desenvolvimento e não faz parte do documento original.

| | |
|---|---|
| **Gerentes de projeto** | Emerson, Maria Clara |
| **Período** | 01/09/2026 – 26/11/2026 |
| **Tarefas** | 54 |
| **Recursos** | 5 |

## Recursos

| Nome | Função | Alocação principal |
|---|---|---|
| Emerson | Gerente de Projeto | Plano, histórias, identidade visual, cronograma, requisitos, cenários de teste |
| Maria Clara | Gerente de Projeto | Plano, histórias, cronograma, requisitos, cenários de teste, protótipo |
| Eduardo | Indefinida | Front-end, orçamento, benchmarking |
| Hálisson | Indefinida | **Backend, Banco de dados** |
| Davi | Indefinida | — |

## Planejamento

| Tarefa | Início | Fim |
|---|---|---|
| Plano do projeto | 01/09/2026 | 27/10/2026 |
| Construção de benchmarking | 07/09/2026 | 07/09/2026 |
| Cronograma | 19/10/2026 | 19/10/2026 |
| Orçamento | 12/10/2026 | 12/10/2026 |
| Documento de requisitos | 07/09/2026 | 11/09/2026 |
| Histórias de usuário | 15/09/2026 | 17/09/2026 |
| Cenários de testes | 17/09/2026 | 18/09/2026 |
| Construção da identidade visual | 16/09/2026 | 16/09/2026 |
| Protótipo das interfaces | 05/10/2026 | 05/10/2026 |

## Banco de dados (02/11/2026)

| ID | Tarefa | Início | Fim | Dependências | Status backend |
|---|---|---|---|---|---|
| 9 | Modelar entidades e relacionamentos | 02/11/2026 | 02/11/2026 | — | ✅ modelos SQLAlchemy |
| 47 | Criação/configuração do banco de dados | 02/11/2026 | 02/11/2026 | 9 (início→início) | ✅ MySQL + Alembic |

## Backend (03/11/2026 – 16/11/2026)

| ID | Tarefa | Início | Fim | Dependências | Status backend |
|---|---|---|---|---|---|
| 12 | Implementar cadastro de quadras, incluindo validação dos campos obrigatórios, envio e validação de fotos e limite da descrição | 03/11 | 03/11 | 47 | ✅ `POST /quadras`, fotos |
| 13 | Implementar consulta dos dados da quadra | 03/11 | 04/11 | 47 | ⬜ |
| 20 | Implementar gerenciamento da disponibilidade de datas e horários | 05/11 | 05/11 | 13 | ⬜ |
| 52 | Implementar consulta de disponibilidade e validação de conflitos de horário | 06/11 | 06/11 | 20 | ⬜ |
| 14 | Implementar criação da reserva e validação do limite de jogadores | 09/11 | 10/11 | 52 | ⬜ |
| 15 | Implementar controle do pagamento/garantia e atualização do status da reserva | 11/11 | 11/11 | 14 | ⬜ |
| 53 | Implementar expiração automática da reserva após uma hora sem pagamento e liberação do horário | 12/11 | 12/11 | 15 | ⬜ |
| 16 | Implementar cancelamento da reserva e aplicação da regra de 24 horas | 12/11 | 13/11 | 15 | ⬜ |
| 54 | Implementar controle de estorno conforme as regras de cancelamento | 16/11 | 16/11 | 16 | ⬜ |
| 18 | Implementar consulta das reservas pelo dono da quadra e pelo cliente (novo) | 11/11 | 13/11 | 14 | ⬜ |
| 49 | Implementar consulta das reservas pelo código da reserva | 03/11 | 03/11 | 47 | ⬜ |
| 19 | Implementar listagem e pesquisa de usuários, retornando nome, e-mail, papel e status | 03/11 | 03/11 | 47 | ⬜ |
| 21 | Implementar desativação e reativação de usuários, incluindo bloqueio de acesso para usuários inativos | 04/11 | 05/11 | 19 | ⬜ |
| 55 | Implementar controle de acesso para restringir o gerenciamento de usuários ao administrador | 04/11 | 04/11 | 19 | ⬜ |
| 24 | Implementar criação da avaliação vinculada à reserva e à quadra, incluindo validação da reserva concluída, nota de 1 a 5 estrelas e comentário de até 300 caracteres | 11/11 | 12/11 | 14 | ⬜ |
| 25 | Implementar consulta das avaliações e cálculo/atualização da nota média da quadra | 13/11 | 13/11 | 24 | ⬜ |

## Front-end (06/10/2026 – 18/11/2026)

| ID | Tarefa | Início | Fim | Depende de (backend) |
|---|---|---|---|---|
| 45 | Criar tela de consulta e detalhes das quadras | 05/11 | 05/11 | 8, 13 |
| 56 | Integrar consulta das quadras e exibir disponibilidade de datas e horários, incluindo indicação de horários indisponíveis | 06/11 | 06/11 | 45 |
| 28 | Criar formulário de reserva com quantidade de jogadores e validações de interface | 06/11 | 06/11 | 45 |
| 57 | Integrar criação da reserva e exibir mensagens de erro para limite de jogadores ou horário ocupado | 11/11 | 12/11 | 14, 28 |
| 58 | Criar interface de pagamento/garantia e exibir situação da reserva/pagamento, incluindo expiração | 13/11 | 13/11 | 53, 57 |
| 29 | Criar tela de consulta de reservas pelo usuário | 06/10 | 06/10 | 8 |
| 59 | Integrar consulta das reservas do usuário e ação de cancelamento, exibindo a regra de 24 horas e informações sobre estorno | 17/11 | 18/11 | 18, 29, 54 |
| 32 | Criar formulário de cadastro da quadra com dados, envio de fotos, validação dos campos obrigatórios e limite da descrição | 06/10 | 08/10 | 8 |
| 51 | Integrar cadastro à API e exibir mensagens de sucesso/erro | 04/11 | 04/11 | 12, 32 |
| 34 | Criar tela de consulta das reservas da quadra para o admin da quadra | 06/10 | 06/10 | 8 |
| 35 | Integrar consulta e exibição dos dados da quadra | 05/11 | 05/11 | 13 |
| 60 | Criar interface para gerenciamento de datas/horários disponíveis e integrar à API | 09/11 | 11/11 | 35, 52 |
| 61 | Integrar consultas das reservas à API e exibir seus clientes, data e horário | 16/11 | 16/11 | 18, 34 |
| 36 | Criar tela de listagem de usuários com nome, e-mail, papel e status, incluindo pesquisa | 04/11 | 04/11 | 8, 19 |
| 62 | Integrar listagem e pesquisa à API de usuários | 05/11 | 05/11 | 36 |
| 37 | Implementar ações de desativação/reativação, confirmação e atualização do status exibido | 06/11 | 10/11 | 21, 62 |
| 63 | Restringir a tela ao administrador e tratar tentativas de acesso não autorizado | 05/11 | 05/11 | 36, 55 |
| 38 | Criar formulário de avaliação com nota de 1 a 5 estrelas, comentário e contador/limite de 300 caracteres | 06/10 | 09/10 | 8 |
| 39 | Disponibilizar envio de avaliação somente após reserva concluída e exibir mensagem quando o usuário não puder avaliar | 16/11 | 16/11 | 25, 38 |
| 40 | Exibir avaliações e nota média da quadra na página da quadra | 16/11 | 16/11 | 25, 45 |

## Testes e implantação (19/11/2026 – 25/11/2026)

| ID | Tarefa | Início | Fim | Dependências |
|---|---|---|---|---|
| 65 | Executar testes funcionais e de integração do sistema | 19/11 | 20/11 | 6, 59 |
| 66 | Corrigir problemas identificados nos testes e realizar retestes | 23/11 | 24/11 | 65 |
| 67 | Realizar deploy e validar o sistema em produção | 25/11 | 25/11 | 66 |
