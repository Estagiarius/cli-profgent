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
import customtkinter as ctk
from tkinter import messagebox
from app.services import data_service
from app.ui.views.base_dialog import BaseDialog

class CopyLessonDialog(BaseDialog):
    def __init__(self, parent, source_class_id, source_subject_id, callback=None):
        super().__init__(parent, "Copiar Aulas")
        self.source_class_id = source_class_id
        self.source_subject_id = source_subject_id
        self.callback = callback

        self.geometry("720x480")
        self.center_on_screen()

        self.grid_rowconfigure(2, weight=1) # Lista de aulas expande
        self.grid_columnconfigure(0, weight=1)

        # 1. Seleção de Destino
        self.target_frame = ctk.CTkFrame(self)
        self.target_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.target_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.target_frame, text="Copiar Para (Turma):").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.class_combo = ctk.CTkOptionMenu(self.target_frame, command=self.on_class_change)
        self.class_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.target_frame, text="Disciplina de Destino:").grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.subject_combo = ctk.CTkOptionMenu(self.target_frame)
        self.subject_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # 2. Seleção de Conteúdo (Aulas)
        ctk.CTkLabel(self, text="Selecione as Aulas para Copiar:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        self.lessons_frame = ctk.CTkScrollableFrame(self)
        self.lessons_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")

        self.select_all_var = ctk.BooleanVar(value=False)
        self.select_all_check = ctk.CTkCheckBox(self, text="Selecionar Todas", variable=self.select_all_var, command=self.toggle_select_all)
        self.select_all_check.grid(row=3, column=0, padx=20, pady=5, sticky="w")

        # 3. Ações
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        self.copy_button = ctk.CTkButton(self.actions_frame, text="Copiar Aulas", command=self.copy_lessons)
        self.copy_button.pack(side="right", padx=10)

        self.cancel_button = ctk.CTkButton(self.actions_frame, text="Cancelar", fg_color="transparent", border_width=1, command=self.destroy)
        self.cancel_button.pack(side="right", padx=10)

        # Dados internos
        self.lesson_vars = {} # {lesson_id: BooleanVar}
        self.target_classes_map = {} # {class_name: class_id}
        self.target_subjects_map = {} # {subject_name: subject_id}

        # Inicialização
        self.load_target_classes()
        self.load_source_lessons()

    def load_target_classes(self):
        all_classes = data_service.get_all_classes()
        # Filtra a turma atual
        target_classes = [c for c in all_classes if c['id'] != self.source_class_id]

        if not target_classes:
            self.class_combo.set("Nenhuma outra turma disponível")
            self.class_combo.configure(state="disabled")
            self.copy_button.configure(state="disabled")
            return

        self.target_classes_map = {c['name']: c['id'] for c in target_classes}
        self.class_combo.configure(values=list(self.target_classes_map.keys()))

        # Seleciona a primeira
        first_class = list(self.target_classes_map.keys())[0]
        self.class_combo.set(first_class)
        self.on_class_change(first_class)

    def on_class_change(self, class_name):
        class_id = self.target_classes_map.get(class_name)
        if not class_id: return

        subjects = data_service.get_subjects_for_class(class_id)

        if not subjects:
            self.subject_combo.set("Nenhuma disciplina nesta turma")
            self.subject_combo.configure(state="disabled", values=[])
            self.target_subjects_map = {}
            return

        self.target_subjects_map = {s['course_name']: s['id'] for s in subjects}
        self.subject_combo.configure(state="normal", values=list(self.target_subjects_map.keys()))

        # Tenta auto-selecionar a disciplina com o mesmo nome da origem
        # Precisamos saber o nome da disciplina de origem.
        # Vamos buscar...
        # Como otimização, poderíamos ter passado o nome no init, mas vamos buscar rapidinho.
        # Mas `source_subject_id` é `ClassSubject.id`. Precisamos do `Course` name.
        # O `get_subjects_for_class` da origem tem isso.

        source_subjects = data_service.get_subjects_for_class(self.source_class_id)
        source_subject_name = next((s['course_name'] for s in source_subjects if s['id'] == self.source_subject_id), "")

        if source_subject_name and source_subject_name in self.target_subjects_map:
            self.subject_combo.set(source_subject_name)
        else:
            self.subject_combo.set(list(self.target_subjects_map.keys())[0])

    def load_source_lessons(self):
        lessons = data_service.get_lessons_for_subject(self.source_subject_id)

        for widget in self.lessons_frame.winfo_children(): widget.destroy()
        self.lesson_vars = {}

        if not lessons:
            ctk.CTkLabel(self.lessons_frame, text="Nenhuma aula encontrada para copiar.").pack(pady=20)
            self.copy_button.configure(state="disabled")
            self.select_all_check.configure(state="disabled")
            return

        for lesson in lessons:
            var = ctk.BooleanVar(value=False)
            self.lesson_vars[lesson['id']] = var

            checkbox = ctk.CTkCheckBox(
                self.lessons_frame,
                text=f"{lesson['date']} - {lesson['title']}",
                variable=var,
                command=self.check_select_all_state
            )
            checkbox.pack(anchor="w", padx=10, pady=5)

    def toggle_select_all(self):
        state = self.select_all_var.get()
        for var in self.lesson_vars.values():
            var.set(state)

    def check_select_all_state(self):
        # Se todos estiverem marcados, marca o Select All. Caso contrário, desmarca.
        if not self.lesson_vars: return
        all_checked = all(var.get() for var in self.lesson_vars.values())
        self.select_all_var.set(all_checked)

    def copy_lessons(self):
        target_subject_name = self.subject_combo.get()
        target_subject_id = self.target_subjects_map.get(target_subject_name)

        if not target_subject_id:
            messagebox.showerror("Erro", "Selecione uma disciplina de destino válida.")
            return

        selected_ids = [lid for lid, var in self.lesson_vars.items() if var.get()]

        if not selected_ids:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma aula para copiar.")
            return

        try:
            count = data_service.copy_lessons(selected_ids, target_subject_id)
            messagebox.showinfo("Sucesso", f"{count} aulas copiadas com sucesso!")

            if self.callback:
                self.callback()

            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao copiar aulas: {e}")
