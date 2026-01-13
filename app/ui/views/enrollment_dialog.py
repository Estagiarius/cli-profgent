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
from typing import List, Dict, Callable, Any, Set
from app.ui.views.base_dialog import BaseDialog

class EnrollmentDialog(BaseDialog):
    def __init__(self, parent, title: str, students: List[Dict[str, Any]], enroll_callback: Callable[[List[int]], None]):
        super().__init__(parent, title)
        self.geometry("1280x720")

        self.students = students
        self.enroll_callback = enroll_callback

        # Performance limit
        self.DISPLAY_LIMIT = 50

        # Debounce timer
        self._search_job = None

        # Independent set to track selected IDs across filters/renders
        self.selected_ids: Set[int] = set()

        self._setup_ui()
        # Initial population
        self._populate_list()

    def _setup_ui(self):
        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Search Area ---
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Buscar aluno por nome...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        # Bind key release to filter with debounce
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        # --- List Area ---
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # --- Actions Area ---
        self.actions_frame = ctk.CTkFrame(self)
        self.actions_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.enroll_button = ctk.CTkButton(self.actions_frame, text="Matricular Selecionados", command=self._on_enroll)
        self.enroll_button.pack(side="right", padx=10, pady=10)

        self.cancel_button = ctk.CTkButton(self.actions_frame, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1)
        self.cancel_button.pack(side="right", padx=10, pady=10)

    def _on_search_key(self, event):
        """Schedule the search to run after a delay (debounce)."""
        if self._search_job:
            self.after_cancel(self._search_job)
        self._search_job = self.after(300, lambda: self._populate_list(self.search_entry.get()))

    def _toggle_selection(self, student_id: int, var: ctk.BooleanVar):
        """Callback to update the independent set of selected IDs."""
        if var.get():
            self.selected_ids.add(student_id)
        else:
            self.selected_ids.discard(student_id)

    def _populate_list(self, filter_text: str = ""):
        # Clear existing widgets in the scrollable frame
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        filter_text = filter_text.lower()

        # Header Row
        header_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(header_frame, text="Nome", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(35, 10))
        ctk.CTkLabel(header_frame, text="Nascimento", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)

        count = 0
        total_matches = 0

        for student in self.students:
            full_name = f"{student['first_name']} {student['last_name']}"

            if filter_text and filter_text not in full_name.lower():
                continue

            total_matches += 1

            # Stop rendering if limit reached
            if count >= self.DISPLAY_LIMIT:
                continue

            student_id = student['id']

            # Row Container
            row_frame = ctk.CTkFrame(self.list_frame)
            row_frame.pack(fill="x", padx=5, pady=2)

            # Initialize checkbox state based on persistent set
            is_selected = student_id in self.selected_ids
            check_var = ctk.BooleanVar(value=is_selected)

            # Create closure to capture correct student_id and var
            cmd = lambda s_id=student_id, v=check_var: self._toggle_selection(s_id, v)

            chk = ctk.CTkCheckBox(
                row_frame,
                text=full_name,
                variable=check_var,
                command=cmd,
                width=20,
                height=20
            )
            chk.pack(side="left", padx=5, pady=5)

            # Birth Date Display
            birth_date_str = student.get('birth_date') or "N/A"
            if birth_date_str != "N/A" and "-" in birth_date_str:
                try:
                    parts = birth_date_str.split("-")
                    if len(parts) == 3:
                        birth_date_str = f"{parts[2]}/{parts[1]}/{parts[0]}"
                except:
                    pass

            ctk.CTkLabel(row_frame, text=birth_date_str).pack(side="right", padx=10)

            count += 1

        if total_matches == 0:
            ctk.CTkLabel(self.list_frame, text="Nenhum aluno encontrado.").pack(pady=20)
        elif total_matches > self.DISPLAY_LIMIT:
             diff = total_matches - self.DISPLAY_LIMIT
             ctk.CTkLabel(self.list_frame, text=f"...e mais {diff} resultados. Digite para refinar.").pack(pady=10)

    def _on_enroll(self):
        if not self.selected_ids:
            return

        self.enroll_callback(list(self.selected_ids))
        self.destroy()
