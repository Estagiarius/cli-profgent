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
from app.services.bncc_service import BNCCService
from app.ui.views.base_dialog import BaseDialog

class BNCCSelectionDialog(BaseDialog):
    def __init__(self, parent, title="Selecionar Habilidades BNCC", initial_selection=None, callback=None):
        super().__init__(parent, title)
        self.geometry("1600x900")
        self.callback = callback
        self.selected_codes = set(initial_selection.split(',')) if initial_selection else set()
        # Clean up empty strings
        self.selected_codes = {c.strip() for c in self.selected_codes if c.strip()}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Search
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Buscar por código ou descrição...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        self.search_btn = ctk.CTkButton(self.search_frame, text="Buscar", command=self.perform_search)
        self.search_btn.pack(side="right")

        # List Area
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Buttons & Status Frame
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Status Label (Left)
        self.status_label = ctk.CTkLabel(self.btn_frame, text=f"Selecionados: {len(self.selected_codes)}")
        self.status_label.pack(side="left", padx=10)

        # Buttons (Right)
        ctk.CTkButton(self.btn_frame, text="Confirmar", command=self.confirm).pack(side="right", padx=10)
        ctk.CTkButton(self.btn_frame, text="Cancelar", fg_color="transparent", border_width=1, command=self.destroy).pack(side="right")

        # Initial Search (Show all or filtered)
        self.perform_search()

    def perform_search(self):
        query = self.search_entry.get()
        results = BNCCService.search_skills(query)

        # Clear current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not results:
            ctk.CTkLabel(self.scrollable_frame, text="Nenhum resultado encontrado.").pack(pady=20)
            return

        # Render list (limit to 50 for performance if query is empty)
        limit = 100 if not query else None

        for i, item in enumerate(results):
            if limit and i >= limit:
                ctk.CTkLabel(self.scrollable_frame, text="... Refine sua busca para ver mais ...").pack(pady=10)
                break

            frame = ctk.CTkFrame(self.scrollable_frame)
            frame.pack(fill="x", pady=2)

            chk_var = ctk.BooleanVar(value=item['code'] in self.selected_codes)

            def toggle(code=item['code'], var=chk_var):
                if var.get():
                    self.selected_codes.add(code)
                else:
                    self.selected_codes.discard(code)
                self.status_label.configure(text=f"Selecionados: {len(self.selected_codes)}")

            chk = ctk.CTkCheckBox(frame, text=f"{item['code']} - {item['title']}", variable=chk_var, command=toggle)
            chk.pack(side="top", anchor="w", padx=5, pady=2)

            desc = ctk.CTkLabel(frame, text=item['description'], wraplength=700, text_color="gray")
            desc.pack(side="top", anchor="w", padx=30, pady=(0, 5))

    def confirm(self):
        if self.callback:
            self.callback(",".join(sorted(list(self.selected_codes))))
        self.destroy()
