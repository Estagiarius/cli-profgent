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
# Importa a biblioteca 'customtkinter' para criar os componentes da interface.
import customtkinter as ctk
# Importa tipos para anotações, melhorando a clareza e a robustez do código.
from typing import Dict, Callable, List
from app.ui.views.bncc_selection_dialog import BNCCSelectionDialog
from app.ui.views.base_dialog import BaseDialog

# Define a classe AddDialog, que herda de BaseDialog para criar uma janela secundária (pop-up).
class AddDialog(BaseDialog):
    # O método construtor da janela de diálogo.
    def __init__(self, parent, title: str, fields: Dict[str, str], dropdowns: Dict[str, List[str]] = None, save_callback: Callable = None):
        # Chama o construtor da classe pai.
        super().__init__(parent, title)

        # Armazena a função de callback que será chamada ao salvar.
        self.save_callback = save_callback
        # Cria um dicionário para armazenar os widgets de entrada (campos de texto, menus dropdown).
        self.entries: Dict[str, ctk.CTkEntry | ctk.CTkOptionMenu] = {}

        # Inicializa um contador para o índice da linha no layout de grade.
        row_index = 0

        # Cria os menus dropdown primeiro, se houver algum especificado.
        if dropdowns:
            # Itera sobre os itens do dicionário de dropdowns.
            for key, (label, options) in dropdowns.items():
                # Cria um rótulo (label) para o campo.
                ctk.CTkLabel(self, text=label).grid(row=row_index, column=0, padx=10, pady=10, sticky="w")
                # Cria o menu dropdown com as opções fornecidas.
                dropdown = ctk.CTkOptionMenu(self, values=options)
                # Posiciona o dropdown na grade. 'sticky="ew"' faz com que ele se expanda horizontalmente.
                dropdown.grid(row=row_index, column=1, padx=10, pady=10, sticky="ew")
                # Armazena o widget no dicionário de entradas, usando a 'key' como identificador.
                self.entries[key] = dropdown
                # Incrementa o índice da linha para o próximo widget.
                row_index += 1

        # Cria os campos de entrada de texto.
        for key, label in fields.items():
            ctk.CTkLabel(self, text=label).grid(row=row_index, column=0, padx=10, pady=10, sticky="w")

            # Special handling for BNCC fields
            if key in ['bncc', 'bncc_expected', 'bncc_codes']:
                frame = ctk.CTkFrame(self, fg_color="transparent")
                frame.grid(row=row_index, column=1, padx=10, pady=10, sticky="ew")
                frame.grid_columnconfigure(0, weight=1)

                entry = ctk.CTkEntry(frame)
                entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

                btn = ctk.CTkButton(frame, text="Selecionar", width=80, command=lambda e=entry: self._open_bncc_selector(e))
                btn.grid(row=0, column=1)

                self.entries[key] = entry
            else:
                # Cria o campo de entrada (entry) normal.
                entry = ctk.CTkEntry(self)
                # Posiciona o campo na grade.
                entry.grid(row=row_index, column=1, padx=10, pady=10, sticky="ew")
                # Armazena o widget no dicionário de entradas.
                self.entries[key] = entry

            # Incrementa o índice da linha.
            row_index += 1

        # Cria o botão "Salvar" que aciona o método `save`.
        save_button = ctk.CTkButton(self, text="Salvar", command=self.save)
        # Posiciona o botão na grade, fazendo-o ocupar duas colunas ('columnspan=2').
        save_button.grid(row=row_index, column=0, columnspan=2, padx=10, pady=20)

    def _open_bncc_selector(self, entry_widget):
        def on_select(result_string):
            entry_widget.delete(0, "end")
            entry_widget.insert(0, result_string)

        BNCCSelectionDialog(self, initial_selection=entry_widget.get(), callback=on_select)

    # Método chamado quando o botão "Salvar" é clicado.
    def save(self):
        # Cria um dicionário 'data' coletando o valor de cada widget de entrada.
        # O método `.get()` é usado para obter o valor de CTkEntry e CTkOptionMenu.
        data = {key: widget.get() for key, widget in self.entries.items()}
        # Se uma função de callback foi fornecida no construtor...
        if self.save_callback:
            # ...chama essa função, passando o dicionário de dados coletados.
            self.save_callback(data)
        # Fecha a janela de diálogo após salvar.
        self.destroy()
