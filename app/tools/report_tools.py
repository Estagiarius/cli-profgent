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
from app.core.tools.tool_decorator import tool
from app.services.data_service import DataService
from app.services.report_service import ReportService

data_service = DataService()
report_service = ReportService()

@tool
def generate_grade_chart_tool(student_name: str, class_name: str) -> str:
    """
    Gera um gráfico de desempenho (barras) para um aluno em uma turma e retorna o caminho do arquivo de imagem gerado.

    :param student_name: Nome do aluno.
    :param class_name: Nome da turma.
    :return: Caminho para o arquivo de imagem gerado ou mensagem de erro.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        filepath = report_service.generate_student_grade_chart(student['id'], target_class['id'])
        return f"Gráfico gerado com sucesso: {filepath}"
    except Exception as e:
        return f"Erro ao gerar gráfico: {e}"

@tool
def generate_class_distribution_tool(class_name: str) -> str:
    """
    Gera um gráfico de distribuição de notas (histograma) para uma turma e retorna o caminho do arquivo.

    :param class_name: Nome da turma.
    :return: Caminho para o arquivo de imagem gerado ou mensagem de erro.
    """
    try:
        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        filepath = report_service.generate_class_grade_distribution(target_class['id'])
        return f"Gráfico de distribuição gerado com sucesso: {filepath}"
    except Exception as e:
        return f"Erro ao gerar gráfico: {e}"

@tool
def export_class_grades_tool(class_name: str) -> str:
    """
    Gera um arquivo CSV contendo todas as notas dos alunos de uma turma.

    :param class_name: Nome da turma.
    :return: Caminho para o arquivo CSV gerado ou mensagem de erro.
    """
    try:
        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        filepath = report_service.export_class_grades_csv(target_class['id'])
        return f"Arquivo CSV exportado com sucesso: {filepath}"
    except Exception as e:
        return f"Erro ao exportar CSV: {e}"

@tool
def generate_report_card_tool(student_name: str, class_name: str) -> str:
    """
    Gera um boletim escolar em formato de texto para um aluno.

    :param student_name: Nome do aluno.
    :param class_name: Nome da turma (para identificar o contexto).
    :return: Caminho para o arquivo de texto gerado ou mensagem de erro.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
             return f"Erro: Turma '{class_name}' não encontrada."

        filepath = report_service.generate_student_report_card(student['id'], target_class['id'])
        return f"Boletim gerado com sucesso: {filepath}"
    except Exception as e:
        return f"Erro ao gerar boletim: {e}"
