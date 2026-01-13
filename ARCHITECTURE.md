# Arquitetura do Sistema - Gestão Acadêmica

Este documento detalha a arquitetura técnica do software de Gestão Acadêmica. Ele serve como guia de referência para desenvolvedores que desejam manter, estender ou entender o funcionamento interno do sistema.

## 1. Visão Geral

O sistema é uma aplicação desktop desenvolvida em **Python 3.10+** que segue o padrão de arquitetura **MVC (Model-View-Controller)** adaptado, com uma camada de serviço robusta (**Service Layer**). A interface gráfica é construída com **CustomTkinter** (CTK), e a persistência de dados é gerenciada pelo **SQLAlchemy** (ORM) sobre um banco de dados **SQLite**.

Um componente central da arquitetura é o **Assistente de IA**, que opera de forma integrada mas desacoplada, utilizando um padrão de design de Ferramentas (Tools) para interagir com o sistema de forma segura.

### Principais Tecnologias
-   **Linguagem:** Python
-   **GUI:** CustomTkinter (Wrapper moderno sobre Tkinter)
-   **ORM:** SQLAlchemy
-   **Banco de Dados:** SQLite
-   **IA:** Integração agnóstica de provedor (OpenAI, etc.)
-   **Visualização:** Matplotlib
-   **Gerenciamento de Dependências:** Poetry
-   **Testes:** Pytest

## 2. Estrutura de Diretórios

A organização do código reflete a separação de responsabilidades:

```text
.
├── app/
│   ├── core/               # Núcleo da aplicação (Configuração, Segurança, Framework de IA)
│   │   ├── llm/            # Abstração dos provedores de LLM
│   │   ├── tools/          # Framework de execução de ferramentas da IA (Registry, Executor)
│   │   └── config.py       # Gerenciamento de configurações
│   ├── data/               # Configuração do banco e arquivos estáticos (JSONs da BNCC)
│   ├── models/             # Modelos ORM (SQLAlchemy) - Definição do Schema
│   │   ├── ...             # student.py, class_.py, course.py, etc.
│   │   └── schedule.py     # Modelos de Horário Escolar
│   ├── services/           # Lógica de Negócios
│   │   ├── data_service.py      # CRUD Central
│   │   ├── assistant_service.py # Lógica do Agente IA
│   │   ├── report_service.py    # Geração de Relatórios e Gráficos
│   │   └── bncc_service.py      # Gestão da Base Nacional Comum Curricular
│   ├── tools/              # Implementação concreta das ferramentas do Agente
│   ├── ui/                 # Camada de Apresentação
│   │   ├── views/          # Telas (Dashboard, Schedule, ClassDetail, etc.)
│   │   ├── widgets/        # Componentes reutilizáveis
│   │   └── main_app.py     # Ponto de entrada da UI
│   └── utils/              # Utilitários
│       ├── async_utils.py       # Gerenciamento de Threads/Async
│       ├── student_csv_parser.py # Importação determinística de CSV
│       └── ...
├── tests/                  # Testes Automatizados
├── AGENTS.md               # Diretrizes para Agentes de IA
├── main.py                 # Ponto de entrada (Bootstrap)
└── pyproject.toml          # Definição de dependências
```

## 3. Camada de Dados (Data Layer)

A camada de dados utiliza o **SQLAlchemy** para mapear classes Python para tabelas do banco de dados SQLite (`academic_management.db`).

### Inicialização
A inicialização do banco de dados ocorre em `main.py`. O sistema verifica a existência das tabelas e as cria automaticamente usando `Base.metadata.create_all(engine)`.

### Diagrama ERD (Entidade-Relacionamento)

```mermaid
erDiagram
    STUDENT ||--o{ CLASS_ENROLLMENT : "possui"
    STUDENT ||--o{ GRADE : "recebe"
    STUDENT ||--o{ INCIDENT : "envolvido_em"
    CLASS ||--o{ CLASS_ENROLLMENT : "contém"
    CLASS ||--o{ CLASS_SUBJECT : "ensina"
    CLASS ||--o{ INCIDENT : "registra"
    COURSE ||--o{ CLASS_SUBJECT : "definido_em"
    CLASS_SUBJECT ||--o{ ASSESSMENT : "inclui"
    CLASS_SUBJECT ||--o{ LESSON : "rastreia"
    CLASS_SUBJECT ||--o{ WEEKLY_SCHEDULE : "ocupa"
    ASSESSMENT ||--o{ GRADE : "avaliado_por"
    TIME_SLOT ||--o{ WEEKLY_SCHEDULE : "define"

    STUDENT {
        int id
        string first_name
        string last_name
    }
    CLASS {
        int id
        string name
    }
    COURSE {
        int id
        string name
        string bncc_expected
    }
    CLASS_ENROLLMENT {
        int id
        int student_id
        int class_id
        string status
    }
    GRADE {
        int id
        float score
    }
    TIME_SLOT {
        int id
        int day_of_week
        int period_index
        time start_time
    }
    WEEKLY_SCHEDULE {
        int id
        int time_slot_id
        int class_subject_id
    }
```

## 4. Camada de Serviços (Service Layer)

A lógica de negócios é encapsulada em serviços:

### `DataService` (`app/services/data_service.py`)
Atua como uma **Fachada (Facade)** centralizada para operações CRUD e gestão de transações. Internamente, delega a lógica para serviços especializados localizados em `app/services/data/` (ex: `StudentService`, `GradeService`, `EnrollmentService`), garantindo modularidade e coesão.

### `AssistantService` (`app/services/assistant_service.py`)
Orquestra a inteligência artificial, mantendo histórico de conversas e gerenciando a chamada de ferramentas.

### `ReportService` (`app/services/report_service.py`)
Centraliza a lógica de geração de relatórios, gráficos (via Matplotlib) e exportações. Utilizado tanto pela UI quanto pelo Agente.

### `BNCCService` (`app/services/bncc_service.py`)
Gerencia o acesso aos dados estáticos da Base Nacional Comum Curricular (BNCC), permitindo a pesquisa e seleção de competências.

## 5. Arquitetura do Agente de IA

O sistema implementa um padrão de "Function Calling".

### Componentes Principais (`app/core/`)

1.  **`LLMProvider`:** Interface abstrata para provedores de IA.
2.  **`ToolRegistry`:** Registro central de ferramentas (`@tool`).
3.  **`ToolExecutor`:** Executor seguro que valida argumentos e invoca as funções Python.

### Fluxo de Execução Típico
1.  Usuário solicita uma ação.
2.  `AssistantService` envia contexto + definições de ferramentas para o LLM.
3.  LLM decide chamar uma ferramenta (ex: `get_global_dashboard_stats`).
4.  `ToolExecutor` executa a função e retorna o JSON resultante.
5.  `AssistantService` devolve o resultado ao LLM, que gera a resposta final em linguagem natural.

## 6. Camada de Interface (UI) e Assincronismo

A interface utiliza **CustomTkinter** e roda em um loop de eventos principal.

### Solução Híbrida (Tkinter + Asyncio)
Para evitar travamentos da UI em operações longas (I/O, IA):
1.  **Loop Asyncio:** Integrado ao loop do Tkinter via polling (`update_asyncio`).
2.  **`run_async_task`:** Utilitário (`app/utils/async_utils.py`) para despachar corrotinas para background, com callbacks thread-safe para atualizar a interface.

## 7. Desenvolvimento e Testes

-   **Testes:** Rodam com `pytest` utilizando banco de dados SQLite **em memória** (`tests/conftest.py`) para isolamento e performance.
