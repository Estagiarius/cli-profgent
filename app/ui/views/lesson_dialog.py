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
from datetime import date, datetime
from app.services import data_service
from app.ui.views.bncc_selection_dialog import BNCCSelectionDialog
from app.ui.views.base_dialog import BaseDialog
from tkinter import messagebox

class LessonDialog(BaseDialog):
    def __init__(self, parent, class_subject_id, lesson_date, lesson_data=None, on_save=None):
        super().__init__(parent, "Registro de Aula")
        self.geometry("1600x900")
        self.class_subject_id = class_subject_id
        self.lesson_date = lesson_date
        self.lesson_data = lesson_data
        self.on_save = on_save

        # Configurações de layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Labels e Entradas
        ctk.CTkLabel(self, text="Título:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Título da Aula")
        self.title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Data (AAAA-MM-DD):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Preenche data automaticamente
        self.date_entry.insert(0, lesson_date.isoformat())

        # BNCC Codes
        ctk.CTkLabel(self, text="BNCC:").grid(row=2, column=0, padx=10, pady=10, sticky="w")

        bncc_frame = ctk.CTkFrame(self, fg_color="transparent")
        bncc_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.bncc_entry = ctk.CTkEntry(bncc_frame)
        self.bncc_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def open_selector():
            BNCCSelectionDialog(self, initial_selection=self.bncc_entry.get(),
                                callback=lambda codes: (self.bncc_entry.delete(0, "end"), self.bncc_entry.insert(0, codes)))

        ctk.CTkButton(bncc_frame, text="Select", width=60, command=open_selector).pack(side="right")

        ctk.CTkLabel(self, text="Conteúdo:").grid(row=3, column=0, padx=10, pady=10, sticky="nw")
        self.content_text = ctk.CTkTextbox(self)
        self.content_text.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

        # Botões
        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.save_button = ctk.CTkButton(self.buttons_frame, text="Salvar", command=self.save)
        self.save_button.pack(side="right", padx=10)

        self.cancel_button = ctk.CTkButton(self.buttons_frame, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1)
        self.cancel_button.pack(side="right", padx=10)

        # Se for edição, popula campos
        if self.lesson_data:
            self.title_entry.insert(0, self.lesson_data['title'])
            self.content_text.insert("1.0", self.lesson_data['content'] or "")
            if self.lesson_data.get('bncc_codes'):
                self.bncc_entry.insert(0, self.lesson_data.get('bncc_codes'))
            # Data já foi inserida no init, mas garantimos que use a do lesson se fornecida (embora deva bater com o argumento)
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, self.lesson_data['date'])

    def save(self):
        title = self.title_entry.get()
        content = self.content_text.get("1.0", "end-1c")
        date_str = self.date_entry.get()
        bncc_codes = self.bncc_entry.get()

        if not title or not date_str:
            messagebox.showerror("Erro", "Título e Data são obrigatórios.")
            return

        try:
            final_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use AAAA-MM-DD.")
            return

        try:
            if self.lesson_data:
                # Update
                data_service.update_lesson(self.lesson_data['id'], title, content, final_date, bncc_codes)
            else:
                # Create
                data_service.create_lesson(self.class_subject_id, title, content, final_date, bncc_codes)

            messagebox.showinfo("Sucesso", "Aula registrada com sucesso!")
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {e}")
