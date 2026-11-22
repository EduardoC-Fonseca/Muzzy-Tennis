# Muzzi Tennis — Gerenciamento de Riscos

> Convertido de [`documento_riscos.pdf`](documento_riscos.pdf). O PDF continua sendo a fonte oficial.

**Integrantes do grupo:** Davi Abner Almeida Santiago, Eduardo Christianini, Emerson Ataide, Hálisson Piovezana, Maria Clara Barbosa Fernandes.

## 1. Objetivo e abordagem

O gerenciamento de riscos busca identificar e analisar eventos incertos que possam afetar os objetivos do projeto, bem como planejar respostas proporcionais à probabilidade e ao impacto de cada evento. O registro deverá ser revisado durante o desenvolvimento, sobretudo quando houver mudanças nos requisitos, no cronograma, na disponibilidade da equipe ou nas tecnologias utilizadas.

A identificação considera riscos de cronograma, equipe, aspectos técnicos, infraestrutura e dependências externas. As avaliações são estimativas iniciais para discussão da equipe.

## 2. Registro e análise dos riscos

Probabilidade e impacto: baixa, média, alta. Grau de risco: baixo (1–2), moderado (3–4), alto (6) e crítico (9).

| ID | Risco e possível impacto | Categoria | Probabilidade | Impacto | Grau |
|---|---|---|---|---|---|
| R1 | **Agenda acadêmica:** a sobreposição de provas, trabalhos e projetos de extensão pode reduzir a disponibilidade dos integrantes, atrasando atividades e comprometendo entregas. | Cronograma | Alta | Alto | 9 — Crítico |
| R2 | **Problemas pessoais e indisponibilidade:** a ausência ou redução da disponibilidade de um membro pode sobrecarregar os demais, criar dependências e atrasar atividades. | Equipe | Média | Alto | 6 — Alto |
| R3 | **Subestimação da complexidade:** estimativas inferiores ao esforço necessário podem gerar atrasos, retrabalho e pressão para reduzir testes ou funcionalidades. | Cronograma | Alta | Alto | 9 — Crítico |
| R4 | **Falhas na integração entre Frontend e Backend:** incompatibilidades nos contratos das APIs, nos formatos dos dados ou nas regras de negócio podem impedir o funcionamento integrado e gerar retrabalho. | Técnico | Média | Alto | 6 — Alto |
| R5 | **Sobrecarga ou indisponibilidade da infraestrutura:** excesso de requisições, limites de capacidade ou falhas de configuração podem deixar servidor ou APIs lentos ou indisponíveis. | Técnico | Baixa | Alto | 3 — Moderado |
| R6 | **Dependência de ferramentas e serviços externos:** indisponibilidade, alterações de versão, mudanças de limites ou descontinuação podem interromper o desenvolvimento ou comprometer funcionalidades. | Ferramentas | Média | Médio | 4 — Moderado |

## 3. Plano de respostas aos riscos

Mitigação: ações preventivas para reduzir probabilidade ou impacto (antes do evento). Contingência: ações acionadas caso o risco se concretize.

| ID | Mitigação | Contingência | Sinais de alerta | Responsável sugerido |
|---|---|---|---|---|
| R1 | Mapear provas, trabalhos e compromissos acadêmicos; planejar entregas conforme a disponibilidade real; acompanhar o progresso semanalmente; prever margem para imprevistos. | Replanejar as atividades afetadas, redistribuir tarefas conforme a capacidade da equipe e priorizar funcionalidades essenciais. Comunicar impactos aos responsáveis pelas entregas. | Conflitos de datas; tarefas sem progresso; atrasos recorrentes nas metas semanais. | Responsável pelo gerenciamento do projeto. |
| R2 | Manter documentação mínima; utilizar controle de versão; realizar revisões de código; compartilhar conhecimento e evitar que atividades críticas dependam de uma única pessoa. | Redistribuir as tarefas, transferir o conhecimento necessário, reorganizar prioridades e reduzir funcionalidades secundárias se necessário para preservar as entregas essenciais. | Ausências em reuniões; tarefas sem atualização; concentração de tarefas críticas em uma pessoa; bloqueios sem responsável. | Responsável pelo projeto, com participação da equipe. |
| R3 | Decompor funcionalidades complexas; revisar estimativas em equipe; criar protótipos para componentes incertos; comparar esforço previsto e realizado e atualizar estimativas. | Usar a margem de contingência disponível, replanejar e priorizar o escopo. Simplificar funcionalidades secundárias, preservando testes e funcionalidades essenciais. | Atividades ultrapassando estimativas repetidamente; dificuldades técnicas recorrentes; retrabalho significativo; aumento de tarefas pendentes. | Responsável pelo cronograma e responsável técnico. |
| R4 | Definir contratos das APIs (parâmetros, formatos de resposta, erros e regras de negócio); integrar progressivamente; usar dados simulados; manter comunicação entre Frontend e Backend. | Alinhar os contratos das APIs, priorizar os fluxos essenciais e usar dados simulados temporariamente para desbloquear as interfaces. Validar a integração real antes da entrega. | Respostas incompatíveis; falhas frequentes nas requisições; divergência entre dados produzidos e consumidos; testes de integração mal sucedidos. | Responsáveis pelo Frontend e pelo Backend. |
| R5 | Realizar testes básicos de carga; configurar limites de requisições; monitorar erros e tempo de resposta; usar paginação/cache quando apropriado; manter procedimento de recuperação. | Restringir temporariamente o tráfego, desabilitar funcionalidades não essenciais, ampliar recursos conforme a infraestrutura e reverter alterações que tenham causado a falha. | Aumento do tempo de resposta; erros do servidor; consumo excessivo de recursos; limites de serviço esgotados; falhas em operações essenciais. | Responsável técnico pela infraestrutura e pelo Backend. |
| R6 | Selecionar ferramentas com manutenção e documentação adequadas; verificar licenças; fixar versões quando apropriado; avaliar alternativas e reduzir acoplamento a fornecedores. | Substituir a ferramenta por alternativa previamente avaliada, quando viável; reverter para versão compatível se seguro; ou usar procedimento temporário simplificado para funções não essenciais. | Indisponibilidade recorrente; mudanças de limites ou condições; incompatibilidade após atualização; descontinuação; ausência de alternativa operacional conhecida. | Responsável técnico pelas integrações e dependências. |
