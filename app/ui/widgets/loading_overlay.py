# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-01-29
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.

import customtkinter as ctk

class LoadingOverlay(ctk.CTkFrame):
    """
    Um overlay de carregamento que cobre o frame pai e exibe um indicador de progresso.
    """
    def __init__(self, parent, text="Carregando..."):
        super().__init__(parent, fg_color=("gray90", "gray20"), corner_radius=0)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0)

        self.label = ctk.CTkLabel(self.container, text=text, font=ctk.CTkFont(size=16, weight="bold"))
        self.label.pack(pady=(0, 10))

        self.progress = ctk.CTkProgressBar(self.container, mode="indeterminate", width=200)
        self.progress.pack()
        self.progress.start()

        # Garante que o overlay esteja no topo
        self.lift()

    def update_text(self, text):
        self.label.configure(text=text)

    def destroy(self):
        self.progress.stop()
        super().destroy()
