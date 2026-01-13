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
# Importa a função utilitária para executar tarefas assíncronas sem bloquear a UI.
from app.utils.async_utils import run_async_task

# Define a classe AssistantView, que herda de CTkFrame para ser um painel dentro da janela principal.
class AssistantView(ctk.CTkFrame):
    # O método construtor.
    def __init__(self, parent, main_app, assistant_service):
        # Chama o construtor da classe pai.
        super().__init__(parent)
        # Armazena a instância do serviço do assistente, que contém a lógica da IA.
        self.assistant_service = assistant_service
        # Armazena a instância da aplicação principal para acessar o loop asyncio e a fila.
        self.main_app = main_app

        # Configura o layout de grade da view para que a caixa de chat se expanda.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Cria a caixa de texto para exibir o histórico do chat.
        # 'state="disabled"' impede que o usuário digite diretamente no histórico.
        # 'wrap="word"' quebra as linhas por palavra.
        self.chat_history = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.chat_history.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Cria um frame para agrupar o campo de entrada e o botão de enviar.
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        # Configura a coluna 0 do frame de entrada para se expandir com a janela.
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Cria o campo de entrada para o usuário digitar a mensagem.
        self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Pergunte qualquer coisa ao assistente...")
        self.user_input.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        # Associa a tecla <Return> (Enter) à função de enviar mensagem.
        self.user_input.bind("<Return>", lambda event: self.send_message())

        # Cria o botão "Enviar".
        self.send_button = ctk.CTkButton(self.input_frame, text="Enviar", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Adiciona uma mensagem inicial de boas-vindas ao chat.
        self.add_message("Sistema", "Bem-vindo! Como posso ajudar você hoje?")

    # Método chamado quando o usuário clica em "Enviar" ou pressiona Enter.
    def send_message(self):
        # Obtém o texto do campo de entrada.
        user_text = self.user_input.get()
        # Se o texto estiver vazio ou contiver apenas espaços, não faz nada.
        if not user_text.strip(): return

        # Adiciona a mensagem do usuário ao histórico do chat.
        self.add_message("Você", user_text)
        # Limpa o campo de entrada.
        self.user_input.delete(0, "end")

        # Desabilita os controles de entrada enquanto o assistente está "pensando".
        self.user_input.configure(state="disabled")
        self.send_button.configure(state="disabled")
        # Adiciona uma mensagem temporária de "Pensando...".
        self.add_message("Assistente", "Pensando...")

        # Usa a função utilitária para executar a tarefa assíncrona de obter a resposta da IA.
        # `coro` é a coroutine (a função async a ser executada).
        coro = self.assistant_service.get_response(user_text)
        # `run_async_task` executa a coroutine em segundo plano e, quando termina,
        # coloca o resultado e o callback na fila da UI principal.
        # O lambda define o callback que será executado na thread principal.
        run_async_task(coro, self.main_app.loop, self.main_app.async_queue, lambda result: self.main_app.after(0, self.update_ui_with_response, result))

    # Método de callback que atualiza a UI com a resposta final do assistente.
    def update_ui_with_response(self, response):
        """Atualiza o histórico do chat com a resposta final do assistente."""
        # Habilita a caixa de texto para poder modificá-la.
        self.chat_history.configure(state="normal")
        # Obtém todo o texto atual do histórico.
        current_text = self.chat_history.get("1.0", "end-1c")
        # Divide o texto em blocos de mensagens.
        lines = current_text.strip().split('\n\n')
        # Verifica se a última mensagem é a de "Pensando...".
        if lines and lines[-1].startswith("Assistente: Pensando..."):
            # Remove a última mensagem (o "Pensando...").
            new_text = "\n\n".join(lines[:-1])
            # Limpa toda a caixa de texto.
            self.chat_history.delete("1.0", "end")
            # Reinsere o texto sem a mensagem de "Pensando...".
            if new_text: self.chat_history.insert("1.0", new_text + "\n\n")

        # Verifica se ocorreu um erro durante a execução da tarefa assíncrona.
        if isinstance(response, Exception):
            self.add_message("Sistema", f"Ocorreu um erro: {response}")
        # Adiciona a resposta real do assistente.
        elif response.content:
            self.add_message("Assistente", response.content)
        # Se não houver conteúdo textual (ex: a IA apenas executou uma ação), adiciona uma mensagem do sistema.
        else:
            self.add_message("Sistema", "Uma ação foi realizada, mas nenhuma resposta verbal foi gerada.")

        # Desabilita a caixa de texto novamente.
        self.chat_history.configure(state="disabled")
        # Reabilita os controles de entrada para o usuário.
        self.user_input.configure(state="normal")
        self.send_button.configure(state="normal")

    # Método auxiliar para adicionar uma mensagem formatada ao histórico do chat.
    def add_message(self, sender: str, message: str):
        # Habilita a edição da caixa de texto.
        self.chat_history.configure(state="normal")
        # Insere o texto formatado no final.
        self.chat_history.insert("end", f"{sender}: {message}\n\n")
        # Desabilita a edição novamente.
        self.chat_history.configure(state="disabled")
        # Rola a caixa de texto para mostrar a mensagem mais recente.
        self.chat_history.see("end")
