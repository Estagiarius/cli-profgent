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
# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
from datetime import datetime
# Importa as janelas de diálogo personalizadas para edição e adição.
from app.ui.views.edit_dialog import EditDialog
from app.ui.views.add_dialog import AddDialog
# Importa utilitário de rolagem
from app.ui.ui_utils import bind_global_mouse_scroll
# Importa o diálogo de entrada de texto padrão para confirmação de exclusão.
from customtkinter import CTkInputDialog
from tkinter import messagebox

# Define a classe para a tela de Gestão de Dados.
class ManagementView(ctk.CTkFrame):
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        # Obtém a instância do DataService a partir da aplicação principal.
        self.data_service = self.main_app.data_service
        self.current_page = 1
        self.page_size = 20
        self.total_pages = 1

        # Configura o layout de grade da view.
        self.grid_rowconfigure(1, weight=1) # A linha 1 (com as abas) se expande.
        self.grid_columnconfigure(0, weight=1) # A coluna 0 se expande.

        # Rótulo do título da tela.
        self.title_label = ctk.CTkLabel(self, text="Gestão de Dados", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Cria o widget de abas para organizar a gestão de Alunos, Disciplinas e Notas.
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Adiciona as abas.
        self.tab_view.add("Alunos")
        self.tab_view.add("Disciplinas")
        # Aba "Notas" removida conforme solicitação. Código legado comentado abaixo.
        # self.tab_view.add("Notas")

        # --- Aba de Alunos ---
        students_tab = self.tab_view.tab("Alunos")
        students_tab.grid_rowconfigure(2, weight=1)  # Frame de lista expande
        students_tab.grid_columnconfigure(0, weight=1)

        # Frame para os botões de controle da aba de alunos.
        student_controls_frame = ctk.CTkFrame(students_tab)
        student_controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_student_button = ctk.CTkButton(student_controls_frame, text="Adicionar Novo Aluno", command=self.add_student_popup)
        self.add_student_button.pack(side="left", padx=(0, 10))

        # Busca
        self.search_entry = ctk.CTkEntry(student_controls_frame, placeholder_text="Buscar aluno...")
        self.search_entry.pack(side="left", padx=10, fill="x", expand=True)

        self.search_button = ctk.CTkButton(student_controls_frame, text="Buscar", width=80, command=lambda: self._load_student_page(1))
        self.search_button.pack(side="left", padx=5)

        # Checkbox para filtrar e mostrar apenas alunos com matrículas ativas.
        self.show_active_only = ctk.CTkCheckBox(student_controls_frame, text="Mostrar Apenas Alunos Ativos", command=lambda: self._load_student_page(1))
        self.show_active_only.pack(side="left", padx=10)

        # Cabeçalho da Lista
        header_frame = ctk.CTkFrame(students_tab, height=30)
        header_frame.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")
        ctk.CTkLabel(header_frame, text="ID", width=50, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Nome Completo", anchor="w").pack(side="left", padx=10, fill="x", expand=True)
        ctk.CTkLabel(header_frame, text="Ações", width=150, anchor="e").pack(side="right", padx=10)

        # Frame com rolagem para a lista de alunos.
        self.students_frame = ctk.CTkScrollableFrame(students_tab)
        self.students_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        bind_global_mouse_scroll(self.students_frame)

        # Frame de Paginação
        pagination_frame = ctk.CTkFrame(students_tab)
        pagination_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.btn_prev = ctk.CTkButton(pagination_frame, text="Anterior", width=80, command=self._prev_page)
        self.btn_prev.pack(side="left", padx=10)

        self.lbl_page = ctk.CTkLabel(pagination_frame, text="Página 1 de 1")
        self.lbl_page.pack(side="left", fill="x", expand=True)

        self.btn_next = ctk.CTkButton(pagination_frame, text="Próximo", width=80, command=self._next_page)
        self.btn_next.pack(side="right", padx=10)

        # --- Aba de Disciplinas ---
        courses_tab = self.tab_view.tab("Disciplinas")
        courses_tab.grid_rowconfigure(1, weight=1)
        courses_tab.grid_columnconfigure(0, weight=1)
        self.add_course_button = ctk.CTkButton(courses_tab, text="Adicionar Nova Disciplina", command=self.add_course_popup)
        self.add_course_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.courses_frame = ctk.CTkScrollableFrame(courses_tab)
        self.courses_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        bind_global_mouse_scroll(self.courses_frame)

        # --- Aba de Notas (Código Legado - Comentado) ---
        # grades_tab = self.tab_view.tab("Notas")
        # grades_tab.grid_rowconfigure(1, weight=1)
        # grades_tab.grid_columnconfigure(0, weight=1)
        # ctk.CTkLabel(grades_tab, text="Use a tela 'Quadro de Notas' na visualização da turma para adicionar novas notas.").grid(row=0, column=0, padx=10, pady=10)
        # self.grades_frame = ctk.CTkScrollableFrame(grades_tab)
        # self.grades_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Método chamado sempre que a view é exibida.
    def on_show(self, **kwargs): self.populate_data()
    # Método para preencher os dados de todas as abas de uma vez.
    def populate_data(self):
        # Carrega a primeira página de alunos
        self._load_student_page(1)
        self._populate_courses()
        # self._populate_grades()

    # Método utilitário para limpar todos os widgets de um frame.
    def _clear_frame(self, frame): [w.destroy() for w in frame.winfo_children()]

    def _prev_page(self):
        if self.current_page > 1:
            self._load_student_page(self.current_page - 1)

    def _next_page(self):
        if self.current_page < self.total_pages:
            self._load_student_page(self.current_page + 1)

    # Carrega uma página específica de alunos
    def _load_student_page(self, page_number):
        self._clear_frame(self.students_frame)
        self.current_page = page_number

        search_term = self.search_entry.get().strip()
        active_only = bool(self.show_active_only.get())

        result = self.data_service.get_paginated_students(
            page=self.current_page,
            page_size=self.page_size,
            search_term=search_term if search_term else None,
            active_only=active_only
        )

        # Se a página solicitada estiver vazia e não for a primeira, volta uma página
        # Isso acontece, por exemplo, ao excluir o último item da última página
        if not result["students"] and self.current_page > 1 and result["total_count"] > 0:
             self._load_student_page(self.current_page - 1)
             return

        students = result["students"]
        total_count = result["total_count"]
        self.total_pages = result["total_pages"]
        self.current_page = result["current_page"] # Garante sincronia

        # Atualiza controles de paginação
        self.lbl_page.configure(text=f"Página {self.current_page} de {self.total_pages} (Total: {total_count})")

        state_prev = "normal" if self.current_page > 1 else "disabled"
        state_next = "normal" if self.current_page < self.total_pages else "disabled"
        self.btn_prev.configure(state=state_prev)
        self.btn_next.configure(state=state_next)

        # Itera sobre os alunos e cria uma linha para cada um.
        for student in students:
            f = ctk.CTkFrame(self.students_frame)
            f.pack(fill="x", pady=2)

            # ID
            ctk.CTkLabel(f, text=str(student['id']), width=50, anchor="w").pack(side="left", padx=10)

            # Nome
            name_text = f"{student['first_name']} {student['last_name']}"
            ctk.CTkLabel(f, text=name_text, anchor="w").pack(side="left", padx=10, fill="x", expand=True)

            # Botões
            btn_frame = ctk.CTkFrame(f, fg_color="transparent")
            btn_frame.pack(side="right", padx=5)

            ctk.CTkButton(btn_frame, text="Excluir", fg_color="red", width=60, command=lambda s_id=student['id']: self.delete_student(s_id)).pack(side="right", padx=5)
            ctk.CTkButton(btn_frame, text="Editar", width=60, command=lambda s=student: self.edit_student(s)).pack(side="right", padx=5)

    # Preenche a lista de cursos na aba "Disciplinas".
    def _populate_courses(self):
        self._clear_frame(self.courses_frame)
        for course in self.data_service.get_all_courses():
            f = ctk.CTkFrame(self.courses_frame); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=f"ID: {course['id']} | {course['course_name']} ({course['course_code']})").pack(side="left", padx=10)
            ctk.CTkButton(f, text="Excluir", fg_color="red", command=lambda c_id=course['id']: self.delete_course(c_id)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="Editar", command=lambda c=course: self.edit_course(c)).pack(side="right", padx=5)

    # Preenche a lista de notas na aba "Notas". (Código Legado - Comentado)
    # def _populate_grades(self):
    #     self._clear_frame(self.grades_frame)
    #     # Busca todas as notas com detalhes (nome do aluno, curso, etc.).
    #     grades = self.data_service.get_all_grades_with_details()
    #
    #     for grade in grades:
    #         f = ctk.CTkFrame(self.grades_frame)
    #         f.pack(fill="x", pady=5)
    #
    #         # Atualizado para mostrar Turma e Disciplina
    #         label_text = (
    #             f"ID: {grade['id']} | {grade['student_first_name']} {grade['student_last_name']} | "
    #             f"{grade['class_name']} - {grade['course_name']} | {grade['assessment_name']}: {grade['score']}"
    #         )
    #
    #         ctk.CTkLabel(f, text=label_text).pack(side="left", padx=10)
    #         ctk.CTkButton(f, text="Excluir", fg_color="red", command=lambda g_id=grade['id']: self.delete_grade(g_id)).pack(side="right", padx=5)
    #         # A funcionalidade de edição de notas nesta tela foi removida, pois
    #         # o Quadro de Notas é o local principal para isso.

    # Método auxiliar para exibir um diálogo de confirmação de exclusão.
    def _confirm_delete(self):
        d = CTkInputDialog(text="Digite 'DELETE' para confirmar.", title="Confirmar Exclusão"); return d.get_input() == "DELETE"

    # Métodos de exclusão que chamam o diálogo de confirmação antes de agir.
    def delete_student(self, sid):
        if self._confirm_delete():
            try:
                self.data_service.delete_student(sid)
                self._load_student_page(self.current_page) # Recarrega a página atual
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir aluno: {e}")

    def delete_course(self, cid):
        if self._confirm_delete():
            try:
                self.data_service.delete_course(cid)
                self.populate_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir disciplina: {e}")

    # def delete_grade(self, gid):
    #     if self._confirm_delete():
    #         try:
    #             self.data_service.delete_grade(gid)
    #             self.populate_data()
    #         except Exception as e:
    #             messagebox.showerror("Erro", f"Erro ao excluir nota: {e}")

    # Abre o diálogo de edição para um aluno.
    def edit_student(self, s):
        # Define o callback que será executado ao salvar no diálogo.
        def cb(id, data):
            birth_date_obj = None
            if data['birth_date']:
                try:
                    birth_date_obj = datetime.strptime(data['birth_date'], "%d/%m/%Y").date()
                except ValueError:
                    messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
                    return

            try:
                self.data_service.update_student(id, data['first_name'], data['last_name'], birth_date=birth_date_obj)
                self._load_student_page(self.current_page)
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        # Formata a data de nascimento para exibição (DD/MM/AAAA)
        birth_date_str = ""
        if s.get('birth_date'):
            try:
                # s['birth_date'] vem do DataService como string ISO (YYYY-MM-DD)
                dt = datetime.strptime(s['birth_date'], "%Y-%m-%d")
                birth_date_str = dt.strftime("%d/%m/%Y")
            except ValueError:
                pass

        initial_data = {
            "id": s['id'],
            "first_name": s['first_name'],
            "last_name": s['last_name'],
            "birth_date": birth_date_str
        }

        fields = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "birth_date": "Data de Nascimento (DD/MM/AAAA)"
        }
        EditDialog(self, "Editar Aluno", fields, initial_data, cb)

    # Abre o diálogo de edição para um curso.
    def edit_course(self, c):
        def cb(id, data): self.data_service.update_course(id, data['course_name'], data['course_code'], data.get('bncc_expected')); self.populate_data()
        EditDialog(self, "Editar Disciplina", {"course_name":"Nome", "course_code":"Código", "bncc_expected": "BNCC Esperada (CSV)"}, c, cb)

    # Abre o diálogo de adição para um novo aluno.
    def add_student_popup(self):
        def cb(data):
            birth_date_obj = None
            if data['birth_date']:
                try:
                    birth_date_obj = datetime.strptime(data['birth_date'], "%d/%m/%Y").date()
                except ValueError:
                    messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
                    return

            try:
                self.data_service.add_student(data['first_name'], data['last_name'], birth_date=birth_date_obj)
                self._load_student_page(self.current_page)
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        fields = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "birth_date": "Data de Nascimento (DD/MM/AAAA)"
        }
        AddDialog(self, "Adicionar Aluno", fields, save_callback=cb)

    # Abre o diálogo de adição para um novo curso.
    def add_course_popup(self):
        def cb(data): self.data_service.add_course(data['course_name'], data['course_code']); self.populate_data()
        AddDialog(self, "Adicionar Disciplina", {"course_name":"Nome", "course_code":"Código"}, save_callback=cb)
