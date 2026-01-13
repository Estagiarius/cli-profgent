# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
# Importa a classe base para provedores de LLM e a estrutura de resposta do assistente.
from app.core.llm.base import LLMProvider, AssistantResponse
# Importa o provedor específico para a API da OpenAI.
from app.core.llm.openai_provider import OpenAIProvider
# Importa o provedor específico para a API da Maritaca.
from app.core.llm.maritaca_provider import MaritacaProvider
# Importa o provedor específico para a API do OpenRouter.
from app.core.llm.open_router_provider import OpenRouterProvider
# Importa o provedor específico para rodar modelos localmente com Ollama.
from app.core.llm.ollama_provider import OllamaProvider
# Importa a função para obter chaves de API de forma segura.
from app.core.security.credentials import get_api_key
# Importa a função para carregar configurações salvas.
from app.core.config import load_setting
# Importa o registro de ferramentas, que gerencia as ferramentas disponíveis para a IA.
from app.core.tools.tool_registry import ToolRegistry
# Importa o executor de ferramentas, que executa as chamadas de função da IA.
from app.core.tools.tool_executor import ToolExecutor

# --- Importação das Ferramentas (Tools) ---
# Importa as ferramentas de leitura e escrita do banco de dados.
from app.tools.database_tools import (
    get_student_grades_by_course, list_courses_for_student,
    list_all_classes, get_class_roster,
    add_new_student, add_new_course, add_new_grade,
    create_new_class, add_subject_to_class, create_new_assessment,
    add_new_lesson, register_incident,
    update_student_name, enroll_existing_student,
    list_all_courses
)
# Importa as ferramentas de busca na internet.
from app.tools.internet_tools import search_internet
# Importa as ferramentas de análise de dados.
from app.tools.analysis_tools import get_student_performance_summary_tool, get_students_at_risk_tool
# Importa as ferramentas com foco pedagógico.
from app.tools.pedagogical_tools import suggest_lesson_activities_tool
# Importa as ferramentas de relatórios e gráficos.
from app.tools.report_tools import (
    generate_grade_chart_tool, generate_class_distribution_tool,
    export_class_grades_tool, generate_report_card_tool
)

# Define a classe AssistantService, que orquestra toda a lógica do assistente de IA.
class AssistantService:
    """
    Descrição da classe AssistantService.

    A classe AssistantService é responsável por gerenciar um assistente de gestão acadêmica
    integrado a um aplicativo de desktop. Ela fornece funcionalidades para lidar com um modelo
    de linguagem natural, registro e execução de ferramentas específicas atualizando um histórico
    de mensagens, bem como o gerenciamento do provedor de modelo utilizado.

    A classe trabalha com um provedor de LLM que pode ser configurado dinamicamente, executa
    ferramentas registradas conforme solicitações do usuário, e garante que o sistema opere de
    forma clara e confiável conforme o comportamento esperado.

    :ivar provider: Instância atual do provedor de LLM, que pode ser configurada como `None`
        caso nenhum provedor ativo esteja devidamente configurado.
    :type provider: LLMProvider | None
    :ivar messages: Lista de mensagens que contém o histórico da interação, incluindo mensagens do
        sistema, do usuário e do assistente.
    :type messages: list
    :ivar tool_registry: Registro que armazena todas as ferramentas disponíveis que podem ser usadas
        pelo assistente.
    :type tool_registry: ToolRegistry
    :ivar tool_executor: Executor responsável por realizar chamadas das ferramentas cadastradas no
        registro.
    :type tool_executor: ToolExecutor
    """
    # O método construtor, chamado ao criar uma nova instância do serviço.
    def __init__(self):
        # Inicializa o provedor de LLM como None. Ele será configurado depois.
        self.provider: LLMProvider | None = None
        # Inicializa a lista de mensagens, que manterá o histórico da conversa.
        self.messages: list = []

        # Cria uma instância do registro de ferramentas.
        self.tool_registry = ToolRegistry()
        # Chama o método para registrar todas as ferramentas disponíveis.
        self._register_tools()
        # Cria uma instância do executor de ferramentas, passando o registro como dependência.
        self.tool_executor = ToolExecutor(self.tool_registry)

        # Chama o método para inicializar o provedor de LLM com base nas configurações salvas.
        self._initialize_provider()

    # Método privado para registrar as ferramentas que o assistente pode usar.
    def _register_tools(self):
        # Ferramentas de leitura
        self.tool_registry.register(get_student_grades_by_course)
        self.tool_registry.register(list_courses_for_student)
        self.tool_registry.register(list_all_classes)
        self.tool_registry.register(get_class_roster)
        # Ferramentas de análise
        self.tool_registry.register(get_student_performance_summary_tool)
        self.tool_registry.register(get_students_at_risk_tool)
        # Ferramentas pedagógicas
        self.tool_registry.register(suggest_lesson_activities_tool)
        # Ferramentas de relatórios
        self.tool_registry.register(generate_grade_chart_tool)
        self.tool_registry.register(generate_class_distribution_tool)
        self.tool_registry.register(export_class_grades_tool)
        self.tool_registry.register(generate_report_card_tool)
        # Ferramentas de internet
        self.tool_registry.register(search_internet)
        # Ferramentas de escrita e outros
        self.tool_registry.register(add_new_student)
        self.tool_registry.register(add_new_course)
        self.tool_registry.register(add_new_grade)
        self.tool_registry.register(create_new_class)
        self.tool_registry.register(add_subject_to_class)
        self.tool_registry.register(create_new_assessment)
        self.tool_registry.register(add_new_lesson)
        self.tool_registry.register(register_incident)
        # Ferramentas de manutenção e matrícula
        self.tool_registry.register(update_student_name)
        self.tool_registry.register(enroll_existing_student)
        self.tool_registry.register(list_all_courses)

    # Método privado para inicializar o provedor de LLM ativo.
    def _initialize_provider(self):
        """Inicializa o provedor de LLM ativo e o modelo com base nas configurações salvas."""
        # Carrega o nome do provedor ativo salvo nas configurações, com "OpenAI" como padrão.
        active_provider_name = load_setting("active_provider", "OpenAI")
        # Define a chave para buscar o modelo específico do provedor (ex: "openai_model").
        model_config_key = f"{active_provider_name.lower()}_model"

        # Se o provedor ativo for "Ollama".
        if active_provider_name == "Ollama":
            # Carrega a URL do Ollama e o modelo selecionado.
            ollama_url = load_setting("ollama_url", "http://localhost:11434/v1")
            selected_model = load_setting(model_config_key, "llama3.1")
            # Cria a instância do provedor Ollama.
            self.provider = OllamaProvider(base_url=ollama_url, model=selected_model)
        # Para outros provedores que usam chave de API.
        else:
            # Obtém a chave de API para o provedor ativo.
            api_key = get_api_key(active_provider_name)
            # Se a chave não existir, o provedor não pode ser inicializado.
            if not api_key:
                self.provider = None; return

            # Se for "OpenAI".
            if active_provider_name == "OpenAI":
                selected_model = load_setting(model_config_key, "gpt-4")
                self.provider = OpenAIProvider(api_key=api_key, model=selected_model)
            # Se for "Maritaca".
            elif active_provider_name == "Maritaca":
                selected_model = load_setting(model_config_key, "sabia-3")
                self.provider = MaritacaProvider(api_key=api_key, model=selected_model)
            # Se for "OpenRouter".
            elif active_provider_name == "OpenRouter":
                selected_model = load_setting(model_config_key, "mistralai/mistral-7b-instruct:free")
                self.provider = OpenRouterProvider(api_key=api_key, model=selected_model)
            # Se nenhum provedor conhecido for encontrado.
            else:
                self.provider = None

        # Se um provedor foi inicializado com sucesso.
        if self.provider:
            # Define o "prompt de sistema", que são as instruções e regras fundamentais para a IA.
            system_prompt = (
                "Você é um assistente de gestão acadêmica especializado, integrado a um aplicativo de desktop. "
                "Sua função principal é ajudar os usuários a gerenciar dados de alunos, cursos e notas usando um "
                "conjunto predefinido de ferramentas. Você deve seguir as seguintes regras estritamente:\n"
                "1.  **Use Ferramentas Exclusivamente**: Você DEVE usar as ferramentas fornecidas para responder a perguntas e realizar ações. "
                "Não ofereça realizar ações que não são suportadas pelas ferramentas.\n"
                "2.  **Sem Geração de Código**: Você NÃO DEVE gerar, escrever ou sugerir qualquer código (ex: Python, SQL). "
                "Seu papel é usar as ferramentas, não ser um programador.\n"
                "3.  **Admita Limitações**: Se você não puder atender a uma solicitação com as ferramentas disponíveis, declare claramente que "
                "não pode fazê-lo e explique a limitação. Não invente ferramentas ou funcionalidades.\n"
                "4.  **Clareza e Confirmação**: Após executar uma ferramenta que modifica dados (ex: adicionar um aluno), "
                "sempre confirme o sucesso da ação em uma mensagem clara e amigável, com base na saída da ferramenta.\n"
                "5.  **Planejamento de Aulas**: Se o usuário solicitar a criação de um plano de aula, gere primeiro o conteúdo "
                "estruturado (Objetivos, Conteúdo, Atividades, Avaliação) no chat. Após a aprovação do usuário, "
                "use a ferramenta `add_new_lesson` para salvar esse conteúdo na disciplina e turma apropriadas."
            )
            # Inicia o histórico de mensagens com o prompt de sistema.
            self.messages = [{"role": "system", "content": system_prompt}]

    # Método assíncrono para obter uma resposta do assistente.
    async def get_response(self, user_input: str) -> AssistantResponse:
        # Garante que o provedor esteja atualizado com as últimas configurações.
        self._initialize_provider()
        # Se nenhum provedor estiver configurado, retorna uma mensagem de erro.
        if not self.provider:
            return AssistantResponse(content="Provedor de IA não configurado...")

        # Adiciona a mensagem do usuário ao histórico da conversa.
        self.messages.append({"role": "user", "content": user_input})

        # Passo 1: Obter a resposta inicial do modelo.
        # Envia os esquemas das ferramentas se o provedor suportar (OpenAI, OpenRouter, Ollama).
        tool_schemas = self.tool_registry.get_all_schemas() if self.provider.name in ["OpenAI", "OpenRouter", "Ollama"] else None
        response = await self.provider.get_chat_response(self.messages, tools=tool_schemas)

        # Passo 2: Verificar se o modelo quer chamar uma ferramenta.
        if not response.tool_calls:
            # Se não houver chamadas de ferramenta, temos nossa resposta final.
            if response.content:
                # Adiciona a resposta do assistente ao histórico.
                self.messages.append({"role": "assistant", "content": response.content})
            return response

        # Passo 3: Executar a ferramenta e obter o resultado.
        # Garante que a lista de chamadas de ferramenta seja sempre uma lista.
        tool_calls_list = response.tool_calls if isinstance(response.tool_calls, list) else [response.tool_calls]
        # Adiciona a intenção de chamada de ferramenta ao histórico.
        self.messages.append({"role": "assistant", "tool_calls": tool_calls_list})

        # Lista para armazenar os resultados das ferramentas.
        tool_results = []
        # Itera sobre cada chamada de ferramenta solicitada pelo modelo.
        for tool_call in tool_calls_list:
            # Executa a ferramenta e armazena o resultado.
            result = self.tool_executor.execute_tool_call(tool_call)
            tool_results.append(result)

        # Passo 4: Adicionar os resultados das ferramentas ao histórico e obter a resposta final em linguagem natural.
        self.messages.extend(tool_results)

        # Envia a conversa atualizada (com os resultados) para o modelo.
        final_response = await self.provider.get_chat_response(self.messages, tools=tool_schemas)
        # Se houver conteúdo na resposta final, adiciona ao histórico.
        if final_response.content:
            self.messages.append({"role": "assistant", "content": final_response.content})
        # Retorna a resposta final para a interface do usuário.
        return final_response

    # Método assíncrono para fechar a conexão do provedor de LLM.
    async def close(self):
        """Fecha os recursos do provedor de LLM subjacente."""
        # Se um provedor estiver ativo.
        if self.provider:
            # Chama o método 'close' do provedor para liberar conexões de rede.
            await self.provider.close()

    async def generate_lesson_content(self, topic: str, course_name: str, class_name: str) -> str:
        """
        Gera uma sugestão de plano de aula baseada no tópico, disciplina e turma.
        """
        if not self.provider:
            self._initialize_provider()
            if not self.provider:
                return "Erro: Provedor de IA não configurado."

        system_prompt = (
            "Você é um especialista pedagógico. Sua tarefa é criar um plano de aula detalhado e estruturado. "
            "A saída deve ser texto formatado (não Markdown complexo, mas com quebras de linha e seções claras) "
            "adequado para ser colado em um campo de texto simples.\n"
            "Estrutura Obrigatória:\n"
            "1. Objetivos de Aprendizagem\n"
            "2. Conteúdo/Tópicos a Abordar\n"
            "3. Sugestão de Atividades Práticas\n"
            "4. Avaliação/Verificação de Aprendizado\n\n"
            "Seja direto e prático. Adapte a linguagem à disciplina e nível escolar (inferido pelo nome da turma)."
        )

        user_prompt = f"Crie um plano de aula para a disciplina '{course_name}' da turma '{class_name}' sobre o tema: '{topic}'."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Chamada direta ao provedor, sem usar tools, pois queremos apenas geração de texto.
        response = await self.provider.get_chat_response(messages)
        return response.content if response.content else "Não foi possível gerar o conteúdo."
