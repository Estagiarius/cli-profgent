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
import customtkinter as ctk # Importa a biblioteca 'customtkinter' para os componentes da interface.
from app.services import data_service # Importa o serviço de dados para acessar as informações do banco.
# Importa as janelas de diálogo personalizadas para adicionar e editar.
from app.ui.views.add_dialog import AddDialog
from app.ui.views.edit_dialog import EditDialog
from app.ui.ui_utils import bind_global_mouse_scroll # Importa utilitário de rolagem
from app.ui.views.copy_class_dialog import CopyClassDialog
from app.ui.widgets.loading_overlay import LoadingOverlay # Importa o overlay de carregamento.
from app.utils.async_utils import run_async_task # Importa o utilitário assíncrono.
from customtkinter import CTkInputDialog # Importa a janela de diálogo de entrada de texto padrão do customtkinter.
from tkinter import messagebox # Importa a biblioteca tkinter para exibir caixas de mensagem.
import asyncio

# Define a classe para a tela de seleção de turmas.
class ClassSelectionView(ctk.CTkFrame):
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        # Configura o layout de grade da view.
        self.grid_rowconfigure(1, weight=1) # A linha 1 (com a lista) se expande.
        self.grid_columnconfigure(1, weight=1) # A coluna 1 (onde está o botão de adicionar) se expande.

        # Rótulo do título da tela.
        self.title_label = ctk.CTkLabel(self, text="Minhas Turmas", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Botão para abrir o pop-up de adição de nova turma.
        self.add_class_button = ctk.CTkButton(self, text="Adicionar Nova Turma", command=self.add_class_popup)
        self.add_class_button.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")

        # Frame com rolagem onde os cards das turmas serão exibidos.
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Selecione uma turma para ver os detalhes")
        self.scrollable_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Permite que os cards se expandam horizontalmente.
        bind_global_mouse_scroll(self.scrollable_frame)

    # Método estático para buscar dados em thread separada
    @staticmethod
    def _fetch_classes():
        return data_service.get_all_classes()

    # Callback executado na thread principal após buscar dados
    def _on_classes_fetched(self, classes_data):
        if isinstance(classes_data, Exception):
            # Se houve erro, remove overlay imediatamente para mostrar o erro
            if hasattr(self, 'loading_overlay') and self.loading_overlay:
                self.loading_overlay.destroy()
                self.loading_overlay = None
            messagebox.showerror("Erro", f"Erro ao carregar turmas: {classes_data}")
            return

        # Popula a lista com os dados recebidos
        self.populate_class_cards(classes_data)

        # Força o processamento de tarefas de geometria pendentes (renderização dos cards)
        self.update_idletasks()

        # Remove o overlay com um pequeno atraso para garantir que o usuário veja a tela pronta
        if hasattr(self, 'loading_overlay') and self.loading_overlay:
            self.after(100, self._remove_overlay)

    def _remove_overlay(self):
        if hasattr(self, 'loading_overlay') and self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None

    # Método para criar os cards na tela, agora recebendo os dados como argumento.
    def populate_class_cards(self, classes_data=None):
        # Se os dados não forem fornecidos, dispara o carregamento assíncrono
        if classes_data is None:
            self.load_classes_async()
            return

        # Limpa todos os widgets existentes no frame de rolagem antes de recriá-los.
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Itera sobre os dados de cada turma.
        for i, class_data in enumerate(classes_data):
            # Cria um widget de card para a turma.
            card = self.create_class_card(self.scrollable_frame, class_data)
            # Posiciona o card na grade do frame de rolagem.
            card.grid(row=i, column=0, padx=10, pady=10, sticky="ew")

    # Inicia o processo de carregamento assíncrono
    def load_classes_async(self):
        # Exibe o overlay de carregamento
        if not hasattr(self, 'loading_overlay') or self.loading_overlay is None:
            self.loading_overlay = LoadingOverlay(self, text="Carregando Turmas...")

        # Dispara a tarefa assíncrona
        run_async_task(
            asyncio.to_thread(self._fetch_classes),
            self.main_app.loop,
            self.main_app.async_queue,
            self._on_classes_fetched
        )

    # Método que cria um único widget de card para uma turma.
    def create_class_card(self, parent, class_data):
        # O card é um CTkFrame.
        card = ctk.CTkFrame(parent)
        card.grid_columnconfigure(0, weight=1) # A coluna 0 (com as informações) se expande.

        # Rótulo com o nome da turma.
        class_name_label = ctk.CTkLabel(card, text=class_data["name"], font=ctk.CTkFont(size=16, weight="bold"))
        class_name_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        # Rótulo com a contagem de alunos.
        student_count_label = ctk.CTkLabel(card, text=f"{class_data['student_count']} alunos matriculados", font=ctk.CTkFont(size=10))
        student_count_label.grid(row=1, column=0, padx=15, pady=(5, 10), sticky="w")

        # Frame para agrupar os botões de ação (Detalhes, Editar, Excluir).
        actions_frame = ctk.CTkFrame(card)
        actions_frame.grid(row=0, column=1, rowspan=3, padx=15, pady=15, sticky="e")

        # Botão "Ver Detalhes". O lambda é usado para passar o ID da turma para a função.
        details_button = ctk.CTkButton(actions_frame, text="Ver Detalhes", command=lambda c=class_data["id"]: self.view_class_details(c))
        details_button.pack(side="top", fill="x", padx=5, pady=5)

        # Botão "Editar".
        edit_button = ctk.CTkButton(actions_frame, text="Editar", command=lambda c=class_data: self.edit_class_popup(c))
        edit_button.pack(side="top", fill="x", padx=5, pady=5)

        # Botão "Copiar Turma".
        copy_button = ctk.CTkButton(actions_frame, text="Copiar Turma", fg_color="green", command=lambda c=class_data: self.copy_class_popup(c))
        copy_button.pack(side="top", fill="x", padx=5, pady=5)

        # Botão "Excluir".
        delete_button = ctk.CTkButton(actions_frame, text="Excluir", fg_color="red", command=lambda c_id=class_data["id"]: self.delete_class_action(c_id))
        delete_button.pack(side="top", fill="x", padx=5, pady=5)

        return card

    # Ação de deletar uma turma após confirmação do usuário.
    def delete_class_action(self, class_id):
        # Cria um diálogo de confirmação que exige que o usuário digite 'DELETE'.
        dialog = CTkInputDialog(text="Esta é uma ação destrutiva. Todas as matrículas e notas relacionadas a esta turma serão perdidas.\nDigite 'DELETE' para confirmar a exclusão:", title="Confirmar Exclusão")
        user_input = dialog.get_input()
        # Se o usuário confirmou corretamente.
        if user_input == "DELETE":
            # Chama o serviço para deletar a turma.
            data_service.delete_class(class_id)
            # Atualiza a lista de cards na tela.
            self.load_classes_async()

    # Navega para a tela de detalhes da turma.
    def view_class_details(self, class_id):
        # Chama o método da aplicação principal para mostrar a view 'class_detail', passando o ID da turma.
        self.main_app.show_view("class_detail", class_id=class_id)

    # Abre o pop-up para editar os dados de uma turma.
    def edit_class_popup(self, class_data):
        # Função de callback que será chamada pelo diálogo ao salvar.
        def save_callback(class_id, data):
            new_name = data.get("name")
            if new_name:
                data_service.update_class(class_id, new_name)
                self.load_classes_async()

        # Configuração dos campos para o diálogo de edição.
        fields = {"name": "Nome da Turma"}
        initial_data = {"id": class_data["id"], "name": class_data["name"]}
        EditDialog(self, "Editar Turma", fields, initial_data, save_callback)

    # Abre o pop-up para copiar uma turma.
    def copy_class_popup(self, class_data):
        def save_callback(data):
            try:
                data_service.copy_class(
                    source_class_id=class_data["id"],
                    new_name=data["name"],
                    copy_subjects=data["copy_subjects"],
                    copy_assessments=data["copy_assessments"],
                    copy_students=data["copy_students"]
                )
                messagebox.showinfo("Sucesso", f"Turma '{class_data['name']}' copiada para '{data['name']}' com sucesso!")
                self.load_classes_async()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro inesperado ao copiar turma: {e}")

        CopyClassDialog(self, title=f"Copiar Turma: {class_data['name']}", callback=save_callback)

    # Abre o pop-up para adicionar uma nova turma.
    def add_class_popup(self):
        # Função de callback para o diálogo de adição.
        def save_callback(data):
            class_name = data.get("name")

            if not class_name:
                messagebox.showerror("Erro", "O nome da turma é obrigatório.")
                return

            try:
                # Chama o serviço para criar a nova turma (agora sem curso obrigatório).
                data_service.create_class(name=class_name)
                # Atualiza a lista de cards.
                self.load_classes_async()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar turma: {e}")

        # Configuração dos campos para o diálogo de adição.
        fields = {"name": "Nome da Turma"}
        # Dropdowns removido, pois não selecionamos mais o curso na criação.
        AddDialog(self, "Adicionar Nova Turma", fields=fields, dropdowns=None, save_callback=save_callback)

    # Método chamado sempre que a view é exibida.
    def on_show(self, **kwargs):
        # Atualiza a lista de turmas para garantir que os dados estejam sempre recentes.
        self.load_classes_async()
