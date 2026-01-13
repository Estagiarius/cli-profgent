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
from datetime import datetime
import json
from sqlalchemy.exc import SQLAlchemyError
from app.core.tools.tool_decorator import tool
from app.services import data_service

# --- READ TOOLS ---

@tool
def global_search_tool(search_term: str) -> str:
    """
    Realiza uma busca global no sistema por um termo.
    Procura em Alunos, Turmas e Disciplinas.

    :param search_term: O termo a ser pesquisado (ex: "Ana", "Matemática").
    :return: Um resumo dos resultados encontrados.
    """
    try:
        results = []
        term = search_term.lower()

        # Busca em Alunos
        students = data_service.get_paginated_students(1, 100, search_term=term)['students']
        if students:
            results.append("Alunos encontrados:")
            for s in students:
                results.append(f"- {s['first_name']} {s['last_name']}")

        # Busca em Turmas (filtro simples em memória pois não temos search_classes no service ainda)
        all_classes = data_service.get_all_classes()
        found_classes = [c for c in all_classes if term in c['name'].lower()]
        if found_classes:
            results.append("\nTurmas encontradas:")
            for c in found_classes:
                results.append(f"- {c['name']}")

        # Busca em Disciplinas
        all_courses = data_service.get_all_courses()
        found_courses = [c for c in all_courses if term in c['course_name'].lower() or term in c['course_code'].lower()]
        if found_courses:
            results.append("\nDisciplinas encontradas:")
            for c in found_courses:
                results.append(f"- {c['course_name']} ({c['course_code']})")

        if not results:
            return f"Nenhum resultado encontrado para '{search_term}' em Alunos, Turmas ou Disciplinas."

        return "\n".join(results)

    except Exception as e:
        return f"Erro na busca global: {e}"

@tool
def get_class_full_details_tool(class_name: str) -> str:
    """
    Obtém TODOS os detalhes de uma turma: alunos (com status), disciplinas e avaliações.
    Retorna um JSON complexo ideal para análise detalhada.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        # Get Subjects and Assessments
        subjects = data_service.get_subjects_for_class(cls['id'])
        subjects_data = []
        for s in subjects:
            assessments = data_service.get_assessments_for_subject(s['id'])
            subjects_data.append({
                "name": s['course_name'],
                "assessments": [{"name": a['name'], "weight": a['weight']} for a in assessments]
            })

        # Get Enrollments
        enrollments = data_service.get_enrollments_for_class(cls['id'])
        students_data = [{
            "name": f"{e['student_first_name']} {e['student_last_name']}",
            "call_number": e['call_number'],
            "status": e['status']
        } for e in enrollments]

        result = {
            "class_name": cls['name'],
            "subjects": subjects_data,
            "students": students_data
        }
        return json.dumps(result, indent=2)
    except Exception as e: return f"Erro ao obter detalhes da turma: {e}"

@tool
def get_student_grades_by_course(student_name: str, course_name: str) -> str:
    """
    Obtém as notas de um aluno específico em uma disciplina (curso) específica.

    :param student_name: Nome do aluno.
    :param course_name: Nome da disciplina (ex: "Matemática").
    :return: Lista de notas encontradas.
    """
    student = data_service.get_student_by_name(student_name)
    if not student:
        return f"Aluno '{student_name}' não encontrado."

    course = data_service.get_course_by_name(course_name)
    if not course:
        return f"Disciplina '{course_name}' não encontrada."

    # Busca todas as notas detalhadas e filtra
    all_grades = data_service.get_all_grades_with_details()
    student_grades = [
        g for g in all_grades
        if g['student_id'] == student['id'] and g['course_id'] == course['id']
    ]

    if not student_grades:
        return f"Nenhuma nota encontrada para {student_name} em {course_name}."

    result = [f"Notas de {student_name} em {course_name}:"]
    for g in student_grades:
        result.append(f"- Turma: {g['class_name']} | Avaliação: {g['assessment_name']} | Nota: {g['score']}")

    return "\n".join(result)

@tool
def list_courses_for_student(student_name: str) -> str:
    """
    Lista as disciplinas nas quais o aluno possui algum registro de nota ou atividade.

    :param student_name: O nome do aluno.
    """
    student = data_service.get_student_by_name(student_name)
    if not student:
        return f"Aluno '{student_name}' não encontrado."

    # Como a matrícula é por Turma, e a Turma tem várias disciplinas,
    # listar as disciplinas "do aluno" significa listar as disciplinas das turmas onde ele está matriculado.

    # Precisamos iterar todas as turmas para achar as matrículas desse aluno
    # (Idealmente o DataService teria get_student_enrollments, mas vamos usar o que tem)
    classes = data_service.get_all_classes()
    student_courses = set()

    for cls in classes:
        class_enrollments = data_service.get_enrollments_for_class(cls['id'])
        if any(e['student_id'] == student['id'] for e in class_enrollments):
            # O aluno está nesta turma. Pega as disciplinas da turma.
            subjects = data_service.get_subjects_for_class(cls['id'])
            for s in subjects:
                student_courses.add(s['course_name'])

    if not student_courses:
        return f"{student_name} não está matriculado em turmas com disciplinas cadastradas."

    return f"Disciplinas de {student_name}:\n" + "\n".join(f"- {name}" for name in sorted(list(student_courses)))

@tool
def list_all_classes() -> str:
    """
    Lista todas as turmas cadastradas no sistema e suas disciplinas.
    """
    try:
        classes = data_service.get_all_classes()
        if not classes:
            return "Não há turmas cadastradas no sistema."

        result = []
        for cls in classes:
            subjects = data_service.get_subjects_for_class(cls['id'])
            subject_names = [s['course_name'] for s in subjects]
            subjects_str = ", ".join(subject_names) if subject_names else "Nenhuma disciplina"

            result.append(f"Turma: {cls['name']} | Alunos: {cls['student_count']} | Disciplinas: {subjects_str}")

        return "\n".join(result)
    except Exception as e:
        return f"Erro ao listar turmas: {e}"

@tool
def get_class_roster(class_name: str) -> str:
    """
    Obtém a lista de chamada (roster) de uma turma específica.
    """
    try:
        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        enrollments = data_service.get_enrollments_for_class(target_class['id'])

        if not enrollments:
            return f"A turma '{class_name}' não possui alunos matriculados."

        result = [f"Lista de Chamada para a Turma: {class_name}"]
        for env in enrollments:
            line = f"#{env['call_number']} - {env['student_first_name']} {env['student_last_name']} ({env['status']})"
            result.append(line)

        return "\n".join(result)
    except Exception as e:
        return f"Erro ao obter lista de alunos: {e}"

@tool
def get_incidents_for_class(class_name: str) -> str:
    """
    Lista todos os incidentes registrados para uma turma.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        incidents = data_service.get_incidents_for_class(cls['id'])
        if not incidents: return f"Nenhum incidente registrado para a turma '{class_name}'."

        result = [f"Incidentes da turma {class_name}:"]
        for inc in incidents:
            date_fmt = datetime.strptime(inc['date'], "%Y-%m-%d").strftime("%d/%m/%Y")
            result.append(f"- {date_fmt}: {inc['student_first_name']} {inc['student_last_name']} - {inc['description']}")
        return "\n".join(result)
    except Exception as e: return f"Erro: {e}"

@tool
def get_assessments_for_subject(class_name: str, subject_name: str) -> str:
    """
    Lista as avaliações cadastradas em uma disciplina de uma turma.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)

        if not target_subject: return f"Disciplina '{subject_name}' não encontrada na turma."

        assessments = data_service.get_assessments_for_subject(target_subject['id'])
        if not assessments: return f"Nenhuma avaliação cadastrada para {subject_name}."

        result = [f"Avaliações de {subject_name} ({class_name}):"]
        for a in assessments:
            result.append(f"- {a['name']} (Peso: {a['weight']})")
        return "\n".join(result)
    except Exception as e: return f"Erro: {e}"

@tool
def get_lessons_for_subject(class_name: str, subject_name: str) -> str:
    """
    Lista as aulas registradas em uma disciplina de uma turma.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)
        if not target_subject: return f"Disciplina '{subject_name}' não encontrada na turma."

        lessons = data_service.get_lessons_for_subject(target_subject['id'])
        if not lessons: return f"Nenhuma aula registrada para {subject_name}."

        result = [f"Aulas de {subject_name} ({class_name}):"]
        for l in lessons:
            date_fmt = datetime.strptime(l['date'], "%Y-%m-%d").strftime("%d/%m/%Y")
            result.append(f"- {date_fmt}: {l['title']} - {l['content']}")
        return "\n".join(result)
    except Exception as e: return f"Erro: {e}"

@tool
def get_unenrolled_students(class_name: str) -> str:
    """
    Lista alunos que NÃO estão matriculados na turma especificada.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        students = data_service.get_unenrolled_students(cls['id'])
        if not students: return "Todos os alunos do sistema já estão matriculados nesta turma."

        return "Alunos não matriculados:\n" + "\n".join([f"- {s['first_name']} {s['last_name']}" for s in students])
    except Exception as e: return f"Erro: {e}"

@tool
def get_students_with_birthday_today() -> str:
    """
    Lista os alunos que fazem aniversário hoje.
    """
    try:
        students = data_service.get_students_with_birthday_today()
        if not students: return "Nenhum aluno faz aniversário hoje."
        return "Aniversariantes de hoje:\n" + "\n".join([f"- {s['name']} (Turma: {s['class_name']}) - {s['age']} anos" for s in students])
    except Exception as e: return f"Erro: {e}"

@tool
def search_students(search_term: str) -> str:
    """
    Busca alunos pelo nome (parcial).
    """
    try:
        result = data_service.get_paginated_students(page=1, page_size=50, search_term=search_term)
        students = result['students']
        if not students: return f"Nenhum aluno encontrado com '{search_term}'."
        return "\n".join([f"- {s['first_name']} {s['last_name']}" for s in students])
    except Exception as e: return f"Erro: {e}"

# --- WRITE TOOLS ---

@tool
def import_students_csv_tool(class_name: str, csv_content: str) -> str:
    """
    Importa uma lista de alunos a partir de um texto CSV para uma turma específica.
    O CSV deve ter cabeçalho (ex: Full Name,Birth Date,Status) ou seguir o padrão da escola.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        result = data_service.import_students_from_csv(cls['id'], csv_content)
        imported = result.get('imported_count', 0)
        errors = result.get('errors', [])

        msg = f"Importação concluída. {imported} alunos importados/atualizados."
        if errors:
            msg += f"\nErros ({len(errors)}): " + "; ".join(errors[:3])
            if len(errors) > 3: msg += "..."
        return msg
    except Exception as e: return f"Erro na importação: {e}"

@tool
def transfer_student_tool(student_name: str, from_class_name: str, to_class_name: str) -> str:
    """
    Transfere um aluno de uma turma para outra.
    O aluno será marcado como 'Inactive' na turma antiga e matriculado como 'Active' na nova.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student: return "Aluno não encontrado."

        from_cls = data_service.get_class_by_name(from_class_name)
        if not from_cls: return f"Turma de origem '{from_class_name}' não encontrada."

        to_cls = data_service.get_class_by_name(to_class_name)
        if not to_cls: return f"Turma de destino '{to_class_name}' não encontrada."

        # Find old enrollment
        enrollments = data_service.get_enrollments_for_class(from_cls['id'])
        old_enrollment = next((e for e in enrollments if e['student_id'] == student['id']), None)

        if not old_enrollment:
            return f"Aluno {student_name} não está matriculado na turma {from_class_name}."

        # Inactivate old
        data_service.update_enrollment_status(old_enrollment['id'], "Inactive")

        # Create new enrollment
        next_num = data_service.get_next_call_number(to_cls['id'])
        data_service.add_student_to_class(student['id'], to_cls['id'], next_num, "Active")

        return f"Transferência realizada com sucesso: {student_name} movido de {from_class_name} para {to_class_name}."

    except Exception as e: return f"Erro na transferência: {e}"

@tool
def copy_class_structure_tool(source_class_name: str, target_class_name: str) -> str:
    """
    Copia a estrutura (Disciplinas e Avaliações) de uma turma para outra.
    Útil para configurar rapidamente uma nova turma baseada em uma existente.
    """
    try:
        source_cls = data_service.get_class_by_name(source_class_name)
        if not source_cls: return f"Turma de origem '{source_class_name}' não encontrada."

        target_cls = data_service.get_class_by_name(target_class_name)
        if not target_cls: return f"Turma de destino '{target_class_name}' não encontrada."

        subjects = data_service.get_subjects_for_class(source_cls['id'])
        copied_subjects = 0
        copied_assessments = 0

        for subj in subjects:
            # Add subject to target class
            new_subj = data_service.add_subject_to_class(target_cls['id'], subj['course_id'])
            copied_subjects += 1

            # Get assessments from source subject and copy to new subject
            assessments = data_service.get_assessments_for_subject(subj['id'])
            for assess in assessments:
                data_service.add_assessment(new_subj['id'], assess['name'], assess['weight'])
                copied_assessments += 1

        return f"Estrutura copiada com sucesso! {copied_subjects} disciplinas e {copied_assessments} avaliações replicadas de {source_class_name} para {target_class_name}."

    except Exception as e: return f"Erro ao copiar estrutura: {e}"

@tool
def add_new_student(first_name: str, last_name: str, date_of_birth: str = None, enroll_in_class: str = None) -> str:
    """
    Adiciona um novo aluno ao sistema, com opção de matrícula em uma turma.
    """
    if not first_name or not last_name:
        return "Erro: O nome e o sobrenome são obrigatórios."

    birth_date_obj = None
    if date_of_birth:
        try:
            birth_date_obj = datetime.strptime(date_of_birth, "%d/%m/%Y").date()
        except ValueError:
            return f"Erro: Formato de data inválido '{date_of_birth}'. Use DD/MM/AAAA."

    try:
        student = data_service.add_student(first_name, last_name, birth_date=birth_date_obj)

        if student:
            response_msg = f"Novo aluno adicionado com sucesso: {first_name} {last_name} com ID {student['id']}."

            if enroll_in_class:
                target_class = data_service.get_class_by_name(enroll_in_class)

                if target_class:
                    next_call_number = data_service.get_next_call_number(target_class['id'])
                    enrollment = data_service.add_student_to_class(student['id'], target_class['id'], next_call_number)
                    if enrollment:
                        response_msg += f" Matriculado na turma '{target_class['name']}'."
                    else:
                        response_msg += f" Falha ao matricular na turma '{target_class['name']}'."
                else:
                    response_msg += f" Turma '{enroll_in_class}' não encontrada para matrícula."

            return response_msg
        else:
            return f"Erro: Ocorreu um erro desconhecido ao adicionar o aluno {first_name} {last_name}."
    except SQLAlchemyError as e:
        return f"Erro: Ocorreu um erro de banco de dados ao adicionar o aluno: {e}"
    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"

@tool
def update_student_enrollment_tool(student_name: str, class_name: str, new_status: str, new_call_number: int = None) -> str:
    """
    Atualiza os dados de matrícula de um aluno em uma turma (Status e/ou Número de Chamada).

    :param new_status: 'Active' ou 'Inactive'.
    :param new_call_number: Novo número de chamada (opcional).
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student: return f"Aluno não encontrado."
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma não encontrada."

        enrollments = data_service.get_enrollments_for_class(cls['id'])
        target_enrollment = next((e for e in enrollments if e['student_id'] == student['id']), None)

        if not target_enrollment: return f"Aluno não está matriculado nesta turma."

        if new_status not in ['Active', 'Inactive']:
            return f"Status inválido. Use 'Active' ou 'Inactive'."

        # Update status
        data_service.update_enrollment_status(target_enrollment['id'], new_status)

        # Update call number if provided
        if new_call_number is not None:
            # We reuse add_student_to_class which handles updates if record exists
            data_service.add_student_to_class(student['id'], cls['id'], new_call_number, new_status)
            return f"Matrícula atualizada: Status={new_status}, Nº={new_call_number}."

        return f"Matrícula atualizada para status '{new_status}'."

    except Exception as e: return f"Erro ao atualizar matrícula: {e}"

@tool
def delete_student(student_name: str) -> str:
    """
    Deleta um aluno do sistema. CUIDADO: Esta ação é irreversível e remove todas as notas e histórico.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student: return f"Aluno '{student_name}' não encontrado."

        data_service.delete_student(student['id'])
        return f"Aluno '{student_name}' e todos os seus registros foram removidos com sucesso."
    except Exception as e: return f"Erro ao deletar aluno: {e}"

@tool
def create_new_class(class_name: str) -> str:
    """
    Cria uma nova turma (sem disciplinas inicialmente).

    :param class_name: Nome da turma (ex: "1A").
    """
    if not class_name:
        return "Erro: Nome da turma é obrigatório."

    try:
        existing_class = data_service.get_class_by_name(class_name)
        if existing_class:
            return f"Erro: Já existe uma turma com o nome '{class_name}'."

        new_class = data_service.create_class(class_name)
        if new_class:
            return f"Turma '{class_name}' criada com sucesso. Agora adicione disciplinas a ela."
        else:
            return "Erro: Falha ao criar a turma."
    except Exception as e:
        return f"Erro inesperado ao criar turma: {e}"

@tool
def update_class(current_name: str, new_name: str) -> str:
    """
    Atualiza o nome de uma turma.
    """
    try:
        cls = data_service.get_class_by_name(current_name)
        if not cls: return f"Turma '{current_name}' não encontrada."
        data_service.update_class(cls['id'], new_name)
        return f"Turma renomeada para '{new_name}'."
    except Exception as e: return f"Erro: {e}"

@tool
def delete_class(class_name: str) -> str:
    """
    Deleta uma turma. CUIDADO: Remove matrículas associadas.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."
        data_service.delete_class(cls['id'])
        return f"Turma '{class_name}' deletada com sucesso."
    except Exception as e: return f"Erro: {e}"

@tool
def add_subject_to_class(class_name: str, course_name: str) -> str:
    """
    Adiciona uma disciplina existente a uma turma.

    :param class_name: Nome da turma (ex: "1A").
    :param course_name: Nome da disciplina (ex: "Matemática").
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        course = data_service.get_course_by_name(course_name)
        if not course: return f"Disciplina '{course_name}' não encontrada. Crie a disciplina primeiro."

        result = data_service.add_subject_to_class(cls['id'], course['id'])
        if result:
            return f"Disciplina '{course_name}' adicionada à turma '{class_name}' com sucesso."
        return f"Erro ao adicionar disciplina."
    except Exception as e:
        return f"Erro: {e}"

@tool
def add_new_lesson(class_name: str, subject_name: str, topic: str, content: str, date_str: str) -> str:
    """
    Adiciona uma aula a uma disciplina de uma turma.

    :param class_name: Nome da turma.
    :param subject_name: Nome da disciplina (ex: "Matemática").
    :param topic: Título da aula.
    :param content: Conteúdo.
    :param date_str: Data (DD/MM/AAAA).
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        # Busca a disciplina na turma
        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)

        if not target_subject:
            return f"Erro: A disciplina '{subject_name}' não faz parte da turma '{class_name}'."

        try:
            lesson_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            return f"Erro: Formato de data inválido '{date_str}'."

        lesson = data_service.create_lesson(target_subject['id'], topic, content, lesson_date)

        if lesson:
            return f"Aula '{topic}' de {subject_name} registrada com sucesso para a turma '{class_name}' em {date_str}."
        else:
            return "Erro: Falha ao criar o registro da aula."

    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"

@tool
def update_lesson(class_name: str, subject_name: str, current_topic: str, new_topic: str, new_content: str, new_date_str: str) -> str:
    """
    Atualiza uma aula existente.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)
        if not target_subject: return f"Disciplina não encontrada."

        lessons = data_service.get_lessons_for_subject(target_subject['id'])
        target_lesson = next((l for l in lessons if l['title'].lower() == current_topic.lower()), None)
        if not target_lesson: return f"Aula '{current_topic}' não encontrada."

        try:
            lesson_date = datetime.strptime(new_date_str, "%d/%m/%Y").date()
        except ValueError: return f"Data inválida."

        data_service.update_lesson(target_lesson['id'], new_topic, new_content, lesson_date)
        return f"Aula atualizada com sucesso."
    except Exception as e: return f"Erro: {e}"

@tool
def delete_lesson(class_name: str, subject_name: str, topic: str) -> str:
    """
    Deleta uma aula.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)
        if not target_subject: return f"Disciplina não encontrada."

        lessons = data_service.get_lessons_for_subject(target_subject['id'])
        target_lesson = next((l for l in lessons if l['title'].lower() == topic.lower()), None)
        if not target_lesson: return f"Aula não encontrada."

        data_service.delete_lesson(target_lesson['id'])
        return f"Aula '{topic}' deletada."
    except Exception as e: return f"Erro: {e}"

@tool
def create_new_assessment(class_name: str, subject_name: str, assessment_name: str, weight: float) -> str:
    """
    Cria uma avaliação para uma disciplina de uma turma.

    :param class_name: Nome da turma.
    :param subject_name: Nome da disciplina (ex: "História").
    :param assessment_name: Nome da avaliação (ex: "Prova 1").
    :param weight: Peso (float).
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)

        if not target_subject:
            return f"Erro: A disciplina '{subject_name}' não faz parte da turma '{class_name}'."

        assessment = data_service.add_assessment(target_subject['id'], assessment_name, weight)
        if assessment:
            return f"Avaliação '{assessment_name}' criada para {subject_name} na turma '{class_name}'."
        return "Erro ao criar avaliação."
    except Exception as e:
        return f"Erro: {e}"

@tool
def update_assessment(class_name: str, subject_name: str, current_name: str, new_name: str, new_weight: float) -> str:
    """
    Atualiza uma avaliação (nome e peso).
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)
        if not target_subject: return f"Disciplina não encontrada."

        assessments = data_service.get_assessments_for_subject(target_subject['id'])
        target_assessment = next((a for a in assessments if a['name'].lower() == current_name.lower()), None)
        if not target_assessment: return f"Avaliação '{current_name}' não encontrada."

        data_service.update_assessment(target_assessment['id'], new_name, new_weight)
        return f"Avaliação atualizada para '{new_name}' (Peso: {new_weight})."
    except Exception as e: return f"Erro: {e}"

@tool
def delete_assessment(class_name: str, subject_name: str, assessment_name: str) -> str:
    """
    Deleta uma avaliação e todas as notas associadas.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)
        if not target_subject: return f"Disciplina não encontrada."

        assessments = data_service.get_assessments_for_subject(target_subject['id'])
        target_assessment = next((a for a in assessments if a['name'].lower() == assessment_name.lower()), None)
        if not target_assessment: return f"Avaliação '{assessment_name}' não encontrada."

        data_service.delete_assessment(target_assessment['id'])
        return f"Avaliação '{assessment_name}' deletada."
    except Exception as e: return f"Erro: {e}"

@tool
def add_new_grade(student_name: str, class_name: str, subject_name: str, assessment_name: str, score: float) -> str:
    """
    Adiciona uma nota para um aluno.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student: return f"Aluno '{student_name}' não encontrado."

        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)

        if not target_subject:
            return f"Erro: Disciplina '{subject_name}' não encontrada na turma."

        # Busca avaliações dessa disciplina
        assessments = data_service.get_assessments_for_subject(target_subject['id'])
        target_assessment = next((a for a in assessments if a['name'].lower() == assessment_name.lower()), None)

        if not target_assessment:
            return f"Erro: Avaliação '{assessment_name}' não encontrada em {subject_name}."

        grade = data_service.add_grade(student['id'], target_assessment['id'], score)
        if grade:
            return f"Nota {score} adicionada para {student_name} em {assessment_name} ({subject_name})."
        return "Erro ao adicionar nota."
    except Exception as e:
        return f"Erro: {e}"

@tool
def update_grade_tool(student_name: str, class_name: str, subject_name: str, assessment_name: str, new_score: float) -> str:
    """
    Atualiza uma nota existente de um aluno.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student: return f"Aluno não encontrado."
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma não encontrada."
        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)
        if not target_subject: return f"Disciplina não encontrada."
        assessments = data_service.get_assessments_for_subject(target_subject['id'])
        target_assessment = next((a for a in assessments if a['name'].lower() == assessment_name.lower()), None)
        if not target_assessment: return f"Avaliação não encontrada."

        # Find existing grade
        # We use upsert logic essentially: find if exists, then update.
        # But DataService doesn't have `update_grade` (it uses upsert_grades_for_subject).
        # We can implement it via upsert_grades_for_subject with a single item list.

        grade_data = [{
            "student_id": student['id'],
            "assessment_id": target_assessment['id'],
            "score": new_score
        }]

        data_service.upsert_grades_for_subject(target_subject['id'], grade_data)
        return f"Nota atualizada para {new_score}."

    except Exception as e: return f"Erro ao atualizar nota: {e}"

@tool
def delete_grade(student_name: str, class_name: str, subject_name: str, assessment_name: str) -> str:
    """
    Deleta uma nota de um aluno.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student: return f"Aluno não encontrado."

        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)
        if not target_subject: return f"Disciplina não encontrada."

        assessments = data_service.get_assessments_for_subject(target_subject['id'])
        target_assessment = next((a for a in assessments if a['name'].lower() == assessment_name.lower()), None)
        if not target_assessment: return f"Avaliação não encontrada."

        # Busca nota especifica (não temos get_grade_by_... direto, então vamos iterar ou melhorar o service no futuro)
        # Por enquanto vou usar get_grades_for_subject e filtrar
        grades = data_service.get_grades_for_subject(target_subject['id'])
        target_grade = next((g for g in grades if g['student_id'] == student['id'] and g['assessment_id'] == target_assessment['id']), None)

        if target_grade:
            data_service.delete_grade(target_grade['id'])
            return f"Nota de {student_name} em {assessment_name} deletada."
        else:
            return f"Nota não encontrada."

    except Exception as e: return f"Erro: {e}"

@tool
def register_incident(student_name: str, class_name: str, description: str, date_str: str) -> str:
    """
    Registra um incidente (comportamental/geral) para um aluno em uma turma.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student: return f"Aluno '{student_name}' não encontrado."

        target_class = data_service.get_class_by_name(class_name)
        if not target_class: return f"Turma '{class_name}' não encontrada."

        try:
            incident_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            return f"Erro: Data inválida '{date_str}'."

        incident = data_service.create_incident(target_class['id'], student['id'], description, incident_date)
        if incident:
            return f"Incidente registrado para {student_name} na turma {class_name}."
        return "Erro ao registrar incidente."
    except Exception as e:
        return f"Erro: {e}"

@tool
def add_new_course(course_name: str, course_code: str) -> str:
    """
    Adiciona uma nova disciplina ao catálogo do sistema.
    """
    if not course_name or not course_code:
        return "Erro: Nome e código são obrigatórios."
    try:
        course = data_service.add_course(course_name, course_code)
        if course:
            return f"Disciplina '{course_name}' ({course_code}) criada com sucesso."
        return "Erro ao criar disciplina."
    except Exception as e:
        return f"Erro: {e}"

@tool
def update_course(current_name: str, new_name: str, new_code: str) -> str:
    """
    Atualiza uma disciplina no catálogo.
    """
    try:
        course = data_service.get_course_by_name(current_name)
        if not course: return f"Disciplina não encontrada."
        data_service.update_course(course['id'], new_name, new_code)
        return f"Disciplina atualizada para '{new_name}' ({new_code})."
    except Exception as e: return f"Erro: {e}"

@tool
def delete_course(course_name: str) -> str:
    """
    Deleta uma disciplina do catálogo. Falha se estiver em uso por alguma turma.
    """
    try:
        course = data_service.get_course_by_name(course_name)
        if not course: return f"Disciplina não encontrada."
        data_service.delete_course(course['id'])
        return f"Disciplina '{course_name}' deletada."
    except Exception as e: return f"Erro: {e}"

# --- MAINTENANCE TOOLS ---

@tool
def update_student_name(current_name: str, new_first_name: str, new_last_name: str) -> str:
    try:
        student = data_service.get_student_by_name(current_name)
        if not student: return "Aluno não encontrado."
        data_service.update_student(student['id'], new_first_name, new_last_name)
        return f"Nome atualizado para {new_first_name} {new_last_name}."
    except Exception as e: return f"Erro: {e}"

@tool
def enroll_existing_student(student_name: str, class_name: str) -> str:
    try:
        student = data_service.get_student_by_name(student_name)
        if not student: return "Aluno não encontrado."
        cls = data_service.get_class_by_name(class_name)
        if not cls: return "Turma não encontrada."

        next_num = data_service.get_next_call_number(cls['id'])
        res = data_service.add_student_to_class(student['id'], cls['id'], next_num)
        if res: return f"Aluno matriculado na turma {class_name}."
        return "Erro na matrícula."
    except Exception as e: return f"Erro: {e}"

@tool
def list_all_courses() -> str:
    """Lista todas as disciplinas do catálogo."""
    try:
        courses = data_service.get_all_courses()
        if not courses: return "Nenhuma disciplina no catálogo."
        return "\n".join([f"- {c['course_name']} ({c['course_code']})" for c in courses])
    except Exception as e: return f"Erro: {e}"

@tool
def register_attendance_tool(class_name: str, subject_name: str, lesson_title: str, student_names: str, status: str) -> str:
    """
    Registra a frequência de alunos em uma aula específica.

    :param class_name: Nome da turma.
    :param subject_name: Nome da disciplina.
    :param lesson_title: Título da aula.
    :param student_names: Lista de nomes de alunos separados por vírgula (ex: "João Silva, Maria Souza"). Use "TODOS" para aplicar a todos.
    :param status: Status da presença: 'P' (Presente), 'F' (Falta), 'J' (Justificada), 'A' (Atraso).
    """
    valid_statuses = {'P', 'F', 'J', 'A'}
    if status not in valid_statuses:
        return f"Erro: Status inválido '{status}'. Use P, F, J ou A."

    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)
        if not target_subject: return f"Disciplina '{subject_name}' não encontrada na turma."

        lessons = data_service.get_lessons_for_subject(target_subject['id'])
        target_lesson = next((l for l in lessons if l['title'].lower() == lesson_title.lower()), None)
        if not target_lesson: return f"Aula '{lesson_title}' não encontrada."

        # Identify students
        target_student_ids = []

        if student_names.upper() == "TODOS":
            enrollments = data_service.get_enrollments_for_class(cls['id'])
            target_student_ids = [e['student_id'] for e in enrollments if e['status'] == 'Active']
        else:
            names_list = [n.strip() for n in student_names.split(',')]
            for name in names_list:
                s = data_service.get_student_by_name(name)
                if s:
                    target_student_ids.append(s['id'])
                else:
                    return f"Erro: Aluno '{name}' não encontrado."

        if not target_student_ids:
            return "Nenhum aluno identificado para registro."

        attendance_data = [{"student_id": sid, "status": status} for sid in target_student_ids]
        data_service.register_attendance(target_lesson['id'], attendance_data)

        return f"Frequência registrada: {len(attendance_data)} alunos marcados como '{status}' na aula '{lesson_title}'."

    except Exception as e:
        return f"Erro ao registrar frequência: {e}"

@tool
def get_attendance_stats_tool(student_name: str, class_name: str, subject_name: str) -> str:
    """
    Obtém estatísticas de frequência de um aluno em uma disciplina.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student: return f"Aluno '{student_name}' não encontrado."

        cls = data_service.get_class_by_name(class_name)
        if not cls: return f"Turma '{class_name}' não encontrada."

        subjects = data_service.get_subjects_for_class(cls['id'])
        target_subject = next((s for s in subjects if s['course_name'].lower() == subject_name.lower()), None)
        if not target_subject: return f"Disciplina '{subject_name}' não encontrada na turma."

        stats = data_service.get_student_attendance_stats(student['id'], target_subject['id'])

        return (f"Frequência de {student_name} em {subject_name}:\n"
                f"- Aulas Totais: {stats['total_lessons']}\n"
                f"- Presenças (P/A/J): {stats['present_count']}\n"
                f"- Faltas: {stats['absent_count']}\n"
                f"- Percentual: {stats['percentage']:.1f}%")

    except Exception as e:
        return f"Erro ao obter estatísticas: {e}"
