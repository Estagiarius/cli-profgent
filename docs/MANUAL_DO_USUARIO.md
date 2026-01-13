# Manual do Usuário - Sistema de Gestão Acadêmica (Profgent)

Bem-vindo ao manual completo do **Profgent**. Este documento foi elaborado para fornecer uma compreensão profunda de todas as funcionalidades do sistema, garantindo que você possa extrair o máximo potencial da ferramenta para a gestão escolar.

---

## Sumário
1. [Introdução](#1-introdução)
2. [Primeiros Passos e Navegação](#2-primeiros-passos-e-navegação)
3. [Dashboard de Análises](#3-dashboard-de-análises)
4. [Gestão de Turmas (O Coração do Sistema)](#4-gestão-de-turmas)
5. [Área da Turma: Detalhamento Completo](#5-área-da-turma-detalhamento-completo)
    - [5.1 Cabeçalho e Seleção de Disciplina](#51-cabeçalho-e-seleção-de-disciplina)
    - [5.2 Alunos: Matrícula e Gestão](#52-alunos-matrícula-e-gestão)
    - [5.3 Avaliações: Criando o Critério Avaliativo](#53-avaliações-criando-o-critério-avaliativo)
    - [5.4 Aulas: Registro, Frequência e IA](#54-aulas-registro-frequência-e-ia)
    - [5.5 Quadro de Notas: Lançamento e Cálculo](#55-quadro-de-notas-lançamento-e-cálculo)
    - [5.6 Incidentes Disciplinares](#56-incidentes-disciplinares)
    - [5.7 BNCC e Relatórios](#57-bncc-e-relatórios)
6. [Horário Escolar](#6-horário-escolar)
7. [Gestão de Dados Globais](#7-gestão-de-dados-globais)
8. [Configurações e Personalização](#8-configurações-e-personalização)
9. [Assistente de Inteligência Artificial](#9-assistente-de-inteligência-artificial)

---

## 1. Introdução

O **Profgent** é uma solução integrada para a gestão acadêmica focada na realidade da escola brasileira. Ele centraliza informações de alunos, turmas, notas, frequência e currículo (BNCC) em uma interface unificada.

### Conceitos Chave
- **Turma:** Um grupo de alunos (ex: "6º Ano A").
- **Disciplina:** A matéria lecionada (ex: "Matemática"). Uma turma possui várias disciplinas.
- **Avaliação:** Um instrumento de nota (ex: "Prova Mensal", "Trabalho").
- **Aula:** O registro diário do conteúdo lecionado e da chamada.

---

## 2. Primeiros Passos e Navegação

Ao abrir o sistema, você encontrará a **Barra Lateral de Navegação** à esquerda. Ela é fixa e permite acesso rápido a qualquer módulo:

1.  **Dashboard:** O "painel de controle" com estatísticas.
2.  **Minhas Turmas:** Onde 80% do trabalho acontece. Gerenciamento das classes.
3.  **Horário:** Visualização da grade de aulas semanal.
4.  **Assistente IA:** Chat com a inteligência artificial.
5.  **Gestão de Dados:** Cadastros "crus" de alunos e catálogo de disciplinas.
6.  **Configurações:** Ajustes do sistema.

**Dica:** O sistema salva os dados automaticamente em um banco de dados local sempre que você confirma uma ação (botões "Salvar", "Confirmar", etc.).

---

## 3. Dashboard de Análises

O Dashboard oferece uma visão macro da escola para tomada de decisão rápida.

### Aba: Visão Geral
*   **Cards de Estatísticas:** Números absolutos de Alunos Ativos, Turmas, Disciplinas e Incidentes. Use para ter noção do tamanho da operação.
*   **Índice Global de Aprovação:** Um gráfico de pizza que mostra a saúde acadêmica da escola.
    *   **Verde:** Alunos com média >= 5.0 (Aprovados).
    *   **Vermelho:** Alunos com média < 5.0 (Em Risco).
    *   **Ação:** Clique no botão vermelho **"Ver Alunos em Risco"** para abrir uma janela flutuante com a lista nominal de quem precisa de atenção, indicando a turma e a média atual.

### Aba: Destaques & Alertas
*   **Quadro de Honra:** Lista automática dos melhores alunos da escola (Média Geral >= 9.0). Útil para premiações e reconhecimento.
*   **Top Incidentes:** Ranking das turmas mais "problemáticas" baseado no número de ocorrências registradas. Ajuda a identificar onde a disciplina precisa ser reforçada.

### Aba: Por Disciplina
*   Selecione uma disciplina (ex: "Matemática") no menu suspenso.
*   O sistema gera um gráfico de barras mostrando a distribuição das notas especificamente para aquela matéria em toda a escola.

---

## 4. Gestão de Turmas

Acesse via menu **"Minhas Turmas"**.

### Criando uma Nova Turma
1.  Clique no botão **"Adicionar Nova Turma"** (canto superior direito).
2.  Digite o nome (ex: "1º Ano B").
3.  Confirme. Um novo "Card" aparecerá na tela.

### Interagindo com o Card da Turma
Cada turma é representada por um cartão com 4 botões de ação:
1.  **Ver Detalhes:** Entra na gestão completa da turma (ver seção 5).
2.  **Editar:** Corrige o nome da turma.
3.  **Copiar Turma (Verde):** Ferramenta poderosa para virada de ano/semestre.
    *   Permite duplicar a turma com um novo nome.
    *   Você escolhe o que copiar: As Disciplinas? As Avaliações configuradas? Os Alunos (rematrícula automática)?
4.  **Excluir (Vermelho):** Apaga a turma e **todos** os seus dados (notas, aulas, vínculos). Exige digitar "DELETE" para confirmar.

---

## 5. Área da Turma: Detalhamento Completo

Ao clicar em "Ver Detalhes", você entra no painel de controle daquela turma específica.

### 5.1 Cabeçalho e Seleção de Disciplina
No topo da tela, existe um menu **"Disciplina"**.
*   **Por que isso é importante?** Notas, Aulas e Frequência são lançadas *por disciplina*.
*   **Ação Obrigatória:** Se a turma é nova, o menu estará vazio. Clique em **"Adicionar Disciplina"** à direita, selecione a matéria (ex: "Ciências") e confirme. Repita para todas as matérias da turma.
*   **Navegação:** Use o menu para trocar de matéria. O conteúdo das abas (Notas, Aulas) mudará instantaneamente para refletir a disciplina selecionada.

### 5.2 Alunos: Matrícula e Gestão
Aba **"Alunos"**. Aqui você define QUEM estuda nesta turma.

*   **Matricular Aluno:** Abre uma lista de alunos cadastrados no sistema que *não* estão nesta turma. Selecione um ou vários e confirme.
*   **Importar Alunos (.csv):** A maneira mais rápida de começar.
    *   Prepare uma planilha Excel/CSV com colunas como "Nome Completo" e "Data de Nascimento".
    *   Clique no botão, selecione o arquivo e o sistema fará o cadastro e matrícula em lote.
*   **Status do Aluno:**
    *   Na lista, cada aluno tem um botão "Ativo" (Verde) ou "Inativo" (Vermelho).
    *   Clique para alternar. Alunos inativos não aparecem na chamada e nem nos relatórios de risco, mas seu histórico de notas é preservado.

### 5.3 Avaliações: Criando o Critério Avaliativo
Aba **"Avaliações"**. Configure como os alunos serão avaliados.

1.  Selecione a aba do **Bimestre** desejado (1º ao 4º).
2.  Clique em **"Adicionar Nova Avaliação"**.
3.  Preencha:
    *   **Nome:** (ex: "Prova P1").
    *   **Peso:** Importante para a média ponderada (ex: 1.0, 2.0).
    *   **BNCC:** (Opcional) Códigos das habilidades avaliadas.
4.  Repita para criar todas as avaliações do bimestre. O sistema somará os pesos para calcular a média.

### 5.4 Aulas: Registro, Frequência e IA
Aba **"Aulas"**. O diário de classe digital.

*   **Registrar Aula:** Clique em "Adicionar Nova Aula".
    *   Preencha Data e Título.
    *   **Gerar com IA:** Clique neste botão roxo se estiver sem criatividade. A IA lerá o título da aula e a disciplina e escreverá um plano de aula completo com objetivos e atividades no campo "Conteúdo".
    *   **BNCC:** Selecione os códigos trabalhados na aula.
*   **Frequência (Chamada):**
    *   Na lista de aulas, clique no botão verde **"Chamada"**.
    *   Uma lista de alunos aparecerá. Marque: **P** (Presente), **F** (Falta), **J** (Justificada).
    *   O sistema calcula a % de frequência automaticamente e exibe na aba de Alunos.

### 5.5 Quadro de Notas: Lançamento e Cálculo
Aba **"Quadro de Notas"**. Uma planilha ágil.

*   **Lançamento:** O sistema cruza os Alunos (linhas) com as Avaliações criadas (colunas). Basta digitar a nota.
*   **Cálculo Automático:** A última coluna mostra a **Média do Bimestre** calculada em tempo real baseada nos pesos das avaliações.
*   **Resultados Finais:** Na última aba deste quadro, você vê a média anual (média aritmética dos 4 bimestres).
    *   **Recuperação/Conselho:** Se precisar alterar a nota final calculada, digite o novo valor na coluna "Nota Final (Editável)". O sistema passará a considerar essa nota para aprovação.
*   **Salvar:** Sempre clique no botão **"Salvar Alterações"** no rodapé antes de trocar de aba.

### 5.6 Incidentes Disciplinares
Aba **"Incidentes"**.
*   Use para registrar ocorrências (ex: "Aluno brigou no recreio", "Aluno sem uniforme").
*   Isso alimenta o ranking de incidentes do Dashboard.

### 5.7 BNCC e Relatórios
Aba **"BNCC"**:
*   Mostra um "termômetro" de cobertura curricular.
*   Compare o que foi **Planejado** (no cadastro da disciplina) com o que foi efetivamente **Trabalhado** (nas Aulas e Avaliações).
*   Se a barra estiver vazia ou com alerta, certifique-se de configurar o **Currículo Global** clicando no botão "Editar Currículo Global".

Aba **"Relatórios"**:
*   **Boletim:** Selecione um aluno e gere um PDF/TXT com todas as notas e faltas.
*   **CSV:** Exporte tudo para Excel para fazer suas próprias análises.

---

## 6. Horário Escolar

Menu **"Horário"**. Organize a rotina da escola.

### Passo 1: Configuração (Aba Direita)
Aqui você define a "forma" do dia.
1.  Escolha o dia da semana (ex: Segunda-feira).
2.  Clique em **"+ Adicionar Aula"**.
3.  Defina: "1ª Aula" das "07:00" às "07:50".
4.  Crie todos os slots de tempo para a semana.

### Passo 2: Alocação (Aba Visualização)
Aqui você preenche o conteúdo.
1.  Você verá a grade vazia com os slots criados.
2.  Clique em um slot vazio (**"+ Alocar"**).
3.  Escolha a **Turma** e a **Disciplina** (ex: "1º Ano A - Matemática").
4.  O horário agora está preenchido.

### Passo 3: Uso Diário
*   Na visualização, clique em um horário já preenchido (ex: Terça, 10:00, História).
*   O sistema abre direto o formulário de **Chamada/Registro de Aula** para aquela turma específica. Atalho essencial para professores!

---

## 7. Gestão de Dados Globais

Menu **"Gestão de Dados"**.
Use esta tela para cadastros que não dependem de turmas.
*   **Alunos:** Cadastro "mestre" dos alunos. Se você precisa corrigir o nome de um aluno ou sua data de nascimento, faça aqui. A alteração reflete em todas as turmas.
*   **Disciplinas:** Catálogo de matérias da escola. Antes de adicionar "Robótica" numa turma, a disciplina "Robótica" precisa existir aqui.

---

## 8. Configurações e Personalização

Menu **"Configurações"**.
*   **Aparência:** Cansou do visual? Troque o tema (ex: "Dracula", "Ocean Breeze").
*   **Integração IA:** É aqui que você conecta o "cérebro" do sistema.
    *   Selecione o provedor (OpenAI, Maritaca, etc.).
    *   Cole sua **Chave de API**.
    *   Se usar Ollama (IA local), configure a URL aqui.

---

## 9. Assistente de Inteligência Artificial

Menu **"Assistente IA"**.
O assistente não é apenas um chat; é um agente capaz de executar funções no sistema.

**Experimente pedir:**
*   *"Crie uma turma chamada 3º Ano C"* (Ele cria a turma).
*   *"Quais alunos do 1º Ano A estão reprovando?"* (Ele busca as notas e analisa).
*   *"Monte um plano de aula sobre Fotossíntese para Ciências"* (Ele gera o texto).
*   *"Importe os alunos do arquivo alunos_novos.csv"* (Ele executa a importação).

Use linguagem natural. O assistente entende o contexto e ajuda a realizar tarefas repetitivas muito mais rápido.
