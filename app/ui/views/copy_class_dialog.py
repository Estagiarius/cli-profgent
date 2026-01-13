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
from app.ui.views.base_dialog import BaseDialog

class CopyClassDialog(BaseDialog):
    def __init__(self, parent, title="Copiar Turma", initial_name="", callback=None):
        super().__init__(parent, title)
        self.callback = callback
        self.geometry("400x350")
        self.center_on_screen()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Espaço vazio empurra botões para baixo

        # Label e Input do Nome
        self.name_label = ctk.CTkLabel(self, text="Nome da Nova Turma:")
        self.name_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Ex: 6º Ano B")
        self.name_entry.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        if initial_name:
            self.name_entry.insert(0, initial_name)

        # Checkboxes
        self.copy_subjects_var = ctk.BooleanVar(value=True)
        self.copy_assessments_var = ctk.BooleanVar(value=True)
        self.copy_students_var = ctk.BooleanVar(value=True)

        self.subjects_chk = ctk.CTkCheckBox(
            self,
            text="Copiar Disciplinas",
            variable=self.copy_subjects_var,
            command=self._toggle_assessments
        )
        self.subjects_chk.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.assessments_chk = ctk.CTkCheckBox(
            self,
            text="Copiar Avaliações",
            variable=self.copy_assessments_var
        )
        self.assessments_chk.grid(row=3, column=0, padx=40, pady=10, sticky="w") # Indentado para mostrar hierarquia

        self.students_chk = ctk.CTkCheckBox(
            self,
            text="Copiar Alunos (Ativos)",
            variable=self.copy_students_var
        )
        self.students_chk.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        # Botões
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1)

        self.cancel_button = ctk.CTkButton(
            self.buttons_frame,
            text="Cancelar",
            fg_color="transparent",
            border_width=1,
            command=self.destroy
        )
        self.cancel_button.grid(row=0, column=0, padx=10, sticky="ew")

        self.confirm_button = ctk.CTkButton(
            self.buttons_frame,
            text="Copiar",
            command=self._on_confirm
        )
        self.confirm_button.grid(row=0, column=1, padx=10, sticky="ew")

        # Foco no input
        self.after(100, self.name_entry.focus)

    def _toggle_assessments(self):
        # Se desmarcar disciplinas, desmarca e desabilita avaliações
        if not self.copy_subjects_var.get():
            self.copy_assessments_var.set(False)
            self.assessments_chk.configure(state="disabled")
        else:
            self.assessments_chk.configure(state="normal")
            self.copy_assessments_var.set(True)

    def _on_confirm(self):
        new_name = self.name_entry.get().strip()

        data = {
            "name": new_name,
            "copy_subjects": self.copy_subjects_var.get(),
            "copy_assessments": self.copy_assessments_var.get(),
            "copy_students": self.copy_students_var.get()
        }

        if self.callback:
            self.callback(data)

        self.destroy()
