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
# Importa a classe 'date' para criar objetos de data para os testes.
from datetime import date
# Importa as classes de serviço e de sessão do banco para serem usadas nas fixtures.
from app.services.data_service import DataService
from sqlalchemy.orm import Session
# Importa 'io' para criar um arquivo de texto em memória.
import io

# Função auxiliar para converter uma lista de dicionários em uma string formatada como CSV.
def dict_to_csv_string(data: list[dict], header: str) -> str:
    """Converte uma lista de dicionários em uma string CSV."""
    # Usa StringIO para construir a string de forma eficiente.
    output = io.StringIO()
    # Escreve o cabeçalho do CSV.
    output.write(header + "\n")
    # Itera sobre cada dicionário (representando um aluno).
    for item in data:
        # Formata a data de nascimento para o padrão brasileiro (DD/MM/AAAA).
        if item.get("birth_date"):
            item["birth_date_str"] = item["birth_date"].strftime("%d/%m/%Y")
        else:
            item["birth_date_str"] = ""

        # Escreve a linha do aluno no formato CSV esperado pelo parser.
        output.write(f"1;{item['full_name']};{item['birth_date_str']};{item['status']}\n")

    # Retorna o conteúdo completo da string CSV.
    return output.getvalue()

# Define a função de teste principal para os cenários de importação.
def test_batch_upsert_students_and_enroll_scenarios(data_service: DataService, db_session: Session):
    """
    Testa o ciclo de vida completo da importação de alunos, garantindo que todas as
    operações ocorram dentro de uma única sessão de banco de dados consistente,
    fornecida pelas fixtures de teste.
    """
    # --- PREPARAÇÃO INICIAL ---
    # Cria uma turma de pré-requisito para os testes.
    # course = data_service.add_course("Test Course", "TC101") # Não precisa
    class_ = data_service.create_class("Test Class")
    # `flush` envia as alterações pendentes para o banco de dados de teste.
    db_session.flush()

    # Define o cabeçalho esperado pelo parser de CSV.
    header = "Nº de chamada;Nome do Aluno;Data de Nascimento;Situação do Aluno"

    # --- CENÁRIO 1: IMPORTAÇÃO INICIAL ---
    # Dados de dois alunos para a primeira importação.
    initial_student_data = [
        {"full_name": "John Doe", "first_name": "John", "last_name": "Doe", "birth_date": date(2010, 1, 1), "status": "Ativo"},
        {"full_name": "Jane Smith", "first_name": "Jane", "last_name": "Smith", "birth_date": date(2011, 2, 2), "status": "Ativo"}
    ]
    # Converte os dados para uma string CSV.
    initial_csv_content = dict_to_csv_string(initial_student_data, header)
    # Chama o método de importação do DataService.
    data_service.import_students_from_csv(class_['id'], initial_csv_content)
    db_session.flush()

    # --- VERIFICAÇÃO 1 ---
    # Busca as matrículas na turma e verifica se os dois alunos foram criados.
    enrollments = data_service.get_enrollments_for_class(class_['id'])
    assert len(enrollments) == 2
    assert data_service.get_student_count() == 2

    # Verifica os detalhes de um dos alunos importados.
    john_enrollment = next(e for e in enrollments if e['student_first_name'] == "John")
    assert john_enrollment['status'] == "Active"
    assert john_enrollment['student_birth_date'] == date(2010, 1, 1).isoformat()

    # --- CENÁRIO 2: ATUALIZAÇÃO E ADIÇÃO ---
    # Prepara um novo CSV que:
    # 1. Atualiza o status e a data de nascimento de "John Doe".
    # 2. Mantém "Jane Smith" inalterada.
    # 3. Adiciona um novo aluno, "Peter Jones".
    updated_student_data = [
        {"full_name": "John Doe", "first_name": "John", "last_name": "Doe", "birth_date": date(2010, 1, 15), "status": "Transferido"},
        {"full_name": "Jane Smith", "first_name": "Jane", "last_name": "Smith", "birth_date": date(2011, 2, 2), "status": "Ativo"},
        {"full_name": "Peter Jones", "first_name": "Peter", "last_name": "Jones", "birth_date": date(2012, 3, 3), "status": "Ativo"}
    ]
    updated_csv_content = dict_to_csv_string(updated_student_data, header)
    # Executa a importação novamente.
    data_service.import_students_from_csv(class_['id'], updated_csv_content)
    db_session.flush()

    # --- VERIFICAÇÃO 2 ---
    # Verifica se o número total de matrículas e alunos agora é 3.
    enrollments = data_service.get_enrollments_for_class(class_['id'])
    assert len(enrollments) == 3
    assert data_service.get_student_count() == 3

    # Verifica se o status do John foi atualizado para "Inactive" (mapeado de "Transferido").
    john_enrollment_updated = next(e for e in enrollments if e['student_first_name'] == "John")
    assert john_enrollment_updated['status'] == "Inactive"

    # Busca novamente o aluno John Doe para verificar se a data de nascimento foi atualizada.
    john_student_updated = data_service.get_student_by_name("John Doe")
    assert john_student_updated['birth_date'] == date(2010, 1, 15).isoformat()

    # --- CENÁRIO 3: TRATAMENTO DE DUPLICATAS NO CSV ---
    # Prepara um CSV que:
    # 1. Reverte o status de "John Doe" para "Ativo".
    # 2. Inclui "Duplicate Person" duas vezes, com status diferentes.
    #    A lógica de importação deve considerar apenas a última ocorrência ("BAIXA").
    duplicate_student_data = [
        {"full_name": "John Doe", "first_name": "John", "last_name": "Doe", "birth_date": date(2010, 1, 15), "status": "Ativo"},
        {"full_name": "Duplicate Person", "first_name": "Duplicate", "last_name": "Person", "birth_date": date(2013, 4, 4), "status": "Ativo"},
        {"full_name": "Duplicate Person", "first_name": "Duplicate", "last_name": "Person", "birth_date": date(2013, 4, 4), "status": "BAIXA"}
    ]
    duplicate_csv_content = dict_to_csv_string(duplicate_student_data, header)
    data_service.import_students_from_csv(class_['id'], duplicate_csv_content)
    db_session.flush()

    # --- VERIFICAÇÃO 3 ---
    # Verifica o número total de matrículas e alunos.
    enrollments = data_service.get_enrollments_for_class(class_['id'])
    assert len(enrollments) == 4, "Alunos que não estão no CSV não devem ser removidos"
    assert data_service.get_student_count() == 4

    # Verifica se o status de John foi revertido para "Active".
    john_final_enrollment = next(e for e in enrollments if e['student_first_name'] == "John")
    assert john_final_enrollment['status'] == "Active"

    # Verifica se o aluno duplicado foi criado corretamente e se seu status é "Inactive" (mapeado de "BAIXA").
    duplicate_enrollment = next(e for e in enrollments if e['student_first_name'] == "Duplicate")
    assert duplicate_enrollment is not None
    assert duplicate_enrollment['status'] == "Inactive"

    # 'commit' finaliza a transação do teste.
    db_session.commit()
