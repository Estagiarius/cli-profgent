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
# Importa o pytest para rodar os testes e as classes necessárias.
from datetime import date
from sqlalchemy.orm import Session
from app.services.data_service import DataService
from app.models.student import Student
from app.models.class_ import Class
from app.models.lesson import Lesson
from app.models.incident import Incident
from app.models.class_subject import ClassSubject

# Define uma função de teste. O pytest automaticamente injetará as fixtures
# `data_service` e `db_session` que foram definidas em `conftest.py`.
def test_create_lesson_and_incident(data_service: DataService, db_session: Session):
    # 1. Preparação (Setup): Cria os objetos pré-requisitos (aluno, curso, turma)
    #    usando o `data_service` para garantir que a lógica de negócios seja aplicada.
    student_dict = data_service.add_student("John", "Doe")
    assert student_dict is not None
    course_dict = data_service.add_course("Test Course", "TC101")
    assert course_dict is not None
    class_dict = data_service.create_class("Test Class") # Nova assinatura
    assert class_dict is not None

    subject_dict = data_service.add_subject_to_class(class_dict['id'], course_dict['id'])

    # Recupera os objetos ORM reais do banco de dados de teste para verificar os relacionamentos.
    # O `data_service` retorna dicionários, mas para testar `back_populates`, precisamos dos objetos SQLAlchemy.
    student = db_session.query(Student).get(student_dict['id'])
    class_ = db_session.query(Class).get(class_dict['id'])
    subject = db_session.query(ClassSubject).get(subject_dict['id'])

    # 2. Teste de Criação de Aula (Lesson)
    # Cria uma nova instância do modelo Lesson diretamente na sessão de teste.
    new_lesson = Lesson(
        date=date.today(),
        title="Introduction to Testing",
        content="This is the content of the lesson.",
        class_subject_id=subject.id # Agora vinculado ao ClassSubject
    )
    db_session.add(new_lesson)
    db_session.commit() # Salva a aula no banco de dados em memória.
    db_session.refresh(new_lesson) # Atualiza o objeto `new_lesson` com dados do banco (como o ID).

    # Verificação da criação da aula.
    assert new_lesson.id is not None # Garante que um ID foi gerado.
    assert new_lesson.title == "Introduction to Testing"
    # Garante que o relacionamento com a disciplina da turma está correto.
    assert new_lesson.class_subject.id == subject.id

    # 3. Teste de Criação de Incidente (Incident)
    # Cria uma nova instância do modelo Incident.
    new_incident = Incident(
        date=date.today(),
        description="Student was very participative.",
        class_id=class_.id,
        student_id=student.id
    )
    db_session.add(new_incident)
    db_session.commit()
    db_session.refresh(new_incident)

    # Verificação da criação do incidente.
    assert new_incident.id is not None
    assert new_incident.description == "Student was very participative."
    # Garante que os relacionamentos com a turma e o aluno estão corretos.
    assert new_incident.class_.id == class_.id
    assert new_incident.student.id == student.id

    # 4. Verificação dos Relacionamentos Inversos (back-population)
    # Atualiza os objetos `class_` e `student` com os dados mais recentes do banco
    # para garantir que as listas de relacionamentos (lessons, incidents) foram atualizadas.
    db_session.refresh(class_)
    db_session.refresh(student)
    db_session.refresh(subject)

    # Verifica se a aula recém-criada aparece na lista de aulas da disciplina.
    assert len(subject.lessons) == 1
    assert subject.lessons[0].title == "Introduction to Testing"

    # Verifica se o incidente aparece tanto na lista de incidentes da turma quanto na do aluno.
    assert len(class_.incidents) == 1
    assert len(student.incidents) == 1
    assert student.incidents[0].description == "Student was very participative."
