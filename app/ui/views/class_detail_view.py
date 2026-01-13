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
# Importa componentes e utilitários do tkinter e customtkinter.
import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv
from datetime import date, datetime
# Importa o serviço de dados para interagir com o banco de dados.
from app.services import data_service
# Importa as janelas de diálogo personalizadas para adicionar e editar registros.
from app.ui.views.add_dialog import AddDialog
from app.ui.views.edit_dialog import EditDialog
from app.ui.views.enrollment_dialog import EnrollmentDialog
from app.ui.views.attendance_dialog import AttendanceDialog
from app.ui.views.bncc_selection_dialog import BNCCSelectionDialog
from app.ui.views.copy_lesson_dialog import CopyLessonDialog
from app.ui.views.seating_chart_view import SeatingChartView
from customtkinter import CTkInputDialog
# Importa utilitários para tarefas assíncronas e de importação.
from app.utils.async_utils import run_async_task
from app.utils.import_utils import async_import_students
from app.utils.format_utils import parse_float_input, format_float_output
# Importa widgets e utilitários de UI
from app.ui.widgets.scrollable_canvas_frame import ScrollableCanvasFrame
from app.ui.ui_utils import bind_global_mouse_scroll
from app.ui.widgets.loading_overlay import LoadingOverlay
# Importa o serviço de relatórios.
from app.services.report_service import ReportService
import os
import asyncio
from PIL import Image

# Define a classe para a tela de detalhes da turma.
class ClassDetailView(ctk.CTkFrame):
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.report_service = ReportService()
        # ID da turma que está sendo visualizada. Inicialmente nulo.
        self.class_id = None
        # ID da disciplina selecionada atualmente.
        self.current_subject_id = None
        # ID da aula que está sendo editada. Inicialmente nulo.
        self.editing_lesson_id = None

        # Inicializa o dicionário de entradas de notas para evitar AttributeError
        self.grade_entries = {}

        # Mapeamento entre o status exibido na UI (português) e o armazenado no banco (inglês).
        self.status_map = {"Ativo": "Active", "Inativo": "Inactive"}
        # Mapeamento reverso para exibir o status do banco na UI.
        self.status_map_rev = {v: k for k, v in self.status_map.items()}

        # Configuração do layout de grade da view.
        self.grid_rowconfigure(2, weight=1) # A linha das abas se expande
        self.grid_columnconfigure(0, weight=1)

        # Rótulo do título principal da tela.
        self.title_label = ctk.CTkLabel(self, text="Detalhes da Turma", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="ew")

        # Frame de seleção de Disciplina (Header)
        self.subject_frame = ctk.CTkFrame(self)
        self.subject_frame.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")

        ctk.CTkLabel(self.subject_frame, text="Disciplina:").pack(side="left", padx=10)
        self.subject_combo = ctk.CTkOptionMenu(self.subject_frame, command=self.on_subject_change)
        self.subject_combo.pack(side="left", padx=10)

        self.add_subject_button = ctk.CTkButton(self.subject_frame, text="Adicionar Disciplina", command=self.add_subject_popup, width=150)
        self.add_subject_button.pack(side="right", padx=10)

        # Cria o widget de abas (Tabview) para organizar o conteúdo.
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        # Adiciona as abas.
        self.tab_view.add("Alunos")
        self.tab_view.add("Avaliações")
        self.tab_view.add("Aulas")
        self.tab_view.add("Incidentes")
        self.tab_view.add("Quadro de Notas")
        self.tab_view.add("Mapa de Sala")
        self.tab_view.add("BNCC")
        self.tab_view.add("Relatórios")

        # --- Aba de Alunos ---
        # Obtém a referência à aba "Alunos".
        students_tab = self.tab_view.tab("Alunos")
        students_tab.grid_rowconfigure(1, weight=1)
        students_tab.grid_columnconfigure(0, weight=1)

        # Frame para opções, como o checkbox de filtro.
        self.options_frame = ctk.CTkFrame(students_tab)
        self.options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Checkbox para filtrar e mostrar apenas alunos ativos.
        self.show_active_only_checkbox = ctk.CTkCheckBox(self.options_frame, text="Mostrar Apenas Alunos Ativos", command=self.populate_student_list)
        self.show_active_only_checkbox.pack(side="left", padx=10, pady=5)
        self.show_active_only_checkbox.select() # Marcado por padrão.

        # Frame com rolagem para exibir a lista de alunos.
        self.student_list_frame = ctk.CTkScrollableFrame(students_tab)
        self.student_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        bind_global_mouse_scroll(self.student_list_frame)

        # Frame para os botões de controle (matricular, importar).
        self.controls_frame = ctk.CTkFrame(students_tab)
        self.controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1)

        # Botão para abrir o pop-up de matrícula de aluno.
        self.enroll_student_button = ctk.CTkButton(self.controls_frame, text="Matricular Aluno", command=self.enroll_student_popup)
        self.enroll_student_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Botão para iniciar a importação de alunos via arquivo CSV.
        self.import_button = ctk.CTkButton(self.controls_frame, text="Importar Alunos (.csv)", command=self.import_students)
        self.import_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # --- Aba de Avaliações ---
        assessments_tab = self.tab_view.tab("Avaliações")
        assessments_tab.grid_rowconfigure(1, weight=1)
        assessments_tab.grid_columnconfigure(0, weight=1)

        # Tabview interno para separar avaliações por bimestre
        self.assessments_tabview = ctk.CTkTabview(assessments_tab, height=400)
        self.assessments_tabview.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.assessments_tabview.add("1º Bimestre")
        self.assessments_tabview.add("2º Bimestre")
        self.assessments_tabview.add("3º Bimestre")
        self.assessments_tabview.add("4º Bimestre")

        # Configura as abas
        for tab_name in ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"]:
            tab = self.assessments_tabview.tab(tab_name)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)
            frame = ctk.CTkScrollableFrame(tab)
            frame.grid(row=0, column=0, sticky="nsew")
            bind_global_mouse_scroll(frame)

        # Botão para adicionar uma nova avaliação.
        self.add_assessment_button = ctk.CTkButton(assessments_tab, text="Adicionar Nova Avaliação", command=self.add_assessment_popup)
        self.add_assessment_button.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        # --- Aba de Aulas ---
        lessons_tab = self.tab_view.tab("Aulas")
        lessons_tab.grid_rowconfigure(0, weight=1)
        lessons_tab.grid_columnconfigure(0, weight=1)

        # Container principal para a aba de aulas, para alternar entre a lista e o editor.
        self.lesson_container = ctk.CTkFrame(lessons_tab)
        self.lesson_container.grid(row=0, column=0, sticky="nsew")
        self.lesson_container.grid_rowconfigure(0, weight=1)
        self.lesson_container.grid_columnconfigure(0, weight=1)

        # --- Sub-view: Lista de Aulas ---
        self.lesson_list_view = ctk.CTkFrame(self.lesson_container)
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")
        self.lesson_list_view.grid_rowconfigure(0, weight=1)
        self.lesson_list_view.grid_columnconfigure(0, weight=1)

        self.lesson_list_frame = ctk.CTkScrollableFrame(self.lesson_list_view)
        self.lesson_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        bind_global_mouse_scroll(self.lesson_list_frame)

        self.lessons_actions_frame = ctk.CTkFrame(self.lesson_list_view, fg_color="transparent")
        self.lessons_actions_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.add_lesson_button = ctk.CTkButton(self.lessons_actions_frame, text="Adicionar Nova Aula", command=self.show_lesson_editor)
        self.add_lesson_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.copy_lesson_button = ctk.CTkButton(self.lessons_actions_frame, text="Copiar para Outra Turma", fg_color="#555555", hover_color="#444444", command=self.open_copy_lesson_dialog)
        self.copy_lesson_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # --- Sub-view: Editor de Aulas ---
        self.lesson_editor_view = ctk.CTkFrame(self.lesson_container)
        self.lesson_editor_view.grid_rowconfigure(2, weight=1) # O campo de conteúdo (linha 2) se expande.
        self.lesson_editor_view.grid_columnconfigure(1, weight=1) # A coluna dos inputs se expande.

        ctk.CTkLabel(self.lesson_editor_view, text="Título:").grid(row=0, column=0, padx=(10,0), pady=10, sticky="w")
        self.lesson_editor_title_entry = ctk.CTkEntry(self.lesson_editor_view, placeholder_text="Título da Aula")
        self.lesson_editor_title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.lesson_editor_view, text="Data (AAAA-MM-DD):").grid(row=1, column=0, padx=(10,0), pady=10, sticky="w")
        self.lesson_editor_date_entry = ctk.CTkEntry(self.lesson_editor_view)
        self.lesson_editor_date_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.lesson_editor_view, text="Conteúdo:").grid(row=2, column=0, padx=(10,0), pady=10, sticky="nw")
        self.lesson_editor_content_textbox = ctk.CTkTextbox(self.lesson_editor_view)
        self.lesson_editor_content_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        # --- Campo BNCC ---
        ctk.CTkLabel(self.lesson_editor_view, text="BNCC:").grid(row=3, column=0, padx=(10,0), pady=10, sticky="w")

        bncc_frame = ctk.CTkFrame(self.lesson_editor_view, fg_color="transparent")
        bncc_frame.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        bncc_frame.grid_columnconfigure(0, weight=1)

        self.lesson_editor_bncc_entry = ctk.CTkEntry(bncc_frame)
        self.lesson_editor_bncc_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        bncc_btn = ctk.CTkButton(bncc_frame, text="Selecionar", width=80, command=self.open_lesson_bncc_selector)
        bncc_btn.grid(row=0, column=1)

        editor_buttons_frame = ctk.CTkFrame(self.lesson_editor_view)
        editor_buttons_frame.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        self.save_lesson_button = ctk.CTkButton(editor_buttons_frame, text="Salvar", command=self.save_lesson)
        self.save_lesson_button.pack(side="left", padx=5)

        self.generate_ai_button = ctk.CTkButton(editor_buttons_frame, text="✨ Gerar com IA", fg_color="purple", command=self.generate_ai_content)
        self.generate_ai_button.pack(side="left", padx=5)

        self.cancel_lesson_button = ctk.CTkButton(editor_buttons_frame, text="Cancelar", command=self.hide_lesson_editor)
        self.cancel_lesson_button.pack(side="left", padx=5)

        self.hide_lesson_editor() # Editor começa escondido.

        # --- Aba de Incidentes ---
        incidents_tab = self.tab_view.tab("Incidentes")
        incidents_tab.grid_rowconfigure(0, weight=1)
        incidents_tab.grid_columnconfigure(0, weight=1)

        self.incident_list_frame = ctk.CTkScrollableFrame(incidents_tab)
        self.incident_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        bind_global_mouse_scroll(self.incident_list_frame)

        self.add_incident_button = ctk.CTkButton(incidents_tab, text="Adicionar Novo Incidente", command=self.add_incident_popup)
        self.add_incident_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Aba do Quadro de Notas ---
        grade_grid_tab = self.tab_view.tab("Quadro de Notas")
        grade_grid_tab.grid_rowconfigure(2, weight=1)
        grade_grid_tab.grid_columnconfigure(0, weight=1)

        # Frame para opções (filtro).
        self.grade_options_frame = ctk.CTkFrame(grade_grid_tab)
        self.grade_options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Checkbox para filtrar e mostrar apenas alunos ativos no quadro de notas.
        self.show_active_only_grades_checkbox = ctk.CTkCheckBox(
            self.grade_options_frame,
            text="Mostrar Apenas Alunos Ativos",
            command=self.populate_grade_grid
        )
        self.show_active_only_grades_checkbox.pack(side="left", padx=10, pady=5)
        self.show_active_only_grades_checkbox.select() # Marcado por padrão.

        # Tabview para os bimestres e resultados finais
        self.grades_tabview = ctk.CTkTabview(grade_grid_tab, command=self.populate_grade_grid)
        self.grades_tabview.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.grades_tabview.add("1º Bimestre")
        self.grades_tabview.add("2º Bimestre")
        self.grades_tabview.add("3º Bimestre")
        self.grades_tabview.add("4º Bimestre")
        self.grades_tabview.add("Resultados Finais")

        # Configura as sub-abas do quadro de notas
        for tab_name in ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre", "Resultados Finais"]:
            tab = self.grades_tabview.tab(tab_name)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)

            # Utiliza o componente customizado com rolagem 2D (Horizontal + Vertical)
            canvas_frame = ScrollableCanvasFrame(tab)
            canvas_frame.grid(row=0, column=0, sticky="nsew")

            # Aplica binding de rolagem (recursivo)
            canvas_frame.bind_mouse_wheel(canvas_frame.canvas)

            if not hasattr(self, "grade_frames"):
                 self.grade_frames = {}
            # O dicionário armazena o frame interno, para compatibilidade com a lógica existente de populate
            self.grade_frames[tab_name] = canvas_frame.scrollable_frame

        self.save_grades_button = ctk.CTkButton(grade_grid_tab, text="Salvar Alterações da Aba Atual", command=self.save_all_grades)
        self.save_grades_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # --- Aba de Relatórios ---
        reports_tab = self.tab_view.tab("Relatórios")
        reports_tab.grid_columnconfigure(0, weight=1)

        # Seção de Relatórios da Turma
        ctk.CTkLabel(reports_tab, text="Relatórios da Turma", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=(20, 10), sticky="w")

        self.class_reports_frame = ctk.CTkFrame(reports_tab)
        self.class_reports_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(self.class_reports_frame, text="Exportar Notas (CSV)", command=self.export_csv).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(self.class_reports_frame, text="Gráfico de Distribuição", command=self.show_distribution_chart).pack(side="left", padx=10, pady=10)

        # Seção de Relatórios do Aluno
        ctk.CTkLabel(reports_tab, text="Relatórios Individuais do Aluno", font=ctk.CTkFont(size=16, weight="bold")).grid(row=2, column=0, padx=10, pady=(20, 10), sticky="w")

        self.student_reports_frame = ctk.CTkFrame(reports_tab)
        self.student_reports_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.student_reports_frame, text="Selecione o Aluno:").pack(side="left", padx=10)
        self.report_student_combo = ctk.CTkComboBox(self.student_reports_frame, values=[])
        self.report_student_combo.pack(side="left", padx=10)

        ctk.CTkButton(self.student_reports_frame, text="Gerar Boletim (TXT)", command=self.generate_report_card).pack(side="left", padx=10)
        ctk.CTkButton(self.student_reports_frame, text="Gráfico de Desempenho", command=self.show_student_chart).pack(side="left", padx=10)

        # --- Aba BNCC ---
        self.bncc_tab = self.tab_view.tab("BNCC")
        self.bncc_tab.grid_rowconfigure(0, weight=1)
        self.bncc_tab.grid_columnconfigure(0, weight=1)

        self.bncc_scroll_frame = ctk.CTkScrollableFrame(self.bncc_tab)
        self.bncc_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Actions Frame
        self.bncc_actions_frame = ctk.CTkFrame(self.bncc_tab, fg_color="transparent")
        self.bncc_actions_frame.grid(row=1, column=0, pady=10)

        self.refresh_bncc_button = ctk.CTkButton(self.bncc_actions_frame, text="Atualizar Relatório", command=self.populate_bncc_tab)
        self.refresh_bncc_button.pack(side="left", padx=5)

        self.edit_bncc_button = ctk.CTkButton(self.bncc_actions_frame, text="Editar Currículo Global", command=self.open_bncc_editor)
        self.edit_bncc_button.pack(side="left", padx=5)

        # --- Aba Mapa de Sala ---
        seating_tab = self.tab_view.tab("Mapa de Sala")
        seating_tab.grid_rowconfigure(0, weight=1)
        seating_tab.grid_columnconfigure(0, weight=1)

        # O self.class_id é None no init, então precisamos configurar a view e atualizá-la depois
        self.seating_chart_view = SeatingChartView(seating_tab, self.class_id)
        self.seating_chart_view.grid(row=0, column=0, sticky="nsew")

    # --- Métodos de Gestão de Disciplinas (Subjects) ---

    def populate_subject_combo(self, subjects=None):
        """Busca as disciplinas da turma e preenche o combobox."""
        if not self.class_id: return

        if subjects is None:
            # Fallback para caso seja chamado sem dados (não deveria, se on_show usar a nova lógica)
            subjects = data_service.get_subjects_for_class(self.class_id)

        if not subjects:
            self.subject_combo.configure(values=["Nenhuma Disciplina"], state="disabled")
            self.current_subject_id = None
            self.subject_combo.set("Nenhuma Disciplina")
        else:
            self.subject_combo.configure(state="normal")
            subject_names = [s['course_name'] for s in subjects]
            self.subject_mapping = {s['course_name']: s['id'] for s in subjects}
            self.subject_data_mapping = {s['course_name']: s for s in subjects}
            self.subject_combo.configure(values=subject_names)

            # Seleciona o primeiro se nada estiver selecionado
            if not self.current_subject_id or self.current_subject_id not in self.subject_mapping.values():
                 first_subject_name = subject_names[0]
                 self.subject_combo.set(first_subject_name)
                 self.on_subject_change(first_subject_name)
            # Se já houver um selecionado, garante que o UI mostre o nome correto
            elif self.current_subject_id in self.subject_mapping.values():
                # Encontra o nome pelo ID
                name = next((n for n, id_ in self.subject_mapping.items() if id_ == self.current_subject_id), None)
                if name: self.subject_combo.set(name)


    # Método estático para buscar dados do subject em background
    @staticmethod
    def _fetch_subject_data(subject_id, class_id):
        return {
            "assessments": data_service.get_assessments_for_subject(subject_id),
            "lessons": data_service.get_lessons_for_subject(subject_id),
            "grades": data_service.get_grades_for_subject(subject_id),
            "enrollments": data_service.get_enrollments_for_class(class_id),
            "attendance_stats": data_service.get_class_attendance_stats(subject_id),
            "bncc_report": data_service.get_bncc_coverage(subject_id),
            "batch_averages": data_service.get_class_period_averages(subject_id)
        }

    def _on_subject_data_fetched(self, result):
        if isinstance(result, Exception):
            if hasattr(self, 'loading_overlay') and self.loading_overlay:
                self.loading_overlay.destroy()
                self.loading_overlay = None
            messagebox.showerror("Erro", f"Erro ao carregar dados da disciplina: {result}")
            return

        # Distribui os dados carregados para os métodos de população
        self.populate_assessment_list(assessments_data=result['assessments'])
        self.populate_lesson_list(lessons_data=result['lessons'])
        self.populate_grade_grid(
            assessments_data=result['assessments'],
            grades_data=result['grades'],
            enrollments_data=result['enrollments'],
            averages_data=result['batch_averages']
        )
        self.populate_student_list(
            enrollments_data=result['enrollments'],
            attendance_stats=result['attendance_stats']
        )
        self.populate_bncc_tab(report_data=result['bncc_report'])

        # Força renderização e atrasa remoção do overlay
        self.update_idletasks()
        if hasattr(self, 'loading_overlay') and self.loading_overlay:
            self.after(100, self._remove_overlay)

    def on_subject_change(self, selected_subject_name):
        """Callback para quando a disciplina é trocada no dropdown."""
        if selected_subject_name in self.subject_mapping:
            self.current_subject_id = self.subject_mapping[selected_subject_name]

            # Inicia o carregamento assíncrono
            if not hasattr(self, 'loading_overlay') or self.loading_overlay is None:
                self.loading_overlay = LoadingOverlay(self, text="Carregando Disciplina...")

            run_async_task(
                asyncio.to_thread(self._fetch_subject_data, self.current_subject_id, self.class_id),
                self.main_app.loop,
                self.main_app.async_queue,
                self._on_subject_data_fetched
            )

    def add_subject_popup(self):
        if not self.class_id: return

        # Pega todos os cursos disponíveis no catálogo
        all_courses = data_service.get_all_courses()
        if not all_courses:
             messagebox.showerror("Erro", "Não há disciplinas cadastradas no sistema.")
             return

        # Filtra cursos que a turma já tem
        current_subjects = data_service.get_subjects_for_class(self.class_id)
        current_course_ids = {s['course_id'] for s in current_subjects}

        available_courses = [c for c in all_courses if c['id'] not in current_course_ids]
        if not available_courses:
            messagebox.showinfo("Aviso", "Esta turma já possui todas as disciplinas cadastradas.")
            return

        course_names = [c['course_name'] for c in available_courses]

        def save_callback(data):
            course_name = data.get("course")
            selected_course = next((c for c in available_courses if c['course_name'] == course_name), None)

            if selected_course:
                data_service.add_subject_to_class(self.class_id, selected_course['id'])
                self.populate_subject_combo()
                # Se for a primeira, seleciona ela automaticamente
                if self.current_subject_id is None:
                     self.subject_combo.set(course_name)
                     self.on_subject_change(course_name)

        dropdowns = {"course": ("Disciplina", course_names)}
        AddDialog(self, "Adicionar Disciplina à Turma", fields={}, dropdowns=dropdowns, save_callback=save_callback)

    # --- Fim Métodos de Gestão de Disciplinas ---

    def open_bncc_editor(self):
        """Abre o diálogo da BNCC para editar o currículo global da disciplina."""
        if not self.current_subject_id:
            return

        # Recupera o course_id usando o mapeamento
        selected_subject_name = self.subject_combo.get()
        subject_data = self.subject_data_mapping.get(selected_subject_name)
        if not subject_data:
            messagebox.showerror("Erro", "Erro ao identificar a disciplina.")
            return

        course_id = subject_data['course_id']
        course_data = data_service.get_course_by_id(course_id)
        current_bncc = course_data.get('bncc_expected', '')

        def save_callback(new_codes):
            try:
                data_service.update_course_bncc(course_id, new_codes)
                messagebox.showinfo("Sucesso", "Currículo global atualizado com sucesso.")
                self.populate_bncc_tab()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao atualizar currículo: {e}")

        BNCCSelectionDialog(self, title="Editar Currículo Global", initial_selection=current_bncc, callback=save_callback)

    def populate_bncc_tab(self, report_data=None):
        """Preenche a aba de relatório BNCC."""
        # Limpa conteúdo
        for widget in self.bncc_scroll_frame.winfo_children():
            widget.destroy()

        if not self.class_id or not self.current_subject_id:
            ctk.CTkLabel(self.bncc_scroll_frame, text="Selecione uma disciplina.").pack(pady=20)
            return

        report = report_data if report_data is not None else data_service.get_bncc_coverage(self.current_subject_id)

        if not report:
             ctk.CTkLabel(self.bncc_scroll_frame, text="Dados não disponíveis.").pack(pady=20)
             return

        # Warning se não houver habilidades esperadas
        if not report.get('expected'):
            warning_frame = ctk.CTkFrame(self.bncc_scroll_frame, fg_color=("#FFEEBB", "#554400"), border_color="orange", border_width=1)
            warning_frame.pack(fill="x", padx=10, pady=(10, 0))

            warning_label = ctk.CTkLabel(
                warning_frame,
                text="⚠️ O professor ainda não cadastrou as habilidades no menu da disciplina, indicando para com que o professor cadastre as habilidades do currículo a serem trabalhadas.",
                text_color=("black", "orange"),
                wraplength=600,
                font=ctk.CTkFont(weight="bold")
            )
            warning_label.pack(padx=10, pady=10)

        # Summary
        summary_frame = ctk.CTkFrame(self.bncc_scroll_frame)
        summary_frame.pack(fill="x", padx=10, pady=10)

        coverage_pct = report.get('coverage_percentage', 0.0)

        ctk.CTkLabel(summary_frame, text=f"Cobertura: {coverage_pct:.1f}%", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)

        progress = ctk.CTkProgressBar(summary_frame)
        progress.pack(fill="x", padx=20, pady=5)
        progress.set(coverage_pct / 100.0)

        # Lists Frame
        lists_frame = ctk.CTkFrame(self.bncc_scroll_frame, fg_color="transparent")
        lists_frame.pack(fill="both", expand=True, padx=5, pady=5)
        lists_frame.grid_columnconfigure(0, weight=1)
        lists_frame.grid_columnconfigure(1, weight=1)

        # Covered
        covered_frame = ctk.CTkFrame(lists_frame)
        covered_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(covered_frame, text="Trabalhadas", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        covered_text = "\n".join(report['total_covered']) if report['total_covered'] else "Nenhuma habilidade registrada."
        ctk.CTkLabel(covered_frame, text=covered_text, justify="left", anchor="n").pack(padx=10, pady=5, fill="both", expand=True)

        # Missing
        missing_frame = ctk.CTkFrame(lists_frame)
        missing_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(missing_frame, text="Pendentes (do currículo)", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        missing_text = "\n".join(report['missing']) if report['missing'] else "Nenhuma pendência."
        ctk.CTkLabel(missing_frame, text=missing_text, justify="left", anchor="n", text_color=("red" if report['missing'] else "green")).pack(padx=10, pady=5, fill="both", expand=True)

        # Details
        details_frame = ctk.CTkFrame(self.bncc_scroll_frame)
        details_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(details_frame, text="Detalhes:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(details_frame, text=f"Em Aulas: {', '.join(report['covered_lessons'])}").pack(anchor="w", padx=10)
        ctk.CTkLabel(details_frame, text=f"Em Avaliações: {', '.join(report['covered_assessments'])}").pack(anchor="w", padx=10)

    def export_csv(self):
        if not self.class_id: return
        try:
            filepath = self.report_service.export_class_grades_csv(self.class_id)
            messagebox.showinfo("Sucesso", f"Arquivo exportado em:\n{filepath}")
            # Tenta abrir a pasta do arquivo
            if os.name == 'nt':
                os.startfile(os.path.dirname(filepath))
            else:
                os.system(f'xdg-open "{os.path.dirname(filepath)}"')
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar CSV: {e}")

    def show_distribution_chart(self):
        if not self.class_id: return
        try:
            filepath = self.report_service.generate_class_grade_distribution(self.class_id)
            self._show_image_popup("Distribuição de Notas", filepath)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar gráfico: {e}")

    def generate_report_card(self):
        if not self.class_id: return
        student_name = self.report_student_combo.get()
        if not student_name:
             messagebox.showwarning("Aviso", "Selecione um aluno primeiro.")
             return

        try:
            # Recupera o ID do aluno baseado no nome selecionado
            enrollments = data_service.get_enrollments_for_class(self.class_id)
            target_enrollment = next((e for e in enrollments if f"{e['student_first_name']} {e['student_last_name']}" == student_name), None)

            if target_enrollment:
                filepath = self.report_service.generate_student_report_card(target_enrollment['student_id'], self.class_id)
                messagebox.showinfo("Sucesso", f"Boletim gerado em:\n{filepath}")
                # Tenta abrir o arquivo
                if os.name == 'nt':
                    os.startfile(filepath)
                else:
                    os.system(f'xdg-open "{filepath}"')
        except Exception as e:
             messagebox.showerror("Erro", f"Falha ao gerar boletim: {e}")

    def show_student_chart(self):
        if not self.class_id: return
        student_name = self.report_student_combo.get()
        if not student_name:
             messagebox.showwarning("Aviso", "Selecione um aluno primeiro.")
             return

        try:
            enrollments = data_service.get_enrollments_for_class(self.class_id)
            target_enrollment = next((e for e in enrollments if f"{e['student_first_name']} {e['student_last_name']}" == student_name), None)

            if target_enrollment:
                filepath = self.report_service.generate_student_grade_chart(target_enrollment['student_id'], self.class_id)
                self._show_image_popup(f"Desempenho - {student_name}", filepath)
        except Exception as e:
             messagebox.showerror("Erro", f"Falha ao gerar gráfico: {e}")

    def _show_image_popup(self, title, filepath):
        """Exibe uma imagem em uma janela popup."""
        top = ctk.CTkToplevel(self)
        top.title(title)
        top.geometry("800x600")

        # Carrega a imagem usando PIL e converte para CTkImage
        pil_image = Image.open(filepath)
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(780, 580))

        label = ctk.CTkLabel(top, image=ctk_image, text="")
        label.pack(padx=10, pady=10, fill="both", expand=True)


    # Método para salvar todas as notas inseridas ou alteradas no quadro de notas.
    def save_all_grades(self):
        if not self.current_subject_id:
             messagebox.showwarning("Aviso", "Selecione uma disciplina antes de salvar notas.")
             return

        current_tab = self.grades_tabview.get()

        # Se estiver na aba "Resultados Finais", a lógica de salvamento é ligeiramente diferente (salva no período 5)
        if current_tab == "Resultados Finais":
             self.save_final_grades()
             return

        # Lógica padrão para bimestres 1-4
        grades_to_upsert = []
        for (student_id, assessment_id), entry_widget in self.grade_entries.items():
            # Filtra apenas entries que pertencem à aba atual (embora grade_entries contenha tudo se não limparmos,
            # mas vamos garantir limpando no populate ou filtrando aqui se necessário).
            # Como populate_grade_grid limpa self.grade_entries, aqui só temos os widgets visíveis da aba atual.

            score_str = entry_widget.get()
            if not score_str: continue

            try:
                score = parse_float_input(score_str)
                if not (0 <= score <= 10):
                    messagebox.showerror("Nota Inválida", f"Nota inválida '{score}'. As notas devem ser entre 0 e 10.")
                    return
                grades_to_upsert.append({'student_id': student_id, 'assessment_id': assessment_id, 'score': score})
            except ValueError:
                messagebox.showerror("Nota Inválida", f"Nota inválida '{score_str}'. As notas devem ser numéricas.")
                return

        if not grades_to_upsert:
            messagebox.showinfo("Nenhuma Mudança", "Nenhuma nota nova ou modificada para salvar.")
            return

        data_service.upsert_grades_for_subject(self.current_subject_id, grades_to_upsert)
        messagebox.showinfo("Sucesso", "Notas salvas com sucesso.")
        self.populate_grade_grid() # Atualiza para refletir mudanças (médias)

    def save_final_grades(self):
        """Salva as notas finais sobrescritas na aba 'Resultados Finais'."""
        # Garante que a avaliação final (grading_period=5) existe
        final_assessment = data_service.ensure_final_assessment(self.current_subject_id)
        final_assessment_id = final_assessment['id']

        grades_to_upsert = []
        for (student_id, _), entry_widget in self.grade_entries.items():
            score_str = entry_widget.get()
            if not score_str: continue # Se vazio, não salva nada (mantém calculado se já existia, ou deleta? Upsert não deleta.)

            # Se o usuário apagou o valor, talvez devesse deletar a nota?
            # Por enquanto, assumimos que ele digita um valor.

            try:
                score = parse_float_input(score_str)
                if not (0 <= score <= 10):
                    messagebox.showerror("Nota Inválida", f"Nota inválida '{score}'.")
                    return

                grades_to_upsert.append({
                    'student_id': student_id,
                    'assessment_id': final_assessment_id,
                    'score': score
                })
            except ValueError:
                messagebox.showerror("Nota Inválida", f"Valor inválido '{score_str}'.")
                return

        if grades_to_upsert:
            data_service.upsert_grades_for_subject(self.current_subject_id, grades_to_upsert)
            messagebox.showinfo("Sucesso", "Notas finais salvas com sucesso.")
            self.populate_grade_grid()
        else:
            messagebox.showinfo("Aviso", "Nenhuma nota final para salvar.")

    # Método para construir e preencher o quadro de notas.
    def populate_grade_grid(self, assessments_data=None, grades_data=None, enrollments_data=None, averages_data=None):
        # Identifica a aba atual
        current_tab_name = self.grades_tabview.get()
        frame = self.grade_frames[current_tab_name]

        # Limpa o frame atual
        for widget in frame.winfo_children():
            widget.destroy()

        # Limpa entradas antigas para não salvar dados de abas invisíveis
        self.grade_entries = {}

        if not self.class_id or not self.current_subject_id:
            ctk.CTkLabel(frame, text="Selecione uma disciplina.").pack(pady=20)
            return

        # Busca alunos (usa dados passados ou busca novos)
        enrollments = enrollments_data if enrollments_data is not None else data_service.get_enrollments_for_class(self.class_id)
        if self.show_active_only_grades_checkbox.get():
            enrollments = [e for e in enrollments if e['status'] == 'Active']

        # Lógica para Abas de Bimestre (1-4)
        if current_tab_name != "Resultados Finais":
            period_map = {"1º Bimestre": 1, "2º Bimestre": 2, "3º Bimestre": 3, "4º Bimestre": 4}
            target_period = period_map.get(current_tab_name, 1)

            # Busca avaliações DO PERÍODO
            all_assessments = assessments_data if assessments_data is not None else data_service.get_assessments_for_subject(self.current_subject_id)
            period_assessments = [a for a in all_assessments if a.get('grading_period', 1) == target_period]

            if not period_assessments:
                ctk.CTkLabel(frame, text="Nenhuma avaliação cadastrada neste bimestre.").pack(pady=20)
                return

            # Headers
            headers = ["Nome do Aluno"] + [a['name'] for a in period_assessments] + ["Média Bimestre"]
            for col, header in enumerate(headers):
                label = ctk.CTkLabel(frame, text=header, font=ctk.CTkFont(weight="bold"))
                label.grid(row=0, column=col, padx=5, pady=5, sticky="w")

            # Dados
            grades = grades_data if grades_data is not None else data_service.get_grades_for_subject(self.current_subject_id)

            # --- OTIMIZAÇÃO: Indexar grades em um dicionário para acesso O(1) ---
            grades_map = {(g['student_id'], g['assessment_id']): g for g in grades}

            for row, enrollment in enumerate(enrollments, start=1):
                student_name = f"{enrollment['student_first_name']} {enrollment['student_last_name']}"
                ctk.CTkLabel(frame, text=student_name).grid(row=row, column=0, padx=5, pady=5, sticky="w")

                student_grades_for_avg = {} # Para cálculo da média local da linha (Dict {assessment_id: score})

                for col, assessment in enumerate(period_assessments, start=1):
                    entry = ctk.CTkEntry(frame, width=80)
                    entry.grid(row=row, column=col, padx=5, pady=5)

                    # Acesso direto via hash map
                    existing_grade = grades_map.get((enrollment['student_id'], assessment['id']))

                    if existing_grade:
                        entry.insert(0, format_float_output(existing_grade['score']))
                        student_grades_for_avg[assessment['id']] = existing_grade['score']

                    self.grade_entries[(enrollment['student_id'], assessment['id'])] = entry

                # Calcula Média do Bimestre
                # Precisamos passar apenas os assessments deste bimestre para o cálculo ficar correto como média deste bimestre
                period_assessments_data = [{"id": a['id'], "weight": a['weight']} for a in period_assessments]
                period_total_weight = sum(a['weight'] for a in period_assessments_data)

                avg = data_service.calculate_weighted_average(
                    enrollment['student_id'],
                    student_grades_for_avg,
                    period_assessments_data,
                    total_weight=period_total_weight
                )

                ctk.CTkLabel(frame, text=format_float_output(avg, precision=2)).grid(row=row, column=len(period_assessments)+1, padx=5, pady=5)

        # Lógica para Aba "Resultados Finais"
        else:
            headers = ["Nome do Aluno", "Média Calculada (4 Bim.)", "Nota Final (Editável)", "Ações"]
            for col, header in enumerate(headers):
                label = ctk.CTkLabel(frame, text=header, font=ctk.CTkFont(weight="bold"))
                label.grid(row=0, column=col, padx=10, pady=5, sticky="w")

            # --- OTIMIZAÇÃO: Batch fetch de médias finais ---
            batch_averages = averages_data if averages_data is not None else data_service.get_class_period_averages(self.current_subject_id)

            for row, enrollment in enumerate(enrollments, start=1):
                student_id = enrollment['student_id']

                # Lookup no batch results (se não existir, retorna dict vazio, que resulta em 0.0)
                averages = batch_averages.get(student_id, {})

                calc_avg = averages.get("final_calculated", 0.0)
                override_avg = averages.get("final_override")

                student_name = f"{enrollment['student_first_name']} {enrollment['student_last_name']}"

                # Col 0: Nome
                ctk.CTkLabel(frame, text=student_name).grid(row=row, column=0, padx=10, pady=5, sticky="w")

                # Col 1: Média Calculada
                ctk.CTkLabel(frame, text=format_float_output(calc_avg, precision=2)).grid(row=row, column=1, padx=10, pady=5)

                # Col 2: Nota Final (Editável)
                entry = ctk.CTkEntry(frame, width=80)
                entry.grid(row=row, column=2, padx=10, pady=5)

                # Valor inicial: Se tiver override, mostra ele. Se não, mostra a calculada.
                current_val = override_avg if override_avg is not None else calc_avg
                entry.insert(0, format_float_output(current_val, precision=2))

                # Armazena entry com chave 'None' para assessment_id, pois tratamos especial no save_final_grades
                self.grade_entries[(student_id, None)] = entry

                # Col 3: Botão Recalcular (Reset)
                # Só faz sentido se tiver um override. Se não tiver, o valor já é o calculado.
                # Mas para simplificar, o botão sempre copia o valor calculado para o entry.
                recalc_btn = ctk.CTkButton(frame, text="Recalcular", width=80,
                                           command=lambda e=entry, val=calc_avg: self._reset_final_grade(e, val))
                recalc_btn.grid(row=row, column=3, padx=10, pady=5)

    def _reset_final_grade(self, entry_widget, calculated_value):
        entry_widget.delete(0, "end")
        entry_widget.insert(0, format_float_output(calculated_value, precision=2))

    # Abre o pop-up para adicionar um novo incidente.
    def add_incident_popup(self):
        if not self.class_id: return

        # Busca os alunos matriculados para preencher o dropdown.
        enrollments = data_service.get_enrollments_for_class(self.class_id)
        student_names = [f"{e['student_first_name']} {e['student_last_name']}" for e in enrollments]

        if not student_names:
            messagebox.showwarning("Aviso", "Nenhum aluno nesta turma para registrar um incidente.")
            return

        # Função de callback que será chamada pelo diálogo ao salvar.
        def save_callback(data):
            student_name = data["student"]
            description = data["description"]
            # Encontra o objeto de matrícula correspondente ao nome do aluno selecionado.
            selected_enrollment = next((e for e in enrollments if f"{e['student_first_name']} {e['student_last_name']}" == student_name), None)

            if selected_enrollment and description:
                # Chama o serviço para criar o incidente no banco de dados.
                data_service.create_incident(self.class_id, selected_enrollment['student_id'], description, date.today())
                # Atualiza a lista de incidentes na tela.
                self.populate_incident_list()

        # Configuração dos campos para o diálogo genérico.
        fields = {"description": "Descrição"}
        dropdowns = {"student": ("Aluno", student_names)}
        AddDialog(self, "Adicionar Novo Incidente", fields=fields, dropdowns=dropdowns, save_callback=save_callback)

    # Preenche a lista de incidentes na respectiva aba.
    def populate_incident_list(self):
        for widget in self.incident_list_frame.winfo_children(): widget.destroy()
        if not self.class_id: return

        incidents = data_service.get_incidents_for_class(self.class_id)

        # Cria cabeçalhos.
        headers = ["Nome do Aluno", "Data", "Descrição"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.incident_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        # Cria as linhas com os dados dos incidentes.
        for i, incident in enumerate(incidents, start=1):
            student_name = f"{incident['student_first_name']} {incident['student_last_name']}"
            ctk.CTkLabel(self.incident_list_frame, text=student_name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=incident['date']).grid(row=i, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=incident['description'], wraplength=400, justify="left").grid(row=i, column=2, padx=10, pady=5, sticky="w")

    # Mostra a view de edição/criação de aula.
    def show_lesson_editor(self, lesson=None):
        if not self.current_subject_id:
             messagebox.showwarning("Aviso", "Selecione uma disciplina para adicionar aulas.")
             return

        # Armazena o ID da aula se estiver em modo de edição.
        self.editing_lesson_id = lesson['id'] if lesson else None
        # Esconde a lista de aulas e mostra o editor.
        self.lesson_list_view.grid_forget()
        self.lesson_editor_view.grid(row=0, column=0, sticky="nsew")

        # Limpa os campos do editor.
        self.lesson_editor_title_entry.delete(0, "end")
        self.lesson_editor_date_entry.delete(0, "end")
        self.lesson_editor_content_textbox.delete("1.0", "end")
        self.lesson_editor_bncc_entry.delete(0, "end")

        # Se estiver editando, preenche os campos com os dados da aula.
        if lesson:
            self.lesson_editor_title_entry.insert(0, lesson['title'])
            self.lesson_editor_date_entry.insert(0, lesson['date'])
            self.lesson_editor_content_textbox.insert("1.0", lesson['content'] or "")
            self.lesson_editor_bncc_entry.insert(0, lesson.get('bncc_codes') or "")
        # Se estiver criando, preenche a data com o dia de hoje.
        else:
            self.lesson_editor_date_entry.insert(0, date.today().isoformat())

    # Esconde a view de edição de aula e volta para a lista.
    def hide_lesson_editor(self):
        self.editing_lesson_id = None
        self.lesson_editor_view.grid_forget()
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")

    def open_lesson_bncc_selector(self):
        def on_select(result_string):
             self.lesson_editor_bncc_entry.delete(0, "end")
             self.lesson_editor_bncc_entry.insert(0, result_string)

        BNCCSelectionDialog(self, initial_selection=self.lesson_editor_bncc_entry.get(), callback=on_select)

    def generate_ai_content(self):
        """Dispara a geração de conteúdo de aula usando IA."""
        title = self.lesson_editor_title_entry.get()
        if not title:
            # Se não houver título, pede um.
            dialog = CTkInputDialog(text="Digite o tema da aula:", title="Gerar Conteúdo com IA")
            title = dialog.get_input()
            if not title: return
            self.lesson_editor_title_entry.insert(0, title)

        if not self.class_id or not self.current_subject_id:
             messagebox.showerror("Erro", "Contexto de Turma ou Disciplina não encontrado.")
             return

        # Busca nomes para passar ao prompt
        class_data = data_service.get_class_by_id(self.class_id)
        # Precisamos buscar o nome do curso pelo ID da disciplina
        subjects = data_service.get_subjects_for_class(self.class_id)
        subject_data = next((s for s in subjects if s['id'] == self.current_subject_id), None)

        if not class_data or not subject_data:
             messagebox.showerror("Erro", "Dados da Turma/Disciplina incompletos.")
             return

        class_name = class_data['name']
        course_name = subject_data['course_name']

        # Feedback visual
        self.generate_ai_button.configure(state="disabled", text="Gerando...")
        self.lesson_editor_content_textbox.delete("1.0", "end")
        self.lesson_editor_content_textbox.insert("1.0", "Gerando sugestão de aula... Por favor aguarde.")

        # Executa assincronamente
        coro = self.main_app.assistant_service.generate_lesson_content(title, course_name, class_name)
        run_async_task(coro, self.main_app.loop, self.main_app.async_queue, self._on_ai_content_generated)

    def _on_ai_content_generated(self, result):
        """Callback após geração de conteúdo."""
        self.generate_ai_button.configure(state="normal", text="✨ Gerar com IA")

        if isinstance(result, Exception):
            messagebox.showerror("Erro IA", f"Falha ao gerar conteúdo: {result}")
            self.lesson_editor_content_textbox.delete("1.0", "end")
            return

        self.lesson_editor_content_textbox.delete("1.0", "end")
        self.lesson_editor_content_textbox.insert("1.0", result)

    # Salva os dados da aula (criação ou atualização).
    def save_lesson(self):
        title = self.lesson_editor_title_entry.get()
        content = self.lesson_editor_content_textbox.get("1.0", "end-1c")
        date_str = self.lesson_editor_date_entry.get()
        bncc_codes = self.lesson_editor_bncc_entry.get()

        if not title or not date_str:
            messagebox.showerror("Erro", "Título e Data são obrigatórios.")
            return

        try:
            lesson_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use AAAA-MM-DD.")
            return

        # Se estiver editando, chama o método de atualização.
        if self.editing_lesson_id:
            data_service.update_lesson(self.editing_lesson_id, title, content, lesson_date, bncc_codes)
        # Caso contrário, chama o método de criação (usando a disciplina atual).
        else:
            data_service.create_lesson(self.current_subject_id, title, content, lesson_date, bncc_codes)

        # Atualiza a lista de aulas e esconde o editor.
        self.populate_lesson_list()
        self.hide_lesson_editor()

    # Abre o pop-up para adicionar uma nova avaliação.
    def add_assessment_popup(self):
        if not self.class_id: return
        if not self.current_subject_id:
             messagebox.showwarning("Aviso", "Selecione uma disciplina para adicionar avaliações.")
             return

        def save_callback(data):
            name = data.get("name")
            weight_str = data.get("weight")
            period_str = data.get("period") # Ex: "1º Bimestre"
            bncc_codes = data.get("bncc")

            period_map = {"1º Bimestre": 1, "2º Bimestre": 2, "3º Bimestre": 3, "4º Bimestre": 4}
            grading_period = period_map.get(period_str, 1)

            if name and weight_str:
                try:
                    weight = parse_float_input(weight_str)
                    data_service.add_assessment(self.current_subject_id, name, weight, grading_period, bncc_codes)
                    self.populate_assessment_list()
                    self.populate_grade_grid() # Atualiza também o quadro de notas para aparecer a nova coluna
                except ValueError as e:
                    messagebox.showerror("Erro", f"Erro ao adicionar avaliação: {e}")

        fields = {"name": "Nome da Avaliação", "weight": "Peso", "bncc": "Códigos BNCC"}
        dropdowns = {"period": ("Bimestre", ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"])}

        AddDialog(self, "Adicionar Nova Avaliação", fields=fields, dropdowns=dropdowns, save_callback=save_callback)

    # Preenche a lista de avaliações separada por bimestres.
    def populate_assessment_list(self, assessments_data=None):
        # Limpa todas as abas
        tab_names = ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"]
        frames = {}
        for name in tab_names:
            frame = self.assessments_tabview.tab(name).winfo_children()[0] # Pega o ScrollableFrame dentro da aba
            for widget in frame.winfo_children(): widget.destroy()
            frames[name] = frame

        if not self.class_id: return
        if not self.current_subject_id:
             # Mostra aviso na primeira aba apenas
             ctk.CTkLabel(frames["1º Bimestre"], text="Selecione ou adicione uma disciplina.").pack(pady=10)
             return

        assessments = assessments_data if assessments_data is not None else data_service.get_assessments_for_subject(self.current_subject_id)

        # Filtra e popula cada aba
        for period_idx, tab_name in enumerate(tab_names, start=1):
            period_assessments = [a for a in assessments if a.get('grading_period', 1) == period_idx]
            frame = frames[tab_name]

            if not period_assessments:
                ctk.CTkLabel(frame, text="Nenhuma avaliação neste bimestre.").pack(pady=10)
                continue

            headers = ["Nome da Avaliação", "Peso", "Ações"]
            for i, header in enumerate(headers):
                label = ctk.CTkLabel(frame, text=header, font=ctk.CTkFont(weight="bold"))
                label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

            for i, assessment in enumerate(period_assessments, start=1):
                ctk.CTkLabel(frame, text=assessment['name']).grid(row=i, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(frame, text=format_float_output(assessment['weight'])).grid(row=i, column=1, padx=10, pady=5, sticky="w")

                actions_frame = ctk.CTkFrame(frame)
                actions_frame.grid(row=i, column=2, padx=5, pady=5, sticky="e")

                edit_button = ctk.CTkButton(actions_frame, text="Editar", command=lambda a=assessment: self.edit_assessment_popup(a))
                edit_button.pack(side="left", padx=5)

                delete_button = ctk.CTkButton(actions_frame, text="Excluir", fg_color="red", command=lambda a_id=assessment['id']: self.delete_assessment_action(a_id))
                delete_button.pack(side="left", padx=5)

    # Ação de deletar uma avaliação após confirmação.
    def delete_assessment_action(self, assessment_id):
        dialog = CTkInputDialog(text="Digite 'DELETE' para confirmar a exclusão:", title="Confirmar Exclusão")
        user_input = dialog.get_input()
        if user_input == "DELETE":
            data_service.delete_assessment(assessment_id)
            self.populate_assessment_list()

    # Abre o pop-up para editar uma avaliação.
    def edit_assessment_popup(self, assessment):
        def save_callback(assessment_id, data):
            name = data.get("name")
            weight_str = data.get("weight")
            period_str = data.get("period")
            bncc_codes = data.get("bncc")

            period_map = {"1º Bimestre": 1, "2º Bimestre": 2, "3º Bimestre": 3, "4º Bimestre": 4}
            grading_period = period_map.get(period_str, assessment.get('grading_period', 1))

            if name and weight_str:
                try:
                    weight = parse_float_input(weight_str)
                    data_service.update_assessment(assessment_id, name, weight, grading_period, bncc_codes)
                    self.populate_assessment_list()
                    self.populate_grade_grid()
                except ValueError as e:
                    messagebox.showerror("Erro", f"Erro ao editar avaliação: {e}")

        fields = {"name": "Nome da Avaliação", "weight": "Peso", "bncc": "Códigos BNCC"}

        # Determine initial period string
        current_period_id = assessment.get('grading_period', 1)
        reverse_period_map = {1: "1º Bimestre", 2: "2º Bimestre", 3: "3º Bimestre", 4: "4º Bimestre"}
        current_period_str = reverse_period_map.get(current_period_id, "1º Bimestre")

        initial_data = {
            "id": assessment['id'],
            "name": assessment['name'],
            "weight": format_float_output(assessment['weight']),
            "period": current_period_str,
            "bncc": assessment.get('bncc_codes') or ""
        }

        dropdowns = {"period": ("Bimestre", ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"])}

        EditDialog(self, "Editar Avaliação", fields, initial_data, save_callback, dropdowns=dropdowns)

    # Abre o pop-up para matricular um aluno existente na turma.
    def enroll_student_popup(self):
        if not self.class_id: return

        unenrolled_students = data_service.get_unenrolled_students(self.class_id)

        if not unenrolled_students:
            messagebox.showinfo("Aviso", "Nenhum aluno disponível para matricular.")
            return

        def enroll_callback(student_ids: list[int]):
            if not student_ids: return

            try:
                data_service.enroll_students(self.class_id, student_ids)

                count = len(student_ids)
                messagebox.showinfo("Sucesso", f"{count} aluno(s) matriculado(s) com sucesso!")

                self.populate_student_list()
                self.populate_report_student_combo()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao matricular alunos: {e}")

        EnrollmentDialog(
            self,
            title="Matricular Alunos",
            students=unenrolled_students,
            enroll_callback=enroll_callback
        )

    # Preenche a lista de alunos matriculados.
    def populate_student_list(self, enrollments_data=None, attendance_stats=None):
        for widget in self.student_list_frame.winfo_children(): widget.destroy()
        if not self.class_id: return

        enrollments = enrollments_data if enrollments_data is not None else data_service.get_enrollments_for_class(self.class_id)

        # Filtra por alunos ativos se o checkbox estiver marcado.
        if self.show_active_only_checkbox.get():
            enrollments = [e for e in enrollments if e['status'] == 'Active']

        # Carrega estatísticas de frequência em lote para evitar N+1 queries
        batch_attendance_stats = attendance_stats
        if batch_attendance_stats is None and self.current_subject_id:
             batch_attendance_stats = data_service.get_class_attendance_stats(self.current_subject_id)
        elif batch_attendance_stats is None:
            batch_attendance_stats = {}

        headers = ["Nº de Chamada", "Nome do Aluno", "Freq. %", "Data de Nascimento", "Status"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.student_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, enrollment in enumerate(enrollments, start=1):
            ctk.CTkLabel(self.student_list_frame, text=str(enrollment['call_number'])).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.student_list_frame, text=f"{enrollment['student_first_name']} {enrollment['student_last_name']}").grid(row=i, column=1, padx=10, pady=5, sticky="w")

            # Coluna Frequência
            freq_text = "-"
            if self.current_subject_id and enrollment['status'] == 'Active':
                stats = batch_attendance_stats.get(enrollment['student_id'])
                if stats and stats['total_lessons'] > 0:
                    freq_text = f"{stats['percentage']:.1f}%"

            ctk.CTkLabel(self.student_list_frame, text=freq_text).grid(row=i, column=2, padx=10, pady=5, sticky="w")

            birth_date_str = ""
            if enrollment['student_birth_date']:
                try:
                    birth_date = datetime.strptime(enrollment['student_birth_date'], '%Y-%m-%d')
                    birth_date_str = birth_date.strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    birth_date_str = "Data Inválida"
            ctk.CTkLabel(self.student_list_frame, text=birth_date_str).grid(row=i, column=3, padx=10, pady=5, sticky="w")

            # Botão Toggle para Status (Mais leve que Dropdown)
            is_active = enrollment['status'] == 'Active'
            btn_text = "Ativo" if is_active else "Inativo"
            btn_color = "#2CC985" if is_active else "#D32F2F" # Verde / Vermelho
            btn_hover = "#229A66" if is_active else "#B71C1C"

            status_btn = ctk.CTkButton(
                self.student_list_frame,
                text=btn_text,
                fg_color=btn_color,
                hover_color=btn_hover,
                width=80,
                command=lambda eid=enrollment['id'], curr=enrollment['status']: self.toggle_student_status(eid, curr)
            )
            status_btn.grid(row=i, column=4, padx=10, pady=5, sticky="w")

    # Atualiza o status de uma matrícula (Toggle).
    def toggle_student_status(self, enrollment_id, current_status):
        new_status = "Inactive" if current_status == "Active" else "Active"
        data_service.update_enrollment_status(enrollment_id, new_status)
        self.populate_student_list()

    def populate_report_student_combo(self):
        """Atualiza o combobox de alunos na aba de relatórios."""
        if not self.class_id: return

        enrollments = data_service.get_enrollments_for_class(self.class_id)
        student_names = [f"{e['student_first_name']} {e['student_last_name']}" for e in enrollments]

        self.report_student_combo.configure(values=student_names)

        current = self.report_student_combo.get()
        if current and current in student_names:
            return # Mantém a seleção atual se ainda for válida

        if student_names:
            self.report_student_combo.set(student_names[0])
        else:
            self.report_student_combo.set("")

    # Inicia o processo de importação de alunos via CSV.
    def import_students(self):
        if not self.class_id:
            messagebox.showerror("Erro", "Selecione uma turma antes de importar alunos.")
            return

        filepath = filedialog.askopenfilename(
            title="Selecione um arquivo CSV de Alunos",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*"))
        )
        if not filepath: return

        # Desabilita botões e mostra feedback de "importando...".
        self.import_button.configure(state="disabled", text="Importando...")
        self.enroll_student_button.configure(state="disabled")

        # Cria a coroutine para a importação assíncrona.
        coro = async_import_students(filepath, self.class_id, self.main_app.data_service)
        # Executa a coroutine em segundo plano.
        run_async_task(coro, self.main_app.loop, self.main_app.async_queue, self._on_import_complete)

    # Callback executado na thread principal após a conclusão da importação.
    def _on_import_complete(self, result):
        """Callback executado na thread principal da UI após a conclusão da tarefa de importação."""
        # Reabilita os botões.
        self.import_button.configure(state="normal", text="Importar Alunos (.csv)")
        self.enroll_student_button.configure(state="normal")

        # Se o resultado for uma exceção, mostra um erro.
        if isinstance(result, Exception):
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro fatal durante a importação:\n\n{result}")
            return

        # Desempacota o resultado.
        success_count, errors = result
        # Atualiza a lista de alunos na tela.
        self.populate_student_list()
        self.populate_report_student_combo()

        # Mostra um relatório de sucesso ou de erros.
        if errors:
            error_message = f"{success_count} alunos importados com sucesso, mas ocorreram os seguintes erros:\n\n" + "\n".join(errors)
            messagebox.showwarning("Importação com Erros", error_message)
        else:
            messagebox.showinfo("Sucesso", f"{success_count} alunos importados com sucesso!")

    # Preenche a lista de aulas.
    def populate_lesson_list(self, lessons_data=None):
        for widget in self.lesson_list_frame.winfo_children(): widget.destroy()
        if not self.class_id: return

        if not self.current_subject_id:
             ctk.CTkLabel(self.lesson_list_frame, text="Selecione ou adicione uma disciplina.").pack(pady=10)
             return

        lessons = lessons_data if lessons_data is not None else data_service.get_lessons_for_subject(self.current_subject_id)

        headers = ["Data", "Título", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.lesson_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, lesson in enumerate(lessons, start=1):
            ctk.CTkLabel(self.lesson_list_frame, text=lesson['date']).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.lesson_list_frame, text=lesson['title']).grid(row=i, column=1, padx=10, pady=5, sticky="w")

            actions_frame = ctk.CTkFrame(self.lesson_list_frame, fg_color="transparent")
            actions_frame.grid(row=i, column=2, padx=10, pady=5, sticky="e")

            # Botão de Chamada
            chamada_btn = ctk.CTkButton(actions_frame, text="Chamada", width=80, fg_color="#2CC985", hover_color="#229A66",
                                        command=lambda lid=lesson['id'], ltitle=lesson['title']: self.open_attendance_dialog(lid, ltitle))
            chamada_btn.pack(side="left", padx=5)

            edit_button = ctk.CTkButton(actions_frame, text="Editar", width=80, command=lambda l=lesson: self.show_lesson_editor(l))
            edit_button.pack(side="left", padx=5)

    def open_copy_lesson_dialog(self):
        if not self.class_id: return
        if not self.current_subject_id:
             messagebox.showwarning("Aviso", "Selecione uma disciplina para copiar aulas.")
             return

        # Callback opcional se quisermos fazer algo após copiar (ex: logar ou atualizar algo)
        # Por enquanto não precisa recarregar nada na view ATUAL, pois copiamos PARA outra turma.
        CopyLessonDialog(self, self.class_id, self.current_subject_id)

    def open_attendance_dialog(self, lesson_id, lesson_title):
        if not self.class_id: return

        # 1. Carrega alunos ativos
        enrollments = data_service.get_enrollments_for_class(self.class_id)
        active_enrollments = [e for e in enrollments if e['status'] == 'Active']

        if not active_enrollments:
            messagebox.showwarning("Aviso", "Não há alunos ativos nesta turma para realizar a chamada.")
            return

        students = [{"id": e['student_id'], "name": f"{e['student_first_name']} {e['student_last_name']}"} for e in active_enrollments]

        # 2. Carrega chamadas existentes
        existing_records = data_service.get_lesson_attendance(lesson_id)
        attendance_map = {r['student_id']: r['status'] for r in existing_records}

        # 3. Callback de salvamento
        def save_attendance(lid, data):
            try:
                data_service.register_attendance(lid, data)
                messagebox.showinfo("Sucesso", "Chamada registrada com sucesso.")
                # Atualiza a lista de alunos para refletir nova % de frequência
                self.populate_student_list()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar chamada: {e}")

        # 4. Abre dialogo
        AttendanceDialog(self, f"Chamada - {lesson_title}", lesson_id, students, attendance_map, save_attendance)

    # Método estático para busca inicial de dados
    @staticmethod
    def _fetch_initial_details(class_id, preferred_subject_id=None):
        class_data = data_service.get_class_by_id(class_id)
        subjects = data_service.get_subjects_for_class(class_id)
        enrollments = data_service.get_enrollments_for_class(class_id)
        incidents = data_service.get_incidents_for_class(class_id)

        subject_data = None
        target_subject_id = None

        # Determina qual disciplina carregar (preferida ou a primeira da lista)
        if subjects:
            ids = [s['id'] for s in subjects]
            if preferred_subject_id and preferred_subject_id in ids:
                target_subject_id = preferred_subject_id
            else:
                target_subject_id = subjects[0]['id']

        # Se identificou uma disciplina alvo, carrega seus dados
        if target_subject_id:
            subject_data = ClassDetailView._fetch_subject_data(target_subject_id, class_id)
            subject_data['id'] = target_subject_id

        return {
            "class_data": class_data,
            "subjects": subjects,
            "enrollments": enrollments,
            "incidents": incidents,
            "initial_subject_data": subject_data
        }

    def _on_initial_details_fetched(self, result):
        if isinstance(result, Exception):
            if hasattr(self, 'loading_overlay') and self.loading_overlay:
                self.loading_overlay.destroy()
                self.loading_overlay = None
            messagebox.showerror("Erro", f"Erro ao carregar turma: {result}")
            return

        class_data = result['class_data']
        self.title_label.configure(text=f"Detalhes da Turma: {class_data['name']}")

        # Recupera dados combinados
        initial_subject_data = result.get('initial_subject_data')
        subjects = result['subjects']

        # Configura o ID da disciplina atual ANTES de popular o combo.
        # Isso impede que o populate_subject_combo dispare o evento on_change desnecessariamente.
        if initial_subject_data:
            self.current_subject_id = initial_subject_data['id']

        # Popula dropdown de subjects
        self.populate_subject_combo(subjects=subjects)
        self.populate_report_student_combo()
        self.populate_incident_list(incidents_data=result['incidents'])

        # Se temos dados da disciplina, populamos tudo
        if initial_subject_data:
            # Popula abas específicas da disciplina
            self.populate_assessment_list(assessments_data=initial_subject_data['assessments'])
            self.populate_lesson_list(lessons_data=initial_subject_data['lessons'])
            self.populate_grade_grid(
                assessments_data=initial_subject_data['assessments'],
                grades_data=initial_subject_data['grades'],
                enrollments_data=result['enrollments'],
                averages_data=initial_subject_data['batch_averages']
            )
            # Popula lista de alunos COM FREQUÊNCIA (Attendance Stats)
            self.populate_student_list(
                enrollments_data=result['enrollments'],
                attendance_stats=initial_subject_data['attendance_stats']
            )
            self.populate_bncc_tab(report_data=initial_subject_data['bncc_report'])
        else:
            # Caso sem disciplina, popula apenas a lista básica de alunos
            self.populate_student_list(enrollments_data=result['enrollments'])

        # Força renderização e atrasa remoção do overlay
        self.update_idletasks()
        if hasattr(self, 'loading_overlay') and self.loading_overlay:
            self.after(100, self._remove_overlay)

    def _remove_overlay(self):
        if hasattr(self, 'loading_overlay') and self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None

    # Sobrecarga para populate_incident_list aceitar dados
    def populate_incident_list(self, incidents_data=None):
        for widget in self.incident_list_frame.winfo_children(): widget.destroy()
        if not self.class_id: return

        incidents = incidents_data if incidents_data is not None else data_service.get_incidents_for_class(self.class_id)

        # Cria cabeçalhos.
        headers = ["Nome do Aluno", "Data", "Descrição"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.incident_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        # Cria as linhas com os dados dos incidentes.
        for i, incident in enumerate(incidents, start=1):
            student_name = f"{incident['student_first_name']} {incident['student_last_name']}"
            ctk.CTkLabel(self.incident_list_frame, text=student_name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=incident['date']).grid(row=i, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=incident['description'], wraplength=400, justify="left").grid(row=i, column=2, padx=10, pady=5, sticky="w")

    # Método chamado quando esta view é exibida.
    def on_show(self, class_id=None):
        self.class_id = class_id

        # Atualiza a view do mapa de sala com o ID novo
        self.seating_chart_view.class_id = class_id
        # Reseta o estado do mapa
        self.seating_chart_view.populate_layout_combo()

        if class_id:
            # Mostra Overlay
            if not hasattr(self, 'loading_overlay') or self.loading_overlay is None:
                self.loading_overlay = LoadingOverlay(self, text="Carregando Detalhes da Turma...")

            # Passa o self.current_subject_id (se houver) como preferência
            # Embora no on_show ele possa ser de uma turma anterior,
            # o ideal seria resetar ou tentar manter se fizer sentido.
            # Como a view é recriada/reusada, melhor passar None para resetar ou
            # confiar na lógica do fetch (pegar o primeiro).
            # Se quisermos persistir a escolha de disciplina ao voltar para a turma,
            # precisaríamos armazenar isso na MainApp ou algo assim.
            # Por padrão, vamos deixar None para pegar a primeira.

            run_async_task(
                asyncio.to_thread(self._fetch_initial_details, class_id),
                self.main_app.loop,
                self.main_app.async_queue,
                self._on_initial_details_fetched
            )
