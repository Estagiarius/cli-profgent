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
# Importa as bibliotecas e classes necessárias para os testes.
from datetime import date
from sqlalchemy.orm import Session
from app.services.data_service import DataService

# Define uma função de teste para os métodos relacionados a Aulas (Lesson).
def test_lesson_methods(data_service: DataService, db_session: Session):
    # --- PREPARAÇÃO ---
    # Cria um curso e uma turma e a disciplina.
    course = data_service.add_course("Science", "SCI101")
    class_ = data_service.create_class("Grade 5 Science")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])
    today = date.today()

    # --- TESTE DE CRIAÇÃO ---
    # Ação: Cria uma nova aula vinculada à disciplina.
    lesson1 = data_service.create_lesson(subject['id'], "Photosynthesis", "Content about photosynthesis.", today)
    db_session.flush() # Envia a criação para o banco de teste.
    # Verificação: Garante que a aula foi criada com um ID.
    assert lesson1['id'] is not None

    # --- TESTE DE LEITURA (GET) ---
    # Ação: Busca as aulas da disciplina.
    lessons = data_service.get_lessons_for_subject(subject['id'])
    # Verificação: Confirma que uma aula foi encontrada e seu título está correto.
    assert len(lessons) == 1
    assert lessons[0]['title'] == "Photosynthesis"

    # --- TESTE DE ATUALIZAÇÃO (UPDATE) ---
    # Ação: Atualiza o título, conteúdo e data da aula.
    new_date = date(2024, 1, 1)
    data_service.update_lesson(lesson1['id'], "Cellular Respiration", "New content.", new_date)
    db_session.flush()

    # Verificação: Busca novamente a aula e confirma que todos os campos foram atualizados.
    updated_lessons = data_service.get_lessons_for_subject(subject['id'])
    assert updated_lessons[0]['title'] == "Cellular Respiration"
    assert updated_lessons[0]['content'] == "New content."
    assert updated_lessons[0]['date'] == new_date.isoformat()

    # --- TESTE DE EXCLUSÃO (DELETE) ---
    # Ação: Deleta a aula.
    data_service.delete_lesson(lesson1['id'])
    db_session.flush()
    # Verificação: Confirma que não há mais aulas na turma.
    lessons_after_delete = data_service.get_lessons_for_subject(subject['id'])
    assert len(lessons_after_delete) == 0

# Define uma função de teste para os métodos relacionados a Incidentes.
def test_incident_methods(data_service: DataService):
    # --- PREPARAÇÃO ---
    student = data_service.add_student("Test", "Student")
    # course = data_service.add_course("History", "HIS101")
    class_ = data_service.create_class("Grade 5 History")
    today = date.today()

    # --- TESTE DE CRIAÇÃO E LEITURA ---
    # Ação: Cria um novo incidente (vinculado à turma e aluno, independente de disciplina).
    data_service.create_incident(class_['id'], student['id'], "Excellent participation.", today)

    # Ação: Busca os incidentes da turma.
    incidents = data_service.get_incidents_for_class(class_['id'])
    # Verificação: Confirma que o incidente foi criado e associado ao aluno correto.
    assert len(incidents) == 1
    assert incidents[0]['student_first_name'] == "Test"

# Define uma função de teste para os métodos de análise de dados.
def test_analysis_methods(data_service: DataService):
    # --- PREPARAÇÃO ---
    # Cria uma estrutura complexa de dados com vários alunos, notas e incidentes
    course = data_service.add_course("Math", "MAT101")
    class_ = data_service.create_class("Grade 6 Math")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])

    # Alunos com diferentes perfis.
    student_ok = data_service.add_student("Alice", "Aventura") # Boas notas, sem incidentes
    student_low_grades = data_service.add_student("Bruno", "Baixanota") # Notas baixas
    student_high_incidents = data_service.add_student("Carlos", "Comportamento") # Muitos incidentes
    student_both = data_service.add_student("Daniela", "Desafio") # Notas baixas e muitos incidentes

    # Matricula todos os alunos na turma.
    data_service.add_student_to_class(student_ok['id'], class_['id'], 1)
    data_service.add_student_to_class(student_low_grades['id'], class_['id'], 2)
    data_service.add_student_to_class(student_high_incidents['id'], class_['id'], 3)
    data_service.add_student_to_class(student_both['id'], class_['id'], 4)

    # Cria avaliações com pesos diferentes na disciplina.
    exam1 = data_service.add_assessment(subject['id'], "Midterm Exam", 4.0) # Peso 4
    exam2 = data_service.add_assessment(subject['id'], "Final Exam", 6.0) # Peso 6

    # Adiciona notas para cada aluno.
    data_service.add_grade(student_ok['id'], exam1['id'], 8.0)
    data_service.add_grade(student_ok['id'], exam2['id'], 7.5)
    data_service.add_grade(student_low_grades['id'], exam1['id'], 4.0)
    data_service.add_grade(student_low_grades['id'], exam2['id'], 5.0)
    data_service.add_grade(student_high_incidents['id'], exam1['id'], 9.0)
    data_service.add_grade(student_high_incidents['id'], exam2['id'], 8.5)
    data_service.add_grade(student_both['id'], exam1['id'], 4.5)
    data_service.add_grade(student_both['id'], exam2['id'], 6.0)

    # Adiciona incidentes para os alunos de risco.
    today = date.today()
    data_service.create_incident(class_['id'], student_high_incidents['id'], "Disruptive behavior", today)
    data_service.create_incident(class_['id'], student_high_incidents['id'], "Late for class", today)
    data_service.create_incident(class_['id'], student_both['id'], "Forgot homework", today)
    data_service.create_incident(class_['id'], student_both['id'], "Unprepared for lesson", today)
    data_service.create_incident(class_['id'], student_both['id'], "Distracted others", today)

    # --- TESTE: get_student_performance_summary ---
    # Ação: Gera o resumo de desempenho para a aluna 'Alice'.
    summary = data_service.get_student_performance_summary(student_ok['id'], class_['id'])
    # Verificação: Confirma que o resumo foi gerado e calcula a média ponderada.
    # Média = (8.0 * 4.0 + 7.5 * 6.0) / (4.0 + 6.0) = (32 + 45) / 10 = 7.7
    assert summary is not None
    assert summary["weighted_average"] == 7.7

    # --- TESTE: get_students_at_risk (com thresholds padrão) ---
    # Ação: Busca alunos em risco com os limites padrão (média < 5.0, incidentes >= 2).
    at_risk = data_service.get_students_at_risk(class_['id'])
    # Verificação: Espera-se 3 alunos em risco:
    # - Bruno (média 4.6)
    # - Carlos (2 incidentes)
    # - Daniela (média 5.4, 3 incidentes - em risco pelos incidentes)
    assert len(at_risk) == 3

    # --- TESTE: get_students_at_risk (com thresholds personalizados) ---
    # Ação: Busca alunos em risco com limites mais rigorosos (média < 4.2, incidentes >= 3).
    at_risk_custom = data_service.get_students_at_risk(class_['id'], grade_threshold=4.2, incident_threshold=3)
    # Verificação: Com os novos limites, apenas a aluna 'Daniela' (3 incidentes) deve ser listada.
    # Bruno (média 4.6) e Carlos (2 incidentes) não atendem mais aos critérios.
    assert len(at_risk_custom) == 1
