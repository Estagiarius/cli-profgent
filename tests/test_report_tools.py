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
import pytest
from unittest.mock import patch
from app.tools.report_tools import (
    generate_grade_chart_tool,
    generate_class_distribution_tool,
    export_class_grades_tool,
    generate_report_card_tool
)

@pytest.fixture
def mock_services():
    with patch('app.tools.report_tools.data_service') as mock_ds, \
         patch('app.tools.report_tools.report_service') as mock_rs:

        # Setup DataService mocks
        mock_ds.get_student_by_name.return_value = {"id": 1, "first_name": "João"}
        mock_ds.get_class_by_name.return_value = {"id": 10, "name": "Turma A"}

        # Setup ReportService mocks (just return fake paths)
        mock_rs.generate_student_grade_chart.return_value = "/tmp/chart.png"
        mock_rs.generate_class_grade_distribution.return_value = "/tmp/dist.png"
        mock_rs.export_class_grades_csv.return_value = "/tmp/grades.csv"
        mock_rs.generate_student_report_card.return_value = "/tmp/boletim.txt"

        yield mock_ds, mock_rs

def test_generate_grade_chart_tool_success(mock_services):
    result = generate_grade_chart_tool("João", "Turma A")
    assert "Gráfico gerado com sucesso" in result
    assert "/tmp/chart.png" in result

def test_generate_grade_chart_tool_student_not_found(mock_services):
    ds, rs = mock_services
    ds.get_student_by_name.return_value = None

    result = generate_grade_chart_tool("Fantasma", "Turma A")
    assert "Erro: Aluno 'Fantasma' não encontrado" in result

def test_generate_class_distribution_tool(mock_services):
    result = generate_class_distribution_tool("Turma A")
    assert "Gráfico de distribuição gerado" in result
    assert "/tmp/dist.png" in result

def test_export_class_grades_tool(mock_services):
    result = export_class_grades_tool("Turma A")
    assert "Arquivo CSV exportado" in result
    assert "/tmp/grades.csv" in result

def test_generate_report_card_tool(mock_services):
    result = generate_report_card_tool("João", "Turma A")
    assert "Boletim gerado com sucesso" in result
    assert "/tmp/boletim.txt" in result
