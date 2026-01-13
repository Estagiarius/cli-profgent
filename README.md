# ProfGent - Sistema de Gestão Acadêmica com Assistente de IA

## Sobre o Projeto

O **ProfGent** é um sistema de gerenciamento escolar desenvolvido em Python, projetado para simplificar a administração de turmas, alunos, notas e horários. A aplicação combina uma interface gráfica moderna (CustomTkinter) com um banco de dados robusto (SQLite/SQLAlchemy) e um **Assistente de IA integrado**, que permite realizar tarefas complexas através de comandos em linguagem natural.

## Funcionalidades Principais

*   **Gestão Acadêmica Completa (CRUD):** Controle total sobre Alunos, Turmas, Disciplinas, Avaliações e Notas.
*   **Horário Escolar:** Configuração flexível de grades horárias, definição de tempos de aula e alocação semanal de disciplinas por turma.
*   **Planejamento com BNCC:** Ferramentas dedicadas para o registro de aulas e seleção de competências da Base Nacional Comum Curricular (BNCC).
*   **Ferramentas de Produtividade:**
    *   **Cópia de Turmas:** Replique a estrutura completa de uma turma (disciplinas, avaliações) para um novo ano ou semestre.
    *   **Replicação de Aulas:** Copie planos de aula e conteúdos entre turmas diferentes.
    *   **Importação Inteligente:** Carregue listas de alunos via CSV com parser determinístico que ajusta nomes e formatações automaticamente.
*   **Visualização de Desempenho:** Geração automática de gráficos de distribuição de notas e boletins de desempenho individual (formato texto e visualização em tela).
*   **Assistente de IA:** Um agente inteligente capaz de executar operações de banco de dados ("Cadastre o aluno X"), analisar dados ("Qual a média da turma Y?") e gerar conteúdos de aula.
*   **Interface Moderna:** GUI baseada em CustomTkinter com suporte a temas e modo escuro.

## Tecnologias Utilizadas

*   **Linguagem:** Python 3.10+
*   **Interface (GUI):** CustomTkinter
*   **Banco de Dados:** SQLite + SQLAlchemy (ORM)
*   **Análise e Gráficos:** Matplotlib
*   **IA e LLM:** Integração com APIs compatíveis com OpenAI
*   **Gerenciamento:** Poetry (Dependências) e Pytest (Testes)

## Como Instalar e Rodar

### Pré-requisitos
*   Python 3.10 ou superior (versões 3.10 a 3.14 suportadas).
*   [Poetry](https://python-poetry.org/) instalado.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd academic-management-app
    ```

2.  **Instale as dependências:**
    ```bash
    poetry install
    ```

3.  **Execute a aplicação:**
    ```bash
    poetry run python main.py
    ```
    *O banco de dados `academic_management.db` será criado automaticamente na primeira execução.*

## Executando Testes

Para rodar a suíte de testes automatizados:

```bash
poetry run pytest
```

## Documentação Técnica

Para desenvolvedores e mantenedores, consulte a documentação detalhada:

*   [Guia de Arquitetura (ARCHITECTURE.md)](ARCHITECTURE.md): Estrutura do código, diagrama de dados e fluxo da IA.
*   [Guia para Agentes (AGENTS.md)](AGENTS.md): Diretrizes para desenvolvimento e manutenção por agentes de IA.
