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
# Importa a classe 'date' para usar nasfixtures de teste.
from datetime import date
# Importa a classe DataService para ser testada.
from app.services.data_service import DataService

# Cada função de teste recebe a fixture `data_service` como argumento.
# Esta fixture (de conftest.py) fornece uma instância limpa do serviço
# conectada a um banco de dados em memória para cada teste.

def test_add_student(data_service: DataService):
    """Testa a adição de um novo aluno."""
    # Ação: Adiciona um novo aluno.
    data_service.add_student("John", "Doe")
    # Verificação: Confirma que a contagem de alunos no banco agora é 1.
    assert data_service.get_student_count() == 1

def test_add_student_with_birth_date(data_service: DataService):
    """Testa a adição de um novo aluno com data de nascimento."""
    birth_date = date(2005, 5, 15)
    # Ação: Adiciona um aluno com data de nascimento.
    student = data_service.add_student("Jane", "Doe", birth_date=birth_date)
    # Verificação: Confirma que a data de nascimento retornada está correta e no formato ISO.
    assert student['birth_date'] == birth_date.isoformat()

def test_add_course(data_service: DataService):
    """Testa a adição de um novo curso."""
    data_service.add_course("Math 101", "MATH101")
    assert data_service.get_course_count() == 1

def test_add_assessment(data_service: DataService):
    """Testa a adição de uma nova avaliação."""
    # Preparação: Cria um curso e uma turma e associa.
    course = data_service.add_course("Science 101", "SCI101")
    class_ = data_service.create_class("1A") # Nova assinatura: apenas nome
    subject = data_service.add_subject_to_class(class_['id'], course['id'])

    # Ação: Adiciona uma avaliação à disciplina da turma.
    assessment = data_service.add_assessment(subject['id'], "Midterm", 1.0)
    # Verificação: Confirma que os dados da avaliação estão corretos.
    assert assessment['name'] == "Midterm"
    assert assessment['class_subject_id'] == subject['id']

def test_add_grade(data_service: DataService):
    """Testa a adição de uma nova nota."""
    # Preparação: Cria aluno, curso, turma, disciplina, avaliação e matricula o aluno.
    student = data_service.add_student("Jane", "Doe")
    course = data_service.add_course("Science 101", "SCI101")
    class_ = data_service.create_class("1A")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])

    assessment = data_service.add_assessment(subject['id'], "Midterm", 1.0)
    data_service.add_student_to_class(student['id'], class_['id'], 1)

    # Ação: Adiciona uma nota para o aluno na avaliação.
    data_service.add_grade(student['id'], assessment['id'], 8.55)

    # Verificação: Confirma que a nota foi salva corretamente.
    grades = data_service.get_grades_for_subject(subject['id'])
    assert len(grades) == 1
    assert grades[0]['score'] == 8.55

def test_get_all_students(data_service: DataService):
    """Testa a busca de todos os alunos."""
    # Preparação: Adiciona dois alunos.
    data_service.add_student("John", "Doe")
    data_service.add_student("Jane", "Smith")
    # Verificação: Confirma que o método retorna 2 alunos.
    assert len(data_service.get_all_students()) == 2

def test_update_student(data_service: DataService, db_session):
    """Testa a atualização das informações de um aluno."""
    # Preparação: Adiciona um aluno com um nome incorreto.
    student = data_service.add_student("Jon", "Doe")
    db_session.flush() # Garante que a criação inicial seja enviada ao banco.
    # Ação: Atualiza o nome do aluno.
    data_service.update_student(student['id'], "John", "Doe")
    db_session.flush() # Garante que a atualização seja enviada.
    # Verificação: Confirma que o nome antigo não é mais encontrado e o novo nome é.
    assert data_service.get_student_by_name("Jon Doe") is None
    updated_student = data_service.get_student_by_name("John Doe")
    assert updated_student is not None
    assert updated_student['first_name'] == "John"

def test_delete_student(data_service: DataService, db_session):
    """Testa a exclusão de um aluno e suas notas associadas."""
    # Preparação: Cria um aluno e uma nota para ele.
    student = data_service.add_student("John", "Doe")
    course = data_service.add_course("History 101", "HIST101")
    class_ = data_service.create_class("1A")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])
    assessment = data_service.add_assessment(subject['id'], "Final Exam", 1.0)
    data_service.add_grade(student['id'], assessment['id'], 9.2)
    db_session.flush()

    assert data_service.get_student_count() == 1
    assert len(data_service.get_all_grades()) == 1
    # Ação: Deleta o aluno.
    data_service.delete_student(student['id'])
    db_session.flush()
    # Verificação: Confirma que o aluno e sua nota foram removidos.
    assert data_service.get_student_count() == 0
    assert len(data_service.get_all_grades()) == 0

def test_get_student_by_name(data_service: DataService):
    """Testa a busca de um aluno pelo nome (ignorando maiúsculas/minúsculas)."""
    data_service.add_student("John", "Doe")
    assert data_service.get_student_by_name("john doe") is not None
    assert data_service.get_student_by_name("Jane Doe") is None

def test_create_class(data_service: DataService):
    """Testa a criação de uma nova turma."""
    # course = data_service.add_course("Biology 101", "BIO101") # Não é mais necessário
    data_service.create_class("1A")
    assert len(data_service.get_all_classes()) == 1

def test_add_student_to_class(data_service: DataService):
    """Testa a matrícula de um aluno em uma turma."""
    student = data_service.add_student("Alice", "Wonderland")
    # course = data_service.add_course("Literature", "LIT101") # Não é mais necessário
    class_ = data_service.create_class("2B")
    # Ação: Matricula o aluno.
    enrollment = data_service.add_student_to_class(student['id'], class_['id'], 1)
    # Verificação: Confirma que os IDs na matrícula estão corretos.
    assert enrollment['student_id'] == student['id']
    assert enrollment['class_id'] == class_['id']

def test_get_students_in_class(data_service: DataService):
    """Testa a busca de todos os alunos matriculados em uma turma."""
    student1 = data_service.add_student("Student", "One")
    student2 = data_service.add_student("Student", "Two")
    # course = data_service.add_course("Gym", "GYM101") # Não é mais necessário
    class_ = data_service.create_class("3C")
    data_service.add_student_to_class(student1['id'], class_['id'], 1)
    data_service.add_student_to_class(student2['id'], class_['id'], 2)
    enrolled_students = data_service.get_enrollments_for_class(class_['id'])
    assert len(enrolled_students) == 2

def test_update_enrollment_status(data_service: DataService, db_session):
    """Testa a atualização do status de uma matrícula."""
    student = data_service.add_student("Student", "One")
    # course = data_service.add_course("Course", "C101") # Não é mais necessário
    class_ = data_service.create_class("Class")
    enrollment = data_service.add_student_to_class(student['id'], class_['id'], 1)
    db_session.flush()
    assert enrollment['status'] == "Active"
    # Ação: Atualiza o status para "Inativo".
    data_service.update_enrollment_status(enrollment['id'], "Inactive")
    db_session.flush()
    # Verificação: Busca novamente a matrícula e confirma a mudança de status.
    updated_enrollment = data_service.get_enrollments_for_class(class_['id'])[0]
    assert updated_enrollment['status'] == "Inactive"

def test_get_unenrolled_students(data_service: DataService):
    """Testa a busca de alunos não matriculados em uma turma específica."""
    student1 = data_service.add_student("Enrolled", "Student")
    data_service.add_student("Unenrolled", "Student")
    # course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class")
    data_service.add_student_to_class(student1['id'], class_['id'], 1)
    # Ação: Busca os alunos não matriculados.
    unenrolled = data_service.get_unenrolled_students(class_['id'])
    # Verificação: Confirma que apenas o aluno não matriculado foi retornado.
    assert len(unenrolled) == 1
    assert unenrolled[0]['first_name'] == "Unenrolled"

def test_get_students_with_active_enrollment(data_service: DataService):
    """Testa a busca de alunos que têm pelo menos uma matrícula ativa."""
    student_active = data_service.add_student("Active", "Student")
    student_inactive = data_service.add_student("Inactive", "Student")
    data_service.add_student("None", "Student") # Aluno sem matrícula
    # course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class")
    data_service.add_student_to_class(student_active['id'], class_['id'], 1, status="Active")
    data_service.add_student_to_class(student_inactive['id'], class_['id'], 2, status="Inactive")
    # Ação: Busca os alunos ativos.
    active_students = data_service.get_students_with_active_enrollment()
    # Verificação: Confirma que apenas o aluno com matrícula ativa foi retornado.
    assert len(active_students) == 1
    assert active_students[0]['first_name'] == "Active"

def test_get_next_call_number(data_service: DataService):
    """Testa o cálculo do próximo número de chamada para uma turma."""
    student1 = data_service.add_student("Student", "One")
    # course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class")
    # Verificação 1: Turma vazia, próximo número deve ser 1.
    assert data_service.get_next_call_number(class_['id']) == 1
    # Preparação: Adiciona um aluno com número de chamada 5.
    data_service.add_student_to_class(student1['id'], class_['id'], 5)
    # Verificação 2: Próximo número deve ser 6 (o máximo atual + 1).
    assert data_service.get_next_call_number(class_['id']) == 6

def test_get_grades_for_class_filters_inactive_students(data_service: DataService):
    """Testa se get_grades_for_subject retorna apenas notas de alunos ativos."""
    student_active = data_service.add_student("Active", "Student")
    student_inactive = data_service.add_student("Inactive", "Student")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])
    assessment = data_service.add_assessment(subject['id'], "Test", 1.0)

    data_service.add_student_to_class(student_active['id'], class_['id'], 1, status="Active")
    data_service.add_student_to_class(student_inactive['id'], class_['id'], 2, status="Inactive")

    data_service.add_grade(student_active['id'], assessment['id'], 10.0)
    data_service.add_grade(student_inactive['id'], assessment['id'], 5.0)

    # Ação: Busca as notas da disciplina.
    grades = data_service.get_grades_for_subject(subject['id'])
    # Verificação: Confirma que apenas a nota do aluno ativo foi retornada.
    assert len(grades) == 1
    assert grades[0]['student_id'] == student_active['id']

def test_update_assessment(data_service: DataService, db_session):
    """Testa a atualização das informações de uma avaliação."""
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])

    assessment = data_service.add_assessment(subject['id'], "Old Name", 1.0)
    db_session.flush()
    # Ação: Atualiza o nome e o peso da avaliação.
    data_service.update_assessment(assessment['id'], "New Name", 2.0)
    db_session.flush()
    # Verificação: Busca novamente a avaliação e confirma as mudanças.
    updated_assessments = data_service.get_assessments_for_subject(subject['id'])
    assert updated_assessments[0]['name'] == "New Name"
    assert updated_assessments[0]['weight'] == 2.0

def test_delete_assessment(data_service: DataService, db_session):
    """Testa a exclusão de uma avaliação e suas notas associadas."""
    student = data_service.add_student("Student", "One")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])

    assessment = data_service.add_assessment(subject['id'], "Test to Delete", 1.0)
    data_service.add_student_to_class(student['id'], class_['id'], 1)
    data_service.add_grade(student['id'], assessment['id'], 10.0)
    db_session.flush()

    assert len(data_service.get_assessments_for_subject(subject['id'])) == 1
    assert len(data_service.get_all_grades()) == 1

    # Ação: Deleta a avaliação.
    data_service.delete_assessment(assessment['id'])
    db_session.flush()

    # Verificação: Confirma que a avaliação e a nota foram removidas.
    assert len(data_service.get_assessments_for_subject(subject['id'])) == 0
    assert len(data_service.get_all_grades()) == 0

def test_grade_grid_logic(data_service: DataService, db_session):
    """Testa o cálculo da média ponderada e a funcionalidade de upsert de notas."""
    # Preparação: Cria alunos, turma e avaliações com pesos diferentes.
    student1 = data_service.add_student("Student", "One")
    student2 = data_service.add_student("Student", "Two")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])

    data_service.add_student_to_class(student1['id'], class_['id'], 1)
    data_service.add_student_to_class(student2['id'], class_['id'], 2)

    assess1 = data_service.add_assessment(subject['id'], "Test 1", 1.0) # Peso 1
    assess2 = data_service.add_assessment(subject['id'], "Test 2", 2.0) # Peso 2
    assessments = [assess1, assess2]

    # Ação 1: Adiciona uma nota para o aluno 1.
    data_service.add_grade(student1['id'], assess1['id'], 8.0)
    db_session.flush()

    grades = data_service.get_grades_for_subject(subject['id'])
    # Verificação 1: Calcula a média ponderada. (8.0 * 1.0 + 0.0 * 2.0) / (1.0 + 2.0) = 8/3 = 2.67
    avg1 = data_service.calculate_weighted_average(student1['id'], grades, assessments)
    assert round(avg1, 2) == 2.67

    # Verificação 2: Aluno 2 não tem notas, a média é 0.
    avg2 = data_service.calculate_weighted_average(student2['id'], grades, assessments)
    assert avg2 == 0.0

    # Ação 2: Usa o upsert para atualizar uma nota e adicionar duas novas.
    grades_to_upsert = [
        {'student_id': student1['id'], 'assessment_id': assess1['id'], 'score': 9.0}, # Atualiza
        {'student_id': student1['id'], 'assessment_id': assess2['id'], 'score': 7.0}, # Adiciona
        {'student_id': student2['id'], 'assessment_id': assess1['id'], 'score': 10.0} # Adiciona
    ]
    data_service.upsert_grades_for_subject(subject['id'], grades_to_upsert)
    db_session.flush()

    # Verificação 3: Calcula as novas médias.
    final_grades = data_service.get_grades_for_subject(subject['id'])
    assert len(final_grades) == 3

    # Média Aluno 1: (9.0 * 1.0 + 7.0 * 2.0) / 3 = 23/3 = 7.67
    final_avg1 = data_service.calculate_weighted_average(student1['id'], final_grades, assessments)
    assert round(final_avg1, 2) == 7.67
    # Média Aluno 2: (10.0 * 1.0 + 0.0 * 2.0) / 3 = 10/3 = 3.33
    final_avg2 = data_service.calculate_weighted_average(student2['id'], final_grades, assessments)
    assert round(final_avg2, 2) == 3.33

def test_update_and_delete_class(data_service: DataService, db_session):
    """Testa a atualização e exclusão de uma turma."""
    student = data_service.add_student("Student", "One")
    # course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Old Name")
    data_service.add_student_to_class(student['id'], class_['id'], 1)
    db_session.flush()
    # Ação 1: Atualiza o nome da turma.
    data_service.update_class(class_['id'], "New Name")
    db_session.flush()
    # Verificação 1: Confirma a mudança de nome.
    updated_class = data_service.get_class_by_id(class_['id'])
    assert updated_class['name'] == "New Name"
    assert len(data_service.get_all_classes()) == 1
    assert len(data_service.get_enrollments_for_class(class_['id'])) == 1
    # Ação 2: Deleta a turma.
    data_service.delete_class(class_['id'])
    db_session.flush()
    # Verificação 2: Confirma que a turma e a matrícula foram removidas.
    assert len(data_service.get_all_classes()) == 0
    assert len(data_service.get_enrollments_for_class(class_['id'])) == 0

def test_get_all_grades_with_details(data_service: DataService):
    """Testa a busca de todas as notas com seus detalhes relacionais completos."""
    # Preparação: Cria a estrutura completa de dados (aluno -> turma -> disciplina, nota -> avaliação -> disciplina).
    student = data_service.add_student("Student", "One")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])

    assessment = data_service.add_assessment(subject['id'], "Final Exam", 1.0)
    data_service.add_student_to_class(student['id'], class_['id'], 1)

    grade = data_service.add_grade(student['id'], assessment['id'], 9.5)
    # Ação: Chama o método que busca notas com detalhes.
    grades_with_details = data_service.get_all_grades_with_details()
    # Verificação: Confirma que a nota foi retornada com todos os detalhes esperados.
    assert len(grades_with_details) == 1
    retrieved_grade = grades_with_details[0]
    assert retrieved_grade['id'] == grade['id']
    assert retrieved_grade['student_first_name'] == "Student"
    assert retrieved_grade['assessment_name'] == "Final Exam"
    assert retrieved_grade['class_name'] == "Class"
    assert retrieved_grade['course_name'] == "Course"
