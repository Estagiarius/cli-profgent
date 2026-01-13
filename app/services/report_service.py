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
import csv
import os
from datetime import datetime
import plotext as plt
from app.services.data_service import DataService

class ReportService:
    """
    Service responsible for generating reports and visualizations.
    This service centralizes logic used by both the AI Assistant and the UI.
    """

    REPORTS_DIR = "reports"

    def __init__(self):
        self.data_service = DataService()
        self._ensure_reports_dir()

    def _ensure_reports_dir(self):
        """Ensures the reports directory exists."""
        if not os.path.exists(self.REPORTS_DIR):
            os.makedirs(self.REPORTS_DIR)

    def _get_file_path(self, filename: str) -> str:
        """Returns the full path for a report file."""
        return os.path.join(self.REPORTS_DIR, filename)

    def generate_seating_chart_pdf(self, chart_id: int) -> str:
        """
        Generates a visual representation of the seating chart.
        For TUI, this returns a text file containing the grid representation.

        :param chart_id: ID of the seating chart.
        :return: Path to the generated text file.
        """
        chart_details = self.data_service.get_seating_chart_details(chart_id)
        if not chart_details:
            raise ValueError("Seating chart not found.")

        rows = chart_details['rows']
        cols = chart_details['columns']
        assignments = chart_details['assignments']

        import json
        try:
            layout_config = json.loads(chart_details.get('layout_config', '{}'))
        except json.JSONDecodeError:
            layout_config = {}

        # Determine cell assignments map
        assigned_map = {}
        for a in assignments:
            assigned_map[(a['row_index'], a['col_index'])] = a

        # Generate Text Grid
        output = [f"Mapa de Sala: {chart_details['name']}", ""]

        # Simple grid drawing with text
        # Assuming 3 lines per row (Top border, content, Bottom border) + headers

        col_width = 15
        border_line = "+" + ("-" * col_width + "+") * cols

        for r in range(rows):
            output.append(border_line)
            row_lines = ["|"]

            for c in range(cols):
                cell_key = f"{r},{c}"
                cell_type = layout_config.get(cell_key, "student_seat")

                content = " " * col_width

                if cell_type == "void":
                    content = "X" * col_width
                elif cell_type == "teacher_desk":
                    content = "Mesa Prof.".center(col_width)
                elif cell_type == "door":
                    content = "Porta".center(col_width)
                elif cell_type == "student_seat":
                    assignment_data = assigned_map.get((r, c))
                    if assignment_data:
                        student_name = assignment_data['student_name']
                        # Truncate if necessary
                        if len(student_name) > col_width - 2:
                            student_name = student_name[:col_width-2]
                        content = f" {student_name} ".center(col_width)
                    else:
                        content = "Vazio".center(col_width)

                row_lines.append(content + "|")

            output.append("".join(row_lines))

        output.append(border_line)

        filename = f"seating_chart_{chart_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self._get_file_path(filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(output))

        return filepath

    def generate_seating_chart_svg(self, chart_id: int) -> str:
        """
        Generates a visual representation of the seating chart as an SVG (vector).
        Legacy method kept for API compatibility, redirects to text version.

        :param chart_id: ID of the seating chart.
        :return: Path to the generated file.
        """
        return self.generate_seating_chart_pdf(chart_id)

    def generate_student_grade_chart(self, student_id: int, class_id: int) -> str:
        """
        Generates a bar chart of a student's grades in a specific class, separated by Subject.

        :param student_id: ID of the student.
        :param class_id: ID of the class.
        :return: Path to the generated text/ansi file.
        """
        report_data = self.data_service.get_class_report_data(class_id)
        student_data = next((s for s in report_data['students'] if s['student_id'] == student_id), None)
        class_info = self.data_service.get_class_by_id(class_id)

        if not student_data or not class_info:
             raise ValueError("Student or Class not found (or student not enrolled).")

        subjects_data = report_data['subjects']
        grades_map = report_data['grades_map']

        if not subjects_data:
            raise ValueError(f"No subjects found for {class_info['name']}.")

        subject_names = []
        averages = []

        for subject in subjects_data:
            assessments = subject['assessments']
            total_weight = sum(a['weight'] for a in assessments)

            student_grades = {}
            for assessment in assessments:
                score = grades_map.get((student_id, assessment['id']))
                if score is not None:
                    student_grades[assessment['id']] = score

            avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments, total_weight=total_weight)
            subject_names.append(subject['course_name'])
            averages.append(avg)

        # Plotting with plotext
        plt.clear_figure()
        plt.bar(subject_names, averages, orientation="vertical", width=0.5)
        plt.title(f"Desempenho de {student_data['name']} - {class_info['name']}")
        plt.xlabel("Disciplinas")
        plt.ylabel("Média")
        plt.ylim(0, 10)

        # Save file
        filename = f"chart_student_{student_id}_class_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self._get_file_path(filename)

        # plotext saves as text with ANSI codes
        plt.save_fig(filepath)

        return filepath

    def generate_class_grade_distribution(self, class_id: int) -> str:
        """
        Generates a histogram of global grade distribution for a class (averaging all subjects).

        :param class_id: ID of the class.
        :return: Path to the generated text/ansi file.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        if not class_info:
            raise ValueError("Class not found.")

        report_data = self.data_service.get_class_report_data(class_id)
        students = report_data['students']
        subjects = report_data['subjects']
        grades_map = report_data['grades_map']

        global_averages = []

        for student in students:
            student_id = student['student_id']
            student_subject_averages = []

            for subject in subjects:
                assessments = subject['assessments']
                total_weight = sum(a['weight'] for a in assessments)

                student_grades = {}
                for assessment in assessments:
                    score = grades_map.get((student_id, assessment['id']))
                    if score is not None:
                        student_grades[assessment['id']] = score

                avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments, total_weight=total_weight)
                student_subject_averages.append(avg)

            if student_subject_averages:
                global_avg = sum(student_subject_averages) / len(student_subject_averages)
                global_averages.append(global_avg)
            else:
                global_averages.append(0.0)

        if not global_averages:
             raise ValueError("No data to generate distribution.")

        # Plotting with plotext
        plt.clear_figure()
        plt.hist(global_averages, bins=10) # bins work differently in plotext, integer count
        plt.title(f"Distribuição de Notas Global - {class_info['name']}")
        plt.xlabel("Média Global")
        plt.ylabel("Número de Alunos")

        # Save file
        filename = f"chart_distribution_class_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self._get_file_path(filename)

        plt.save_fig(filepath)

        return filepath

    def export_class_grades_csv(self, class_id: int) -> str:
        """
        Exports grades for a class to a CSV file, listing all subjects and averages.

        :param class_id: ID of the class.
        :return: Path to the generated CSV file.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        if not class_info:
            raise ValueError("Class not found.")

        # Otimização 3: Usa o helper para evitar N+1 queries na exportação CSV
        report_data = self.data_service.get_class_report_data(class_id)
        students = report_data['students']
        subjects = report_data['subjects']
        grades_map = report_data['grades_map']

        # Prepare CSV Data
        # Header: Nº, Aluno, Subject 1 Avg, Subject 2 Avg, ..., Global Average
        header = ["Nº", "Aluno"] + [s['course_name'] for s in subjects] + ["Média Global"]

        rows = []
        for student in students:
            student_id = student['student_id']

            row = [student['call_number'], student['name']]

            subject_averages = []
            for subject in subjects:
                assessments = subject['assessments']
                total_weight = sum(a['weight'] for a in assessments)

                # Monta notas do aluno para essa matéria usando o mapa (Dict otimizado)
                student_grades = {}
                for assessment in assessments:
                    score = grades_map.get((student_id, assessment['id']))
                    if score is not None:
                        student_grades[assessment['id']] = score

                avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments, total_weight=total_weight)
                row.append(f"{avg:.2f}")
                subject_averages.append(avg)

            if subject_averages:
                global_avg = sum(subject_averages) / len(subject_averages)
                row.append(f"{global_avg:.2f}")
            else:
                row.append("0.00")

            rows.append(row)

        # Save file
        filename = f"grades_class_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self._get_file_path(filename)

        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)

        return filepath

    def generate_student_report_card(self, student_id: int, class_id: int) -> str:
        """
        Generates a text-based report card for a student, grouping grades by subject.

        :param student_id: ID of the student.
        :param class_id: ID of the class.
        :return: Path to the generated text file.
        """
        # Otimização 4 e 5: Usar helper de dados em lote para buscar estrutura e notas,
        # e usar novo método específico para incidentes do aluno.
        report_data = self.data_service.get_class_report_data(class_id)

        # Dados da turma e aluno
        class_info = self.data_service.get_class_by_id(class_id)
        student_data = next((s for s in report_data['students'] if s['student_id'] == student_id), None)

        if not class_info or not student_data:
             # Tenta buscar aluno isolado se não estiver matriculado/ativo no report data
             # Fallback otimizado: Busca apenas o aluno específico pelo ID
             student_obj = self.data_service.get_student_by_id(student_id)
             if not student_obj:
                raise ValueError("Class or Student not found.")
             student_name = f"{student_obj['first_name']} {student_obj['last_name']}"
        else:
             student_name = student_data['name']

        subjects_data = report_data['subjects']
        grades_map = report_data['grades_map']

        # Otimização 5: Buscar apenas incidentes deste aluno, não da turma toda
        student_incidents = self.data_service.get_student_incidents(student_id, class_id)

        # Build Report Content
        lines = [
            "=" * 50,
            "BOLETIM ESCOLAR",
            "=" * 50,
            f"Aluno: {student_name}",
            f"Turma: {class_info['name']}",
            f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y')}",
            "-" * 50,
            "DESEMPENHO POR DISCIPLINA:",
            ""
        ]

        if not subjects_data:
            lines.append("Nenhuma disciplina cadastrada nesta turma.")

        for subject in subjects_data:
            lines.append(f"DISCIPLINA: {subject['course_name'].upper()}")

            assessments = subject['assessments']
            total_weight = sum(a['weight'] for a in assessments)

            # Monta notas do aluno para essa matéria usando o mapa
            student_grades = {}
            for assessment in assessments:
                score = grades_map.get((student_id, assessment['id']))
                if score is not None:
                    student_grades[assessment['id']] = score

            if not assessments:
                lines.append("  - Nenhuma avaliação registrada.")
            else:
                for assessment in assessments:
                    score = grades_map.get((student_id, assessment['id']))
                    score_str = f"{score:.2f}" if score is not None else "N/A"
                    lines.append(f"  - {assessment['name']} (Peso {assessment['weight']}): {score_str}")

            avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments, total_weight=total_weight)
            lines.append(f"  >> MÉDIA FINAL: {avg:.2f}")

            # Adiciona Frequência
            freq_stats = self.data_service.get_student_attendance_stats(student_id, subject['id'])
            if freq_stats['total_lessons'] > 0:
                lines.append(f"  >> FREQUÊNCIA: {freq_stats['percentage']:.1f}% ({freq_stats['present_count']} P / {freq_stats['total_lessons']} Aulas)")
            else:
                lines.append("  >> FREQUÊNCIA: N/A")

            lines.append("-" * 30)

        lines.extend([
            "",
            "=" * 50,
            f"OCORRÊNCIAS DISCIPLINARES: {len(student_incidents)}"
        ])
        for inc in student_incidents:
             lines.append(f"- {inc['date']}: {inc['description']}")

        lines.append("="*50)

        # Save file
        filename = f"boletim_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self._get_file_path(filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        return filepath
