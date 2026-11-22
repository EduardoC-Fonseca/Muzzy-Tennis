# Muzzi Tennis — Documento de Visão

> Convertido de [`documento_visao.pdf`](documento_visao.pdf) (ERS-MT-001, versão 1.1, 27/10/2026). O PDF continua sendo a fonte oficial; este arquivo existe para consulta rápida durante o desenvolvimento.

**Integrantes do grupo:** Davi Abner Almeida Santiago, Eduardo Christianini Fonseca Junior, Emerson Caetano Ataide, Hálisson Silveira Piovezana, Maria Clara Barbosa Fernandes.

## Histórico da revisão

| Data | Versão | Descrição | Autor |
|---|---|---|---|
| 06/10/2026 | 1.0 | Criação do documento. | Maria Clara B. Fernandes |
| 25/10/2026 | 1.1 | Revisão e padronização do documento. | Davi Abner A. Santiago |

## 1. Introdução

O objetivo deste documento é coletar, analisar e definir necessidades e recursos de alto nível do Muzzi Tennis. Ele está focado nos recursos necessários aos investidores e usuários de destino e por que essas necessidades existem. Os detalhes de como o Muzzi Tennis atende essas necessidades são explicados nas especificações de caso de uso e suplementares.

O documento de Visão fornece uma visão geral de todo o documento, estabelecendo uma compreensão geral do projeto, identificando o problema a ser solucionado, as necessidades dos usuários e as principais funcionalidades previstas para o sistema.

### 1.1 Objetivo

Fornecer o contexto geral do projeto Muzzi Tennis, apresentando a oportunidade de negócio, o problema a ser resolvido, a visão geral do produto e seus requisitos funcionais e não funcionais.

### 1.2 Visão geral

O restante do documento aborda o posicionamento do projeto (oportunidade de negócio e declaração do problema); a visão geral do produto (perspectiva, premissas, restrições e licença); os requisitos funcionais, com histórias de usuário e cenários de teste; e os requisitos não funcionais.

## 2. Posicionamento

### 2.1 Oportunidade de negócio

Desenvolver uma plataforma que centralize o processo de reserva de quadras de tênis em João Monlevade, permitindo que os clientes consultem a disponibilidade dos espaços e realizem reservas sem a necessidade de autenticação. A solução busca facilitar o gerenciamento das quadras e dos horários disponibilizados pelos proprietários, reduzindo conflitos de agendamento e proporcionando maior praticidade aos clientes. Além disso, pretende ampliar a divulgação e o alcance dos estabelecimentos.

### 2.2 Declaração do problema

| | |
|---|---|
| **O problema de** | Dificuldade em encontrar informações sobre a disponibilidade de quadras de tênis e realizar reservas de forma organizada, além da possibilidade de ocorrerem conflitos de horários durante o gerenciamento das reservas. |
| **afeta** | Os clientes interessados em reservar quadras de tênis e os proprietários dos espaços que disponibilizam essas quadras na cidade de João Monlevade. |
| **o impacto é o seguinte** | Os clientes podem ter dificuldade para identificar quadras disponíveis e realizar reservas, enquanto os proprietários podem enfrentar dificuldades no controle dos horários, ocasionando conflitos de reservas, além de limitar a divulgação e o alcance de seus espaços. |
| **uma solução bem-sucedida seria** | Uma plataforma que centraliza as quadras de tênis disponíveis na cidade, permitindo que os clientes consultem os horários disponíveis e realizem reservas sem login, enquanto os proprietários cadastram suas quadras e horários de funcionamento e gerenciam as reservas de forma organizada. Espera-se reduzir conflitos de horários, facilitar o processo de reserva e ampliar a divulgação dos espaços. |

## 3. Visão geral do produto

### 3.1 Perspectiva do produto

O Muzzi Tennis é um sistema web de reservas de quadras de tênis, permitindo que os clientes consultem a disponibilidade das quadras e realizem, consultem ou cancelem suas reservas, **sem a necessidade de autenticação para a realização de reservas**.

Para os proprietários, o sistema disponibilizará o cadastro e gerenciamento de suas quadras, definição dos horários disponíveis e acompanhamento das reservas realizadas. Os administradores serão responsáveis pelo gerenciamento geral dos usuários e das quadras cadastradas.

O sistema adotará uma **arquitetura monolítica**, com integração a um **serviço externo de pagamentos** e funcionalidades de comunicação com os clientes.

### 3.2 Premissas

- O sistema contemplará três perfis de usuário: **administrador** (gerenciamento geral da plataforma), **proprietário** (cadastro e gerenciamento de suas quadras e reservas) e **cliente** (consulta das quadras e realização de reservas).
- Os usuários deverão possuir acesso à internet.
- Mudanças de escopo dependem da validação prévia dos stakeholders.
- Um usuário pode escolher uma quadra sem necessidade de cadastro prévio.
- Os clientes poderão consultar a disponibilidade e realizar reservas sem criar conta ou efetuar login, sendo necessário apenas fornecer os dados solicitados para identificação e confirmação da reserva.

### 3.3 Restrições

1. O sistema será disponibilizado inicialmente como aplicação web, acessível por navegadores compatíveis, sem exigir instalação de aplicativo.
2. O sistema não terá disponibilidade internacional, atuando apenas nacionalmente.

### 3.4 Licença

Projeto acadêmico disponibilizado ao professor para demonstração, avaliação e validação, sem cobrança de licença ou chave de ativação. O código-fonte é disponibilizado sob a **Licença MIT**.

## 4. Requisitos funcionais

- **RF01 — Reserva de quadras:** permitir que clientes reservem quadras em datas e horários disponíveis, sem autenticação, com pagamento por serviço externo.
- **RF02 — Cancelamento de reservas:** permitir que clientes cancelem suas reservas, respeitando as condições e prazos de cancelamento.
- **RF03 — Cadastro de quadras:** permitir que proprietários cadastrem quadras informando nome, tipo de quadra, endereço, fotos, descrição, valor do aluguel e capacidade máxima de jogadores.
- **RF04 — Consulta de reservas pelo proprietário:** permitir que proprietários consultem os dados dos clientes que reservaram suas quadras, com datas e horários.
- **RF05 — Gerenciamento administrativo:** permitir que administradores visualizem e gerenciem usuários e quadras, inclusive inativos.
- **RF06 — Avaliação de quadras:** permitir que clientes avaliem quadras após a conclusão da reserva, com nota e comentário.

> A numeração RF01–RF06 e CT01–CT21 foi adicionada nesta conversão para facilitar a rastreabilidade; o PDF usa apenas listas.

### 4.1 Histórias de usuário

1. **HU01** — Como cliente, quero reservar uma quadra para jogar uma partida de tênis com meus amigos.
2. **HU02** — Como cliente, quero cancelar uma reserva que realizei, para receber o reembolso do valor pago.
3. **HU03** — Como proprietário, quero cadastrar minhas quadras (nome, tipo, endereço, fotos, descrição, valor do aluguel e capacidade máxima de jogadores) para disponibilizá-las aos clientes.
4. **HU04** — Como proprietário, quero gerenciar os horários disponíveis das minhas quadras e consultar as informações dos clientes que reservarem (datas e horários), para organizar a utilização dos espaços e evitar conflitos.
5. **HU05** — Como administrador, quero visualizar e gerenciar os clientes e as quadras cadastradas, incluindo seus status, para garantir o controle e o uso adequado da plataforma.
6. **HU06** — Como cliente, quero avaliar e comentar uma quadra que utilizei para compartilhar minha experiência com a comunidade.

### 4.2 Cenários de teste e casos alternativos

| ID | Dado que… | Quando… | Então… |
|---|---|---|---|
| CT01 | a quadra está disponível na data/horário, a quantidade de pessoas respeita o limite e informei os dados necessários | eu realizar o pagamento da garantia dentro do prazo | o sistema confirma a reserva. |
| CT02 | a quadra já está reservada na data/horário | eu tentar reservar o mesmo período | o sistema não permite e informa que o horário não está disponível. |
| CT03 | o cliente iniciou uma reserva e não pagou a reserva/garantia | o prazo de **uma hora** terminar | o sistema cancela a solicitação pendente e o horário volta a ficar disponível. |
| CT04 | o cliente selecionou uma quadra | informar quantidade de jogadores maior que o limite da quadra | o sistema não conclui a reserva e informa o limite máximo. |
| CT05 | o cliente possui reserva confirmada e faltam **pelo menos 24 horas** para o início | solicitar e confirmar o cancelamento | o sistema cancela, libera o horário e processa o reembolso, quando aplicável. |
| CT06 | o cliente possui reserva confirmada e faltam **menos de 24 horas** | tentar cancelar | o sistema não permite e informa que o prazo foi excedido. |
| CT07 | o proprietário preencheu corretamente os dados da quadra | confirmar e finalizar o cadastro | o sistema registra a quadra e a disponibiliza ao cliente. |
| CT08 | o proprietário está cadastrando uma quadra | tentar finalizar com dados obrigatórios ausentes ou inválidos | o sistema não conclui e informa quais dados corrigir. |
| CT09 | o proprietário está cadastrando uma quadra | uma foto for identificada como inadequada às regras da plataforma | o sistema impede seu uso e informa o motivo da rejeição. |
| CT10 | o proprietário está preenchendo a descrição | atingir o limite máximo de caracteres | o sistema impede novos caracteres e informa o limite. |
| CT11 | a quadra está cadastrada e possui reservas | for consultada | o sistema apresenta os dados de identificação dos clientes, com datas e horários. |
| CT12 | a quadra está cadastrada | o proprietário atualizar os horários disponíveis | o sistema atualiza a disponibilidade, **preservando as reservas já confirmadas**. |
| CT13 | o cliente iniciou uma reserva | o pagamento da garantia não for aprovado | o sistema não confirma e informa que o pagamento não foi concluído. |
| CT14 | o cliente cancelou dentro do prazo | o cancelamento for confirmado | o sistema atualiza a situação da reserva e **notifica o proprietário**. |
| CT15 | o administrador está autenticado | acessar o gerenciamento de usuários | o sistema apresenta os usuários, seus papéis (roles) e status. |
| CT16 | o administrador está no gerenciamento de usuários | pesquisar por nome e/ou e-mail | o sistema apresenta os usuários correspondentes. |
| CT17 | um usuário está ativo | o administrador desativá-lo | o status passa a inativo e o usuário não acessa funcionalidades autenticadas. |
| CT18 | um usuário está desativado | o administrador reativá-lo | o status volta a ativo e o acesso ao seu perfil é restabelecido. |
| CT19 | o cliente tem reserva concluída na quadra | selecionar nota de 1 a 5 estrelas, comentar e enviar | a avaliação é publicada na página da quadra e a nota média é atualizada. |
| CT20 | o cliente não possui reserva concluída na quadra | tentar avaliar | o sistema não permite e informa que só quem utilizou a quadra pode avaliar. |
| CT21 | o cliente está preenchendo o comentário | atingir **300 caracteres** | o sistema impede novos caracteres e exibe o limite atingido. |

## 5. Requisitos não funcionais

1. **RNF01 — Confiabilidade:** garantir integridade e consistência das informações de quadras, usuários e reservas, evitando perda de dados e **reservas conflitantes para a mesma quadra, data e horário**.
2. **RNF02 — Usabilidade:** interface amigável e intuitiva, com mensagens de orientação e feedback das ações.
3. **RNF03 — Segurança:** proteger dados pessoais e de reservas, com autenticação e autorização para proprietários e administradores e medidas contra acessos não autorizados.
4. **RNF04 — Manutenibilidade:** código organizado e modularizado, facilitando correções, testes e melhorias.
5. **RNF05 — Disponibilidade:** permanecer acessível durante o período de operação.
6. **RNF06 — Desempenho:** tempos de resposta adequados para consulta de quadras, verificação de disponibilidade e gerenciamento de reservas.
7. **RNF07 — Portabilidade:** acessível por navegadores web compatíveis em diferentes sistemas operacionais.
8. **RNF08 — Escalabilidade:** estrutura que permita expansão conforme o crescimento de usuários, quadras e reservas.
