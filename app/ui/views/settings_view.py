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
# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
# Importa funções para salvar e carregar chaves de API de forma segura.
from app.core.security.credentials import get_api_key, save_api_key
# Importa funções para salvar e carregar configurações gerais da aplicação.
from app.core.config import save_setting, load_setting
import sys
import os
# Importa as classes dos provedores de LLM.
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.maritaca_provider import MaritacaProvider
from app.core.llm.open_router_provider import OpenRouterProvider
from app.core.llm.ollama_provider import OllamaProvider
# Importa a função utilitária para executar tarefas assíncronas.
from app.utils.async_utils import run_async_task


# Define a classe para a tela de Configurações.
class SettingsView(ctk.CTkFrame):
    """
    Uma classe que representa a interface de configuração para integração com provedores
    de inteligência artificial. Fornece recursos para selecionar provedores, modelos, chaves
    de API e outras configurações específicas.

    Inclui lógica de interação com a interface, como salvar configurações e atualizar a lista
    de modelos disponíveis, além de diferenciar funcionalidades baseadas no provedor ativo.

    :ivar main_app: Referência para a aplicação principal. Útil para integração
        com eventos assíncronos e outras funcionalidades compartilhadas.
    :ivar provider_frame: Frame que contém a interface para a seleção do provedor de IA ativo.
    :type provider_frame: ctk.CTkFrame
    :ivar provider_var: Variável associada ao menu de seleção do provedor de IA, mantendo
        o valor do provedor ativo.
    :type provider_var: ctk.StringVar
    :ivar provider_menu: Menu de opções para seleção do provedor de IA.
    :type provider_menu: ctk.CTkOptionMenu
    :ivar model_frame: Frame que contém a interface para a seleção ou entrada manual do modelo.
    :type model_frame: ctk.CTkFrame
    :ivar model_var: Variável associada ao menu de seleção de modelos, contendo o modelo atualmente selecionado.
    :type model_var: ctk.StringVar
    :ivar model_menu: Menu de opções para seleção de modelos disponíveis.
    :type model_menu: ctk.CTkOptionMenu
    :ivar model_entry: Campo de entrada para o nome do modelo, usado especialmente para provedores que permitem
        entrada manual, como Ollama.
    :type model_entry: ctk.CTkEntry
    :ivar refresh_button: Botão que atualiza a lista de modelos disponíveis.
    :type refresh_button: ctk.CTkButton
    :ivar ollama_frame: Frame dedicado à configuração específica do servidor Ollama.
    :type ollama_frame: ctk.CTkFrame
    :ivar ollama_entry: Campo de entrada para a URL do servidor Ollama.
    :type ollama_entry: ctk.CTkEntry
    :ivar keys_frame: Frame que contém os campos para entrada das chaves de API dos provedores.
    :type keys_frame: ctk.CTkFrame
    :ivar openai_entry: Campo de entrada para a chave de API do OpenAI.
    :type openai_entry: ctk.CTkEntry
    :ivar maritaca_entry: Campo de entrada para a chave de API do Maritaca.
    :type maritaca_entry: ctk.CTkEntry
    :ivar openrouter_entry: Campo de entrada para a chave de API do OpenRouter.
    :type openrouter_entry: ctk.CTkEntry
    :ivar save_button: Botão que salva todas as configurações da tela.
    :type save_button: ctk.CTkButton
    :ivar feedback_label: Label para exibir mensagens de feedback sobre eventos, como salvamento de configurações.
    :type feedback_label: ctk.CTkLabel
    """
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app

        # Configura o layout de grade da view.
        self.grid_columnconfigure(0, weight=1)

        # --- Aparência e Tema ---
        self.appearance_frame = ctk.CTkFrame(self)
        self.appearance_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(self.appearance_frame, text="Tema da Aplicação").pack(side="left", padx=10, pady=10)

        self.theme_map = {
            "Black & Orange": "app/ui/themes/black_orange.json",
            "Ocean Breeze": "app/ui/themes/ocean_breeze.json",
            "Dracula": "app/ui/themes/dracula.json",
            "Forest Glade": "app/ui/themes/forest_glade.json",
            "Padrão (Azul)": "blue" # Fallback to default
        }
        self.theme_var = ctk.StringVar(value=load_setting("app_theme_name", "Black & Orange"))
        self.theme_menu = ctk.CTkOptionMenu(self.appearance_frame, values=list(self.theme_map.keys()), variable=self.theme_var)
        self.theme_menu.pack(side="left", padx=10, pady=10)

        self.save_theme_button = ctk.CTkButton(self.appearance_frame, text="Salvar Tema", command=self.save_theme_only)
        self.save_theme_button.pack(side="left", padx=5)

        self.restart_button = ctk.CTkButton(self.appearance_frame, text="Salvar e Reiniciar", command=self.save_theme_and_restart, fg_color="#b91c1c", hover_color="#991b1b")
        self.restart_button.pack(side="left", padx=5)


        # --- Seleção do Provedor de IA ---
        self.provider_frame = ctk.CTkFrame(self)
        self.provider_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(self.provider_frame, text="Provedor de IA Ativo").pack(side="left", padx=10, pady=10)
        # Cria uma variável de string do tkinter para o menu, inicializada com a configuração salva.
        self.provider_var = ctk.StringVar(value=load_setting("active_provider", "OpenAI"))
        self.provider_menu = ctk.CTkOptionMenu(self.provider_frame, values=["OpenAI", "Maritaca", "OpenRouter", "Ollama"], variable=self.provider_var, command=self.provider_changed)
        self.provider_menu.pack(side="right", padx=10, pady=10)

        # --- Seleção do Modelo ---
        self.model_frame = ctk.CTkFrame(self)
        self.model_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.model_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.model_frame, text="Selecione/Digite o Modelo").grid(row=0, column=0, padx=10, pady=10)
        self.model_var = ctk.StringVar()
        self.model_menu = ctk.CTkOptionMenu(self.model_frame, variable=self.model_var, values=["(Atualize para carregar)"], command=self.model_changed)
        self.model_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        # Campo de entrada manual, especialmente para Ollama.
        self.model_entry = ctk.CTkEntry(self.model_frame, placeholder_text="Ou digite o nome do modelo manualmente")
        self.model_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.refresh_button = ctk.CTkButton(self.model_frame, text="Atualizar Lista", command=self.refresh_models)
        self.refresh_button.grid(row=0, column=2, padx=10, pady=10)

        # --- Seções de Configuração Específicas ---
        # Frame para a configuração do servidor Ollama.
        self.ollama_frame = ctk.CTkFrame(self)
        self.ollama_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(self.ollama_frame, text="URL do Servidor Ollama").pack(side="left", padx=10, pady=10)
        self.ollama_entry = ctk.CTkEntry(self.ollama_frame, width=300)
        self.ollama_entry.insert(0, load_setting("ollama_url", "http://localhost:11434/v1"))
        self.ollama_entry.pack(side="right", fill="x", expand=True, padx=10, pady=10)

        # Frame para as chaves de API.
        self.keys_frame = ctk.CTkFrame(self); self.keys_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.keys_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.keys_frame, text="Chave OpenAI").grid(row=0, column=0, padx=10, pady=5, sticky="w"); self.openai_entry = ctk.CTkEntry(self.keys_frame); self.openai_entry.grid(row=0, column=1, padx=10, sticky="ew")
        ctk.CTkLabel(self.keys_frame, text="Chave Maritaca").grid(row=1, column=0, padx=10, pady=5, sticky="w"); self.maritaca_entry = ctk.CTkEntry(self.keys_frame); self.maritaca_entry.grid(row=1, column=1, padx=10, sticky="ew")
        ctk.CTkLabel(self.keys_frame, text="Chave OpenRouter").grid(row=2, column=0, padx=10, pady=5, sticky="w"); self.openrouter_entry = ctk.CTkEntry(self.keys_frame); self.openrouter_entry.grid(row=2, column=1, padx=10, sticky="ew")

        # --- Controles (Botão Salvar e Feedback) ---
        self.save_button = ctk.CTkButton(self, text="Salvar Configurações", command=self.save_settings); self.save_button.grid(row=5, column=0, padx=20, pady=20, sticky="e")
        self.feedback_label = ctk.CTkLabel(self, text=""); self.feedback_label.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        # Chama a função de atualização da lista de modelos quando a tela se torna visível.
        self.bind("<Visibility>", lambda event: self.refresh_models())
        # Chama a função para ajustar a UI com base no provedor selecionado inicialmente.
        self.provider_changed(self.provider_var.get())

    # Chamado quando o usuário seleciona um novo provedor de IA.
    def provider_changed(self, choice):
        save_setting("active_provider", choice)
        self.feedback_label.configure(text=f"{choice} agora está ativo.")
        # Mostra ou esconde o campo de entrada manual de modelo se o provedor for Ollama.
        is_ollama = choice == "Ollama"
        if is_ollama: self.model_entry.grid()
        else: self.model_entry.grid_remove()
        # Atualiza a lista de modelos disponíveis para o novo provedor.
        self.refresh_models()

    # Chamado quando um modelo é selecionado no dropdown.
    def model_changed(self, choice):
        # Se for Ollama, preenche o campo de entrada manual com o modelo selecionado no dropdown.
        if self.provider_var.get() == "Ollama":
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, choice)
        # Salva a nova configuração de modelo.
        self.save_model_setting()

    # Salva a configuração do modelo selecionado.
    def save_model_setting(self):
        provider = self.provider_var.get().lower()
        # Para Ollama, o modelo a ser salvo vem do campo de entrada; para outros, vem do dropdown.
        model_to_save = self.model_entry.get() if provider == "ollama" and self.model_entry.get() else self.model_var.get()
        # Evita salvar valores de status como "Carregando...".
        if "(No models" not in model_to_save and "Loading..." not in model_to_save:
            save_setting(f"{provider}_model", model_to_save)
            self.feedback_label.configure(text=f"Modelo de {provider} definido para: {model_to_save}", text_color="green")

    # Salva todas as configurações da tela.
    def save_settings(self):
        self.save_model_setting()
        save_setting("ollama_url", self.ollama_entry.get())
        # Itera sobre os provedores e seus respectivos campos de entrada de chave de API.
        for service, entry in [("OpenAI", self.openai_entry), ("Maritaca", self.maritaca_entry), ("OpenRouter", self.openrouter_entry)]:
            # Se um valor foi digitado no campo, salva a chave de API.
            if entry.get(): save_api_key(service, entry.get())
        self.feedback_label.configure(text="Configurações salvas!", text_color="green")

    def save_theme_only(self):
        theme_name = self.theme_var.get()
        theme_path = self.theme_map.get(theme_name)
        if theme_path:
            save_setting("app_theme_name", theme_name)
            save_setting("app_theme_path", theme_path)
            self.feedback_label.configure(text="Tema salvo. Reinicie a aplicação para aplicar todas as mudanças.", text_color="orange")

    def save_theme_and_restart(self):
        self.save_theme_only()
        # Reinicia a aplicação
        self.feedback_label.configure(text="Reiniciando...", text_color="orange")
        self.after(500, lambda: os.execl(sys.executable, sys.executable, *sys.argv))

    # Inicia o processo assíncrono de atualização da lista de modelos.
    def refresh_models(self):
        self.model_menu.configure(values=["Carregando..."]); self.model_var.set("Carregando...")
        self.refresh_button.configure(state="disabled")

        provider_name = self.provider_var.get()
        # Lê os valores da UI na thread principal antes de passar para a coroutine.
        ollama_base_url = self.ollama_entry.get()

        # Define a coroutine a ser executada.
        coro = self._get_models_coro(provider_name, ollama_base_url)

        # Executa a coroutine em segundo plano e agenda o callback para atualizar a UI.
        run_async_task(coro, self.main_app.loop, self.main_app.async_queue, self._update_models_ui)

    # Coroutine que busca a lista de modelos de um provedor.
    @staticmethod
    async def _get_models_coro(provider_name, ollama_base_url=None):
        provider = None
        # Cria a instância apropriada do provedor com base no nome.
        if provider_name == "Ollama":
            provider = OllamaProvider(base_url=ollama_base_url)
        else:
            api_key = get_api_key(provider_name)
            if api_key:
                if provider_name == "OpenAI": provider = OpenAIProvider(api_key)
                elif provider_name == "Maritaca": provider = MaritacaProvider(api_key)
                elif provider_name == "OpenRouter": provider = OpenRouterProvider(api_key)
        # Se um provedor foi criado, chama seu método `list_models`; caso contrário, retorna uma lista vazia.
        return await provider.list_models() if provider else []

    # Callback que atualiza a UI com a lista de modelos recebida.
    def _update_models_ui(self, models):
        provider = self.provider_var.get().lower()
        if models:
            self.model_menu.configure(values=models)
            # Carrega o modelo salvo anteriormente para este provedor.
            saved_model = load_setting(f"{provider}_model", models[0])
            # Define o valor do menu para o modelo salvo, se ele ainda existir na lista.
            self.model_var.set(saved_model if saved_model in models else models[0])
        else:
            self.model_menu.configure(values=["(Falha na listagem)"]); self.model_var.set("(Falha na listagem)")
        # Para Ollama, também atualiza o campo de entrada manual.
        if provider == "ollama":
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, load_setting(f"{provider}_model", "llama3.1"))
        # Reabilita o botão de atualização.
        self.refresh_button.configure(state="normal")
