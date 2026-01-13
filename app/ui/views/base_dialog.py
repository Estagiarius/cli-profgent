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

class BaseDialog(ctk.CTkToplevel):
    """
    Classe base para diálogos modais que garante comportamento consistente
    em diferentes sistemas operacionais (Windows, Linux, macOS).
    """
    def __init__(self, parent, title: str = "Dialog", **kwargs):
        super().__init__(parent, **kwargs)
        self.title(title)

        # Aplica configurações para garantir que o diálogo seja modal e
        # apareça corretamente acima da janela pai (Z-order fix).
        self.transient(parent)
        self.lift()
        self.focus_force()
        self.grab_set()

    def center_on_screen(self):
        """Centraliza a janela na tela."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
