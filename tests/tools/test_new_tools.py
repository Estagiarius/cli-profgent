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
# Importa as bibliotecas e funções necessárias.
import json
import pytest
from unittest.mock import MagicMock
from app.tools.analysis_tools import get_student_performance_summary_tool, get_students_at_risk_tool
from app.tools.pedagogical_tools import suggest_lesson_activities_tool

# Define uma fixture para criar um 'mock' (simulacro) do DataService.
# Mocks são objetos falsos que simulam o comportamento de objetos reais,
# permitindo testar uma unidade de código (como uma ferramenta) isoladamente.
@pytest.fixture
def mock_data_service():
    """Fixture para criar um DataService mockado."""
    # Cria um objeto MagicMock, que pode simular qualquer método ou atributo.
    mock = MagicMock()

    # Configura o mock para simular a busca de um aluno.
    mock.get_student_by_name.return_value = {"id": 1, "first_name": "John", "last_name": "Doe"}

    # Configura o mock para simular a busca de turmas pelo nome.
    mock_class_data = {"id": 101, "name": "Math Grade 5"}
    mock.get_class_by_name.return_value = mock_class_data

    # Mantém get_all_classes mockado por precaução, mas as ferramentas atualizadas não devem usá-lo para busca por nome.
    mock.get_all_classes.return_value = [mock_class_data]

    # Retorna o objeto mockado.
    return mock

# Define uma função de teste para a ferramenta `get_student_performance_summary_tool`.
# `mocker` é uma fixture do pytest-mock, `mock_data_service` é a nossa fixture definida acima.
def test_get_student_performance_summary_tool(mocker, mock_data_service):
    # Faz o 'patch' (substituição) da instância do data_service no módulo da ferramenta
    # pelo nosso `mock_data_service`. Agora, quando a ferramenta chamar o `data_service`,
    # ela estará interagindo com o nosso mock.
    mocker.patch('app.tools.analysis_tools.data_service', mock_data_service)

    # Configura o valor de retorno esperado do método de análise específico.
    summary_data = {"student_name": "John Doe", "weighted_average": 85.5, "incident_count": 1}
    mock_data_service.get_student_performance_summary.return_value = summary_data

    # --- AÇÃO ---
    # Chama a função da ferramenta.
    result_str = get_student_performance_summary_tool("John Doe", "Math Grade 5")
    # Converte o resultado JSON (string) de volta para um dicionário Python.
    result_json = json.loads(result_str)

    # --- VERIFICAÇÕES ---
    # Verifica se os métodos mockados foram chamados com os argumentos corretos.
    mock_data_service.get_student_by_name.assert_called_with("John Doe")
    mock_data_service.get_class_by_name.assert_called_with("Math Grade 5")
    mock_data_service.get_student_performance_summary.assert_called_with(1, 101) # Verifica se os IDs corretos foram usados.
    # Verifica se os dados no resultado JSON estão corretos.
    assert result_json["weighted_average"] == 85.5
    assert result_json["student_name"] == "John Doe"

# Define uma função de teste para a ferramenta `get_students_at_risk_tool`.
def test_get_students_at_risk_tool(mocker, mock_data_service):
    mocker.patch('app.tools.analysis_tools.data_service', mock_data_service)

    # Configura o valor de retorno esperado.
    at_risk_data = [{"student_name": "Jane Doe", "reasons": ["Low grade in Math"]}]
    mock_data_service.get_students_at_risk.return_value = at_risk_data

    # --- AÇÃO ---
    result_str = get_students_at_risk_tool("Math Grade 5")
    result_json = json.loads(result_str)

    # --- VERIFICAÇÕES ---
    mock_data_service.get_class_by_name.assert_called_with("Math Grade 5")
    mock_data_service.get_students_at_risk.assert_called_with(101)
    assert len(result_json) == 1
    assert result_json[0]["student_name"] == "Jane Doe"

# Testa o cenário onde a ferramenta de alunos em risco não encontra nenhum aluno.
def test_get_students_at_risk_tool_no_students(mocker, mock_data_service):
    mocker.patch('app.tools.analysis_tools.data_service', mock_data_service)

    # Configura o mock para retornar uma lista vazia.
    mock_data_service.get_students_at_risk.return_value = []

    # --- AÇÃO ---
    result_str = get_students_at_risk_tool("Math Grade 5")

    # --- VERIFICAÇÃO ---
    # Garante que a ferramenta retorna a mensagem informativa correta, em vez de um JSON vazio.
    assert "Nenhum aluno foi identificado" in result_str

# Define um teste para a ferramenta pedagógica.
def test_suggest_lesson_activities_tool():
    # Esta ferramenta não depende de serviços externos, então não precisa de mocks.
    # Ela apenas formata uma string para o LLM.
    topic = "the solar system"
    student_level = "4th grade"
    num_suggestions = 2

    # --- AÇÃO ---
    result = suggest_lesson_activities_tool(topic, student_level, num_suggestions)

    # --- VERIFICAÇÃO ---
    # Garante que a string de saída (que é um prompt para o LLM) contém
    # os parâmetros formatados corretamente.
    assert "2 atividades de aula criativas e envolventes" in result
    assert "'the solar system'" in result
    assert "alunos de 4th grade" in result
