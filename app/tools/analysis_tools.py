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
# Importa o módulo 'json' para converter os resultados em formato JSON.
import json
# Importa o decorador 'tool' que transforma uma função em uma ferramenta utilizável pela IA.
from app.core.tools.tool_decorator import tool
# Importa a classe DataService para interagir com o banco de dados.
from app.services.data_service import DataService

# Cria uma instância do DataService para ser usada pelas ferramentas neste módulo.
data_service = DataService()

# O decorador '@tool' registra esta função no ToolRegistry,
# gerando um esquema JSON a partir da docstring e das anotações de tipo.
# Este esquema é enviado para o LLM, permitindo que ele entenda como usar a função.
@tool
def get_student_performance_summary_tool(student_name: str, class_name: str) -> str:
    """
    Obtém um resumo detalhado do desempenho de um aluno em uma turma específica.
    Retorna as informações relevantes no formato JSON formatado, facilitando
    sua análise por ferramentas automatizadas.

    Este método consulta um serviço de dados para buscar o aluno pelo nome,
    identificar a turma especificada e obter detalhes sobre o desempenho
    acadêmico do aluno na turma. Caso ocorram erros, mensagens descritivas
    são retornadas.

    :param student_name: Nome do aluno pelo qual o desempenho será consultado.
    :type student_name: str
    :param class_name: Nome da turma para a qual será obtido o desempenho do aluno.
    :type class_name: str
    :return: Um resumo em formato JSON string contendo as informações
             de desempenho do aluno na turma especificada ou mensagens de erro
             detalhando falhas no processo.
    :rtype: str
    """
    # Bloco try/except para capturar e tratar qualquer erro inesperado que possa ocorrer.
    try:
        # Busca o aluno pelo nome usando o DataService.
        student = data_service.get_student_by_name(student_name)
        # Se o aluno não for encontrado, retorna uma mensagem de erro clara.
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        # Busca a turma pelo nome.
        target_class = data_service.get_class_by_name(class_name)

        # Se a turma não for encontrada, retorna uma mensagem de erro.
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        # Chama o DataService para obter o resumo de desempenho do aluno na turma.
        summary = data_service.get_student_performance_summary(student['id'], target_class['id'])

        # Se não for possível obter o resumo, retorna um erro.
        if not summary:
            return f"Erro: Não foi possível obter o resumo de desempenho para {student_name} em {class_name}."

        # Retorna o resumo como uma string JSON formatada.
        # O LLM pode analisar (parse) esta string facilmente para usar os dados.
        return json.dumps(summary, indent=2)
    # Captura exceções genéricas.
    except Exception as e:
        # Retorna uma mensagem de erro informando sobre a falha inesperada.
        return f"Erro: Ocorreu um erro inesperado: {e}"

@tool
def get_students_at_risk_tool(class_name: str) -> str:
    """
    Identifica e lista alunos que estão em risco em uma turma específica com base em notas baixas ou um alto número de incidentes.
    Use esta ferramenta para responder a perguntas como "Quais alunos precisam de ajuda?" ou "Mostre-me os alunos com problemas de desempenho."
    """
    try:
        # Busca a turma pelo nome.
        target_class = data_service.get_class_by_name(class_name)

        # Se a turma não for encontrada, retorna um erro.
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        # Chama o DataService para obter a lista de alunos em risco.
        students_at_risk = data_service.get_students_at_risk(target_class['id'])

        # Se a lista estiver vazia, informa que nenhum aluno foi identificado como em risco.
        if not students_at_risk:
            return f"Nenhum aluno foi identificado como em risco na turma {class_name}."

        # Retorna a lista de alunos em risco como uma string JSON formatada.
        return json.dumps(students_at_risk, indent=2)
    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"

@tool
def get_global_dashboard_stats_tool() -> str:
    """
    Obtém estatísticas globais do sistema, como total de alunos ativos, turmas, disciplinas e incidentes.
    Use esta ferramenta para responder perguntas como "Como está a escola hoje?" ou "Quantos alunos temos?".
    """
    try:
        stats = data_service.get_global_dashboard_stats()
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Erro ao obter estatísticas do painel: {e}"

@tool
def get_global_performance_stats_tool() -> str:
    """
    Obtém estatísticas globais de desempenho, incluindo taxa de aprovação, contagem de aprovados/reprovados,
    e listas de alunos em recuperação (Failed) ou destaque (Honor Roll).
    Use para visão geral da qualidade do ensino.
    """
    try:
        stats = data_service.get_global_performance_stats()
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Erro ao obter estatísticas de desempenho: {e}"

@tool
def get_class_incident_ranking_tool(limit: int = 5) -> str:
    """
    Obtém o ranking das turmas com maior número de incidentes registrados.
    Útil para identificar turmas problemáticas.

    :param limit: Número de turmas para listar (padrão 5).
    """
    try:
        ranking = data_service.get_class_incident_ranking(limit=limit)
        if not ranking:
            return "Nenhum incidente registrado no sistema."
        return json.dumps(ranking, indent=2)
    except Exception as e:
        return f"Erro ao obter ranking de incidentes: {e}"
