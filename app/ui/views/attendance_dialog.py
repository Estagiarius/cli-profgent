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
from app.ui.views.base_dialog import BaseDialog

class AttendanceDialog(BaseDialog):
    def __init__(self, parent, title, lesson_id, students, attendance_map, save_callback):
        super().__init__(parent, title)
        self.geometry("1280x720")
        self.resizable(False, True)

        self.lesson_id = lesson_id
        self.students = students # List of student dicts (id, name)
        self.attendance_map = attendance_map # Dict {student_id: status}
        self.save_callback = save_callback

        self.result_map = {} # To store {student_id: variable}

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Scrollable Frame for Students
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(1, weight=1)

        # Headers
        ctk.CTkLabel(self.scroll_frame, text="Aluno", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.scroll_frame, text="Status", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5)

        # Populate List
        self.status_vars = {}

        for i, student in enumerate(self.students, start=1):
            name = student['name']
            sid = student['id']
            current_status = self.attendance_map.get(sid, 'P')

            ctk.CTkLabel(self.scroll_frame, text=name).grid(row=i, column=0, padx=10, pady=5, sticky="w")

            # Segmented Button for P/F/J/A
            seg_btn = ctk.CTkSegmentedButton(self.scroll_frame, values=["P", "F", "J", "A"])
            seg_btn.set(current_status)
            seg_btn.grid(row=i, column=1, padx=10, pady=5)

            self.status_vars[sid] = seg_btn

        # Actions Frame
        self.actions_frame = ctk.CTkFrame(self)
        self.actions_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkButton(self.actions_frame, text="Salvar Chamada", command=self.on_save).pack(side="right", padx=10, pady=10)
        ctk.CTkButton(self.actions_frame, text="Cancelar", fg_color="transparent", border_width=1, command=self.destroy).pack(side="right", padx=10, pady=10)

        # Mark all buttons
        ctk.CTkButton(self.actions_frame, text="Marcar Todos Presentes", command=lambda: self.set_all('P')).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(self.actions_frame, text="Marcar Todos Faltantes", fg_color="#D9534F", hover_color="#C9302C", command=lambda: self.set_all('F')).pack(side="left", padx=10, pady=10)

    def set_all(self, status):
        for btn in self.status_vars.values():
            btn.set(status)

    def on_save(self):
        data = []
        for sid, btn in self.status_vars.items():
            status = btn.get()
            data.append({"student_id": sid, "status": status})

        self.save_callback(self.lesson_id, data)
        self.destroy()
