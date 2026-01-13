# Guia para Agentes de IA

Este documento fornece diretrizes e informações essenciais para agentes de IA que trabalham neste repositório. Para uma visão técnica aprofundada, consulte sempre o arquivo [ARCHITECTURE.md](ARCHITECTURE.md).

## Visão Geral do Projeto

Este é um Sistema de Gestão Acadêmica construído em Python com uma GUI CustomTkinter e um banco de dados SQLite gerenciado via SQLAlchemy. O projeto inclui um Assistente de IA que utiliza um framework de ferramentas ("Function Calling") para interagir com o sistema de forma segura.

## Configuração do Ambiente

O projeto utiliza o **Poetry** para gerenciamento de dependências.

1.  **Instalar dependências:**
    ```bash
    poetry install --no-root --with dev
    ```
    *A flag `--with dev` é necessária para incluir dependências de teste como `pytest`.*

## Padrões de Desenvolvimento

Para manter a consistência e estabilidade do código, siga estas regras estritamente:

*   **Idioma:** Todo o código visível ao usuário (interface, logs, saídas de ferramentas) e comentários devem ser em **Português do Brasil**. Identificadores de código (variáveis, funções, classes) devem permanecer em **Inglês**.
*   **Cabeçalho de Propriedade Intelectual:** Todo arquivo de código-fonte (especialmente `.py`) deve iniciar com o seguinte cabeçalho (respeitando shebangs/encodings):
    ```python
    # Author: Victor Hugo Garcia de Oliveira
    # Date: [Data de Criação do Arquivo no Formato YYYY-MM-DD]
    #
    # This Source Code Form is subject to the terms of the Mozilla Public
    # License, v. 2.0. If a copy of the MPL was not distributed with this
    # file, You can obtain one at https://mozilla.org/MPL/2.0/.
    #
    # Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
    # License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
    # arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
    ```
    *Para arquivos novos, use a data atual. Para arquivos existentes, preserve a data da primeira inserção.*
*   **Interface Gráfica e Assincronismo:** A aplicação usa `CustomTkinter` (CTK) em um loop de eventos principal.
    *   **NUNCA** execute código bloqueante (ex: `time.sleep`, requisições HTTP síncronas, queries pesadas) diretamente na thread da UI. Isso congelará a aplicação.
    *   Utilize o utilitário `run_async_task` (`app/utils/async_utils.py`) para despachar corrotinas para background.
    *   A classe `MainApp` integra o loop `asyncio` através de um mecanismo de polling (`update_asyncio`).
*   **Injeção de Dependência:** As Views da UI não devem instanciar serviços diretamente. Elas devem receber instâncias de `DataService`, `AssistantService`, etc., via construtor (`__init__`).

## Execução e Testes

*   **Executar a aplicação:**
    ```bash
    poetry run python main.py
    ```

*   **Executar a suíte de testes:**
    ```bash
    poetry run pytest
    ```
    *   **Ambiente de Teste:** Os testes utilizam o `tests/conftest.py` para criar um banco de dados SQLite **em memória** (`db_session` fixture) para cada função de teste. Isso garante isolamento total.
    *   **Fixtures Úteis:** `db_session`, `data_service`, `assistant_service`.

## Arquitetura do Banco de Dados

**AVISO IMPORTANTE:** O sistema de migração de banco de dados **Alembic foi removido** deste projeto.

*   **Banco de Dados:** O arquivo é nomeado `academic_management.db`.
*   **Inicialização:** Todas as tabelas são criadas automaticamente na primeira vez que a aplicação é executada (`main.py` -> `initialize_database`), utilizando `Base.metadata.create_all(engine)`.
*   **Migrações:** Alterações de schema devem ser gerenciadas manualmente ou através de scripts de migração personalizados em `app/data/migrations.py` (se existirem), nunca via Alembic.

## Estrutura do Código

*   `app/`: Código-fonte da aplicação.
    *   `core/`: Núcleo estrutural (Configuração, Segurança, Framework de IA).
    *   `data/`: Configuração do banco (`database.py`) e arquivos estáticos da BNCC.
    *   `models/`: Definições de modelos SQLAlchemy (`student.py`, `schedule.py`, etc.).
    *   `services/`: Lógica de negócios.
        *   `DataService` (`data_service.py`): **Fachada** que centraliza o acesso aos dados.
        *   `data/`: Submódulo contendo os serviços especializados (`StudentService`, `GradeService`, etc.) que compõem o `DataService`.
        *   Outros serviços: `AssistantService`, `ReportService`, `BNCCService`.
    *   `tools/`: Implementações concretas das ferramentas do Assistente.
    *   `ui/`: Camada de apresentação (`views/`, `widgets/` e `main_app.py`).
    *   `utils/`: Utilitários compartilhados (`async_utils.py`, `student_csv_parser.py`, `charts.py`).
*   `tests/`: Testes automatizados.
*   `main.py`: Ponto de entrada (Bootstrap).

## Framework de Ferramentas do Agente

O Assistente de IA interage com o sistema exclusivamente através de ferramentas registradas.

*   **Infraestrutura:** A lógica de registro e execução reside em `app/core/tools/`.
*   **Definição:** As ferramentas concretas estão em `app/tools/` e devem ser decoradas com `@tool`.
*   **Registro:** Novas ferramentas devem ser registradas manualmente no `AssistantService`.
*   **Segurança:** O agente deve usar apenas as ferramentas fornecidas e não pode executar código arbitrário.
