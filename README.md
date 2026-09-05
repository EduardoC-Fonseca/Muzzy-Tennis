#Muzzy-Tennis
Plataforma Web em Flutter para agendamento de quadras de tênis, conectando proprietários a jogadores. Projeto focado na aplicação de conceitos de Gerência de Projetos de Software.

# 🎾 Muzzy Tennis

Bem-vindo ao repositório do **Muzzy Tennis**, uma plataforma Web desenvolvida em Flutter que conecta proprietários de clubes/quadras de tênis a jogadores, funcionando de forma semelhante ao modelo do Airbnb para espaços esportivos.

## Objetivo do Projeto

Este projeto tem fins acadêmicos e práticos. O objetivo principal é aplicar os conceitos de **Gerência de Projetos de Software**, produzindo todos os artefatos necessários para o planejamento, organização, estimativa e acompanhamento do ciclo de vida de desenvolvimento de um sistema de software.

## O Contexto

O sistema atua como um intermediário entre quem possui uma quadra e aquele que deseja jogar tênis. Qualquer proprietário de um clube/quadra de tênis poderá registrar seu espaço na nossa plataforma e disponibilizá-lo para a comunidade. Por outro lado, os jogadores podem entrar no sistema, encontrar quadras disponíveis e reservar horários de forma extremamente ágil.

## Funcionalidades Principais

O sistema é dividido para atender a dois perfis principais de usuários:

###  Cliente (Jogador)
Foco em agilidade e conversão. O cliente não precisa passar por processos longos de cadastro para jogar.
- **Busca Rápida:** Consulta de quadras e horários disponíveis.
- **Agendamento Simplificado:** Reserva de horários (slots de 1 hora) informando apenas o Nome Completo e Telefone para contato **ou** E-MAIL(devemos decidir)
- **Sem Login Obrigatório:** Não há necessidade de criação de conta para realizar a reserva.
- **Regra de Negócio:** Limite máximo de 2 agendamentos de horários por dia por cliente.

### Proprietário do Espaço (Clube)
Foco em gestão e rentabilidade. O proprietário tem total controle sobre seus espaços cadastrados.
- **Área Restrita:** Acesso seguro via Login e Senha.(pelo o que entendemos, alterar)
- **Gestão de Espaços:** Cadastro, edição e gerenciamento das quadras disponíveis.
- **Controle de Agenda:** Disponibilização de dias e horários para agendamento na plataforma.
- **Acompanhamento:** Dashboard/Visualização dos agendamentos realizados.
- **Relatórios:** Geração de relatórios de locação por período, com identificação dos clientes que realizaram as reservas.

## Tecnologias Utilizadas

- **Frontend/Web:** [Flutter Web](https://flutter.dev/multi-platform/web)
- *(Ainda a decidir outras tecnologias que vamos usar, como Firebase, Node.js, PostgreSQL, etc. para o backend/banco de dados)*

## Premissas do Projeto

Conforme as definições do grupo, algumas características adicionais (como o modelo de negócio no estilo "Airbnb" de múltiplas quadras/clubes) foram adotadas como premissas fundamentais para o desenvolvimento e arquitetura do software. Todas as decisões de arquitetura e gerência de projeto estão documentadas nos artefatos do repositório.

## Equipe de Desenvolvimento

- Maria Clara
- Davi
- Eduardo
- Emerson
- Halison

---
*Projeto desenvolvido como requisito prático para o estudo de Gerência de Projetos de Software.*
