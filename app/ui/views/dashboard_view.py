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

import os
import customtkinter as ctk
from tkinter import messagebox
from typing import List, Dict, Any, Optional

from PIL import Image

from app.ui.ui_utils import bind_global_mouse_scroll
from app.utils.charts import create_grade_distribution_chart, create_approval_pie_chart
from app.ui.views.base_dialog import BaseDialog

# Constants for Thresholds and Colors
APPROVAL_THRESHOLD_HIGH = 70
APPROVAL_THRESHOLD_MEDIUM = 50

COLOR_RISK = "red"
COLOR_WARNING = "orange"
COLOR_SUCCESS = "green"
COLOR_HONOR = "#FFD700"
COLOR_TEXT_GRAY = "gray"
COLOR_PIE_CHART_BG = "#DCB538"
COLOR_HOVER_RED = "#d32f2f"


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent: Any, main_app: Any):
        super().__init__(parent)
        self.main_app = main_app
        self.data_service = self.main_app.data_service
        self.courses: List[Dict[str, Any]] = []
        self.selected_course_id: Optional[int] = None

        # Data placeholders
        self.failed_details_data: List[Dict[str, Any]] = []
        self.honor_roll_data: List[Dict[str, Any]] = []

        # Configura o layout de grade da view.
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Título ---
        self.title_label = ctk.CTkLabel(self, text="Dashboard de Análises", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # --- Sistema de Abas ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, rowspan=2, padx=20, pady=10, sticky="nsew")

        self.tab_overview = self.tabview.add("Visão Geral")
        self.setup_overview_tab()

        self.tab_rankings = self.tabview.add("Destaques & Alertas")
        self.setup_rankings_tab()

        self.tab_analysis = self.tabview.add("Por Disciplina")
        self.setup_analysis_tab()

        # --- Frame de Aniversariantes ---
        self.birthdays_frame_container = ctk.CTkFrame(self)
        self.birthdays_frame_container.grid(row=1, column=1, rowspan=2, padx=(0, 20), pady=10, sticky="nsew")
        self.birthdays_frame_container.grid_rowconfigure(1, weight=1)
        self.birthdays_frame_container.grid_columnconfigure(0, weight=1)

        self.birthdays_title = ctk.CTkLabel(self.birthdays_frame_container, text="Aniversariantes do Dia", font=ctk.CTkFont(size=16, weight="bold"))
        self.birthdays_title.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.birthdays_scrollable_frame = ctk.CTkScrollableFrame(self.birthdays_frame_container, label_text="")
        self.birthdays_scrollable_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        bind_global_mouse_scroll(self.birthdays_scrollable_frame)

    def setup_overview_tab(self) -> None:
        """Configura os elementos da aba Visão Geral."""
        self.tab_overview.grid_columnconfigure(0, weight=1)
        self.tab_overview.grid_columnconfigure(1, weight=1)
        self.tab_overview.grid_rowconfigure(1, weight=1)

        # Cards de Estatísticas
        self.stats_frame = ctk.CTkFrame(self.tab_overview)
        self.stats_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.stats_frame.grid_columnconfigure((0, 1), weight=1)

        self.card_students = self._create_stat_card(self.stats_frame, "Alunos Ativos", "0", 0, 0)
        self.card_classes = self._create_stat_card(self.stats_frame, "Turmas", "0", 0, 1)
        self.card_courses = self._create_stat_card(self.stats_frame, "Disciplinas", "0", 1, 0)
        self.card_incidents = self._create_stat_card(self.stats_frame, "Incidentes", "0", 1, 1)

        # Seção de Aprovação Global
        self.approval_frame = ctk.CTkFrame(self.tab_overview)
        self.approval_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")
        self.approval_frame.grid_columnconfigure(0, weight=1)
        self.approval_frame.grid_columnconfigure(1, weight=1)

        # -- Coluna 0: Texto e Botão --
        text_container = ctk.CTkFrame(self.approval_frame, fg_color="transparent")
        text_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(text_container, text="Índice Global de Aprovação\n(Média >= 5.0)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))

        self.approval_label = ctk.CTkLabel(text_container, text="--%", font=ctk.CTkFont(size=40, weight="bold"))
        self.approval_label.pack(pady=10)

        self.approval_detail_label = ctk.CTkLabel(text_container, text="Aprovados: 0 | Abaixo da Média: 0", text_color=COLOR_TEXT_GRAY)
        self.approval_detail_label.pack(pady=(0, 20))

        self.btn_details = ctk.CTkButton(
            text_container,
            text="Ver Alunos em Risco",
            command=self.open_risk_details_dialog,
            fg_color=COLOR_RISK,
            hover_color=COLOR_HOVER_RED
        )
        self.btn_details.pack(pady=10)

        # -- Coluna 1: Gráfico Pizza --
        self.pie_chart_container = ctk.CTkFrame(self.approval_frame, fg_color=COLOR_PIE_CHART_BG)
        self.pie_chart_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.pie_chart_label = ctk.CTkLabel(self.pie_chart_container, text="")
        self.pie_chart_label.pack(expand=True)
        self.pie_chart_image = None

    def setup_rankings_tab(self) -> None:
        """Configura os elementos da aba de Destaques e Alertas."""
        self.tab_rankings.grid_columnconfigure(0, weight=1)
        self.tab_rankings.grid_columnconfigure(1, weight=1)
        self.tab_rankings.grid_rowconfigure(0, weight=1)

        # --- Quadro de Honra ---
        self.honor_frame = ctk.CTkFrame(self.tab_rankings)
        self.honor_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.honor_frame, text="Quadro de Honra (Média >= 9.0)", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10)

        self.honor_count_label = ctk.CTkLabel(self.honor_frame, text="0 Alunos Destaque", font=ctk.CTkFont(size=14), text_color=COLOR_HONOR)
        self.honor_count_label.pack(pady=5)

        self.honor_list_frame = ctk.CTkScrollableFrame(self.honor_frame)
        self.honor_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        bind_global_mouse_scroll(self.honor_list_frame)

        # --- Ranking de Incidentes ---
        self.incidents_frame = ctk.CTkFrame(self.tab_rankings)
        self.incidents_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.incidents_frame, text="Top Incidentes por Turma", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10)

        self.incidents_list_frame = ctk.CTkScrollableFrame(self.incidents_frame)
        self.incidents_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        bind_global_mouse_scroll(self.incidents_list_frame)

    def setup_analysis_tab(self) -> None:
        """Configura os elementos da aba Análise por Disciplina."""
        self.tab_analysis.grid_columnconfigure(0, weight=1)
        self.tab_analysis.grid_rowconfigure(1, weight=1)

        # Frame de Controles
        self.controls_frame = ctk.CTkFrame(self.tab_analysis)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.course_label = ctk.CTkLabel(self.controls_frame, text="Selecione a Disciplina:")
        self.course_label.pack(side="left", padx=10, pady=10)

        self.course_menu = ctk.CTkOptionMenu(self.controls_frame, values=[], command=self.on_course_select)
        self.course_menu.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # Frame do Gráfico
        self.chart_frame = ctk.CTkFrame(self.tab_analysis)
        self.chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.chart_label = ctk.CTkLabel(self.chart_frame, text="Selecione um curso para ver a distribuição de médias.")
        self.chart_label.pack(expand=True, fill="both")
        self.chart_image = None

    def on_show(self, **kwargs) -> None:
        try:
            _ = kwargs
            self.update_global_stats()
            self.load_courses()
            self.update_chart()
            self.update_birthdays()
        except Exception as e:
            messagebox.showerror("Erro no Dashboard", f"Erro ao carregar dados do dashboard: {e}")

    def update_global_stats(self) -> None:
        """Atualiza os cards e estatísticas da aba Visão Geral."""
        try:
            stats = self.data_service.get_global_dashboard_stats()
            self.card_students.configure(text=str(stats.get('active_students', 0)))
            self.card_classes.configure(text=str(stats.get('total_classes', 0)))
            self.card_courses.configure(text=str(stats.get('total_courses', 0)))
            self.card_incidents.configure(text=str(stats.get('total_incidents', 0)))

            perf = self.data_service.get_global_performance_stats()
            approval_rate = perf.get('approval_rate', 0.0)
            approved = perf.get('approved', 0)
            failed = perf.get('failed', 0)
            self.failed_details_data = perf.get('failed_details', [])
            self.honor_roll_data = perf.get('honor_roll_details', [])

            color = COLOR_SUCCESS if approval_rate >= APPROVAL_THRESHOLD_HIGH else COLOR_WARNING if approval_rate >= APPROVAL_THRESHOLD_MEDIUM else COLOR_RISK
            self.approval_label.configure(text=f"{approval_rate:.1f}%", text_color=color)
            self.approval_detail_label.configure(text=f"Aprovados: {approved} | Abaixo da Média: {failed}")

            # Atualiza Honor Roll
            self.honor_count_label.configure(text=f"{len(self.honor_roll_data)} Alunos Destaque")

            for widget in self.honor_list_frame.winfo_children():
                widget.destroy()

            if not self.honor_roll_data:
                ctk.CTkLabel(self.honor_list_frame, text="Nenhum aluno em destaque.", text_color=COLOR_TEXT_GRAY).pack(pady=5)
            else:
                for item in self.honor_roll_data:
                    row = ctk.CTkFrame(self.honor_list_frame)
                    row.pack(fill="x", pady=2)
                    text = f"{item['student_name']} - {item['course_name']}"
                    score_text = f"{item['average']}"
                    ctk.CTkLabel(row, text=text, anchor="w").pack(side="left", padx=5)
                    ctk.CTkLabel(row, text=score_text, text_color=COLOR_HONOR, font=ctk.CTkFont(weight="bold")).pack(side="right", padx=5)

            # Atualiza Gráfico Pizza
            pie_chart_path = create_approval_pie_chart(approved, failed)
            if os.path.exists(pie_chart_path):
                img = Image.open(pie_chart_path)
                self.pie_chart_image = ctk.CTkImage(light_image=img, size=img.size)
                self.pie_chart_label.configure(image=self.pie_chart_image, text="")
            else:
                self.pie_chart_label.configure(image=None, text="Erro no Gráfico")

            # Atualiza Ranking Incidentes
            incident_ranking = self.data_service.get_class_incident_ranking()

            for widget in self.incidents_list_frame.winfo_children():
                widget.destroy()

            if not incident_ranking:
                ctk.CTkLabel(self.incidents_list_frame, text="Nenhum incidente registrado.", text_color=COLOR_TEXT_GRAY).pack(pady=5)
            else:
                for i, item in enumerate(incident_ranking):
                    row = ctk.CTkFrame(self.incidents_list_frame)
                    row.pack(fill="x", pady=2)
                    ctk.CTkLabel(row, text=f"{i+1}. {item['class_name']}", anchor="w").pack(side="left", padx=5)
                    ctk.CTkLabel(row, text=f"{item['count']} incidentes", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=5)

        except Exception as e:
            print(f"Erro ao atualizar estatísticas globais: {e}")
            # Non-critical, suppress UI popup to avoid spam, just log or print

    def load_courses(self) -> None:
        """Carrega os cursos no menu dropdown."""
        try:
            self.courses = self.data_service.get_all_courses()
            course_names = [c['course_name'] for c in self.courses]

            if course_names:
                self.course_menu.configure(values=course_names)
                if not self.selected_course_id:
                    self.course_menu.set(course_names[0])
                    self.on_course_select(course_names[0])
            else:
                self.course_menu.configure(values=["Nenhum curso disponível"])
                self.course_menu.set("Nenhum curso disponível")
                self.selected_course_id = None
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar disciplinas: {e}")

    def on_course_select(self, selected_name: str) -> None:
        self.selected_course_id = None
        for course in self.courses:
            if course['course_name'] == selected_name:
                self.selected_course_id = course['id']
                break
        self.update_chart()

    def update_chart(self) -> None:
        """Gera e exibe o gráfico com as médias finais."""
        try:
            if self.selected_course_id is None:
                self.chart_label.configure(text="Nenhum curso selecionado ou disponível.", image=None)
                return

            selected_course = self.data_service.get_course_by_id(self.selected_course_id)
            if not selected_course:
                self.chart_label.configure(text=f"Não foi possível encontrar o curso com ID: {self.selected_course_id}", image=None)
                return

            averages = self.data_service.get_course_averages(self.selected_course_id)
            chart_path = create_grade_distribution_chart(averages, selected_course['course_name'])

            if os.path.exists(chart_path):
                img = Image.open(chart_path)
                self.chart_image = ctk.CTkImage(light_image=img, size=img.size)
                self.chart_label.configure(image=self.chart_image, text="")
            else:
                self.chart_label.configure(image=None, text="Não foi possível gerar o gráfico.")
        except Exception as e:
            self.chart_label.configure(text=f"Erro ao gerar gráfico: {e}", image=None)

    def update_birthdays(self) -> None:
        try:
            for widget in self.birthdays_scrollable_frame.winfo_children():
                widget.destroy()

            birthdays = self.data_service.get_students_with_birthday_today()

            if not birthdays:
                ctk.CTkLabel(self.birthdays_scrollable_frame, text="Nenhum aniversariante hoje.", text_color=COLOR_TEXT_GRAY).pack(pady=20)
                return

            for student in birthdays:
                card = ctk.CTkFrame(self.birthdays_scrollable_frame)
                card.pack(fill="x", pady=5, padx=5)

                ctk.CTkLabel(card, text=student["name"], font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 0))
                ctk.CTkLabel(card, text=f"Completando {student['age']} anos").pack(anchor="w", padx=10)
                ctk.CTkLabel(card, text=f"{student['class_name']}", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_GRAY).pack(anchor="w", padx=10, pady=(0, 5))
        except Exception as e:
             ctk.CTkLabel(self.birthdays_scrollable_frame, text=f"Erro ao carregar aniversariantes: {e}", text_color=COLOR_RISK).pack(pady=20)

    def open_risk_details_dialog(self) -> None:
        """Abre um modal com a lista de alunos abaixo da média."""
        self._show_student_list_modal("Alunos em Risco (Média < 5.0)", self.failed_details_data, COLOR_RISK)

    def _show_student_list_modal(self, title: str, data: List[Dict[str, Any]], score_color: str) -> None:
        if not data:
            messagebox.showinfo("Informação", "Nenhum aluno nesta categoria no momento.")
            return

        dialog = BaseDialog(self, title)
        dialog.geometry("500x400")
        dialog.center_on_screen()

        ctk.CTkLabel(dialog, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        bind_global_mouse_scroll(scroll_frame)

        for item in data:
            row_frame = ctk.CTkFrame(scroll_frame)
            row_frame.pack(fill="x", pady=2)

            text = f"{item['student_name']} - {item['course_name']} ({item['class_name']})"
            score_text = f"Média: {item['average']}"

            ctk.CTkLabel(row_frame, text=text, anchor="w").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(row_frame, text=score_text, text_color=score_color, font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10, pady=5)

    def _create_stat_card(self, parent: ctk.CTkFrame, title: str, value: str, row: int, col: int) -> ctk.CTkLabel:
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_GRAY).pack(pady=(10, 0))
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"))
        value_label.pack(pady=(0, 10))
        return value_label
