# -*- coding: utf-8 -*-
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

"""
Testes para o parser de CSV de alunos e a funcionalidade de importação.
"""
# Importa o pytest para rodar os testes e as classes necessárias.
import pytest
from app.services.data_service import DataService
from app.models.student import Student
from app.models.class_enrollment import ClassEnrollment

# Conteúdo de um arquivo CSV de exemplo para ser usado nos testes.
# Este mock simula um arquivo real com metadados no início, cabeçalho e dados.
MOCK_CSV_CONTENT = """
Alunos;11/11/2025 13:31

Filtros

Ano Letivo;2025

Nº de chamada;Nome do Aluno;Data de Nascimento;Situação do Aluno
1;ANA JULIA GONÇALVES;09/06/2008;Transferido
2;ANDRÉ HENRIQUE COSTA E SILVA;01/10/2009;Ativo
3;PEDRO HENRIQUE SILVA DA ROCHA;09/09/2009;Ativo
4;MARIA EDUARDA MORAES DA SILVA;03/07/2009;BAIXA - TRANSFERÊNCIA
5;JOSÉ CARLOS SANTANA;15/05/2010;Ativo

"""

# Define uma fixture que será usada pelos testes neste arquivo.
# Ela substitui a fixture `data_service` de `conftest.py` para injetar
# a sessão de banco de dados diretamente no construtor do DataService.
# Isso garante que todos os métodos, inclusive o construtor, usem a mesma sessão de teste.
@pytest.fixture
def data_service(db_session):
    """
    Fornece uma instância do DataService com a sessão de banco de dados do teste injetada.
    """
    return DataService(db_session=db_session)

# Define a função de teste para o cenário de sucesso da importação.
def test_import_students_from_csv_success(data_service: DataService, db_session):
    """
    Testa o fluxo completo de importação de CSV, verificando se os alunos
    são criados e matriculados corretamente.
    """
    # --- PREPARAÇÃO ---
    # Cria uma turma de teste para a qual os alunos serão matriculados.
    # course = data_service.add_course("Ciência da Computação - Teste CSV", "CSV-TEST-101") # Não necessário
    class_ = data_service.create_class("Turma Teste CSV")
    db_session.flush() # Garante que a turma seja criada antes da importação.

    # --- AÇÃO ---
    # Executa a função de importação com o conteúdo do CSV mockado.
    result = data_service.import_students_from_csv(class_['id'], MOCK_CSV_CONTENT)
    db_session.commit() # Salva a transação completa no banco de dados de teste.

    # --- VERIFICAÇÃO DO RESULTADO ---
    # Garante que a função reportou a importação de 5 alunos e nenhum erro.
    assert result["imported_count"] == 5
    assert not result["errors"]

    # --- VERIFICAÇÃO DO ESTADO DO BANCO ---
    # Verifica diretamente no banco se os alunos foram criados.
    all_students = db_session.query(Student).order_by(Student.first_name).all()
    assert len(all_students) == 5

    # Verifica detalhes específicos para garantir que o parsing de nomes compostos funcionou.
    # Teste de nome composto "ANA JULIA"
    ana = db_session.query(Student).filter(Student.last_name == "GONÇALVES").first()
    assert ana is not None
    assert ana.first_name == "ANA JULIA"

    # Teste de nome simples com sobrenome composto
    andre = db_session.query(Student).filter(Student.first_name == "ANDRÉ").first()
    assert andre is not None
    assert andre.last_name == "HENRIQUE COSTA E SILVA"

    # Teste de outro nome composto "PEDRO HENRIQUE"
    pedro = db_session.query(Student).filter(Student.first_name == "PEDRO HENRIQUE").first()
    assert pedro is not None
    assert pedro.last_name == "SILVA DA ROCHA"

    # Verifica se os status foram mapeados corretamente ("Ativo" -> "Active", "Transferido" -> "Inactive").
    enrollments = db_session.query(ClassEnrollment).all()
    assert len(enrollments) == 5

    active_count = sum(1 for e in enrollments if e.status == "Active")
    inactive_count = sum(1 for e in enrollments if e.status == "Inactive")
    assert active_count == 3
    assert inactive_count == 2

    # Verifica se os números de chamada foram atribuídos sequencialmente a partir de 1.
    call_numbers = sorted([e.call_number for e in enrollments])
    assert call_numbers == [1, 2, 3, 4, 5]

# Testa o comportamento da importação quando o arquivo CSV não tem o cabeçalho esperado.
def test_import_students_from_csv_invalid_header(data_service: DataService):
    """
    Testa se a importação falha corretamente quando o cabeçalho do CSV é inválido.
    """
    invalid_csv = "Coluna1;Coluna2\\nValor1;Valor2"
    # Ação: Tenta importar o CSV inválido.
    result = data_service.import_students_from_csv(1, invalid_csv)

    # Verificação: Garante que a função reportou 0 importações e um erro específico.
    assert result["imported_count"] == 0
    assert len(result["errors"]) == 1
    assert "Cabeçalho do CSV não encontrado" in result["errors"][0]

# Testa se o parser lida corretamente com alunos duplicados no mesmo arquivo.
def test_import_handles_duplicate_students(data_service: DataService, db_session):
    """
    Testa se o parser lida com alunos duplicados, importando apenas a última
    ocorrência com o status mais recente.
    """
    # CSV com a aluna 'JÚLIA NOGUEIRA RAMOS' aparecendo duas vezes com status diferentes.
    duplicate_csv = """
Nº de chamada;Nome do Aluno;Data de Nascimento;Situação do Aluno
18;JÚLIA NOGUEIRA RAMOS;28/09/2009;Transferido
19;KAIQUE ALMEIDA CLEMENTE;29/01/2010;Ativo
63;JÚLIA NOGUEIRA RAMOS;28/09/2009;Ativo
"""
    # Preparação
    # course = data_service.add_course("Português", "PT101")
    class_ = data_service.create_class("Turma Duplicatas")
    db_session.flush()

    # Ação
    result = data_service.import_students_from_csv(class_['id'], duplicate_csv)
    db_session.commit()

    # Verificação
    assert result["imported_count"] == 2 # Apenas 2 alunos únicos.
    assert not result["errors"]

    # Deve haver apenas 2 alunos e 2 matrículas no total no banco.
    students = db_session.query(Student).all()
    enrollments = db_session.query(ClassEnrollment).all()
    assert len(students) == 2
    assert len(enrollments) == 2

    # A aluna duplicada 'JÚLIA NOGUEIRA RAMOS' deve ter sido importada com o
    # status de sua ÚLTIMA aparição no arquivo, que é 'Ativo'.
    julia_enrollment = db_session.query(ClassEnrollment).join(Student).filter(
        Student.first_name == "JÚLIA"
    ).first()

    assert julia_enrollment is not None
    assert julia_enrollment.status == "Active"
