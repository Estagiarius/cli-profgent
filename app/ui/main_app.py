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
# Importa a biblioteca 'asyncio' para gerenciar o loop de eventos assíncrono.
import asyncio
import platform
# Importa a biblioteca 'customtkinter' para criar os componentes da interface gráfica.
import customtkinter as ctk
# Importa 'Queue' para comunicação thread-safe e 'Empty' para exceções de fila vazia.
from queue import Queue, Empty
# Importa as classes de cada tela (view) da aplicação.
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.assistant_view import AssistantView
from app.ui.views.settings_view import SettingsView
from app.ui.views.management_view import ManagementView
from app.ui.views.class_selection_view import ClassSelectionView
from app.ui.views.class_detail_view import ClassDetailView
from app.ui.views.schedule_view import ScheduleView
from app.core.config import load_setting
from app.utils.path_utils import get_resource_path

# Importa as classes de serviço que contêm a lógica de negócios e da IA.
from app.services.data_service import DataService
from app.services.assistant_service import AssistantService

# Define a classe principal da aplicação, que herda de ctk.CTk (a janela principal).
class MainApp(ctk.CTk):
    """
    Classe principal que gerencia a interface gráfica da aplicação de Gestão Acadêmica.

    A classe MainApp é responsável por criar a janela principal da aplicação, configurar
    os layouts, gerenciar as telas (views) e possibilitar a comunicação assíncrona entre
    a interface do usuário e os serviços de backend.

    :ivar data_service: Serviço para manipulação e acesso aos dados.
                        Responsável por operações relacionadas a dados persistentes.
    :type data_service: DataService
    :ivar assistant_service: Serviço para funcionalidades de assistente inteligente
                             baseado em IA.
    :type assistant_service: AssistantService
    :ivar loop: Loop de eventos asyncio, utilizado para integrar tarefas assíncronas
                com o loop de eventos do tkinter.
    :type loop: asyncio.AbstractEventLoop
    :ivar async_queue: Fila thread-safe utilizada para a comunicação entre a interface
                       gráfica e tarefas assíncronas.
    :type async_queue: Queue
    :ivar _poll_id: ID do evento agendado para o loop de integração do tkinter e asyncio.
    :type _poll_id: int
    :ivar navigation_frame: Frame principal da navegação, localizado na lateral
                            esquerda da janela.
    :type navigation_frame: ctk.CTkFrame
    :ivar navigation_frame_label: Rótulo que exibe o título do painel de navegação.
    :type navigation_frame_label: ctk.CTkLabel
    :ivar dashboard_button: Botão de navegação para o dashboard.
    :type dashboard_button: ctk.CTkButton
    :ivar schedule_button: Botão de navegação para o horário escolar.
    :type schedule_button: ctk.CTkButton
    :ivar management_button: Botão de navegação para a gestão de dados.
    :type management_button: ctk.CTkButton
    :ivar class_selection_button: Botão de navegação para a seleção de turmas.
    :type class_selection_button: ctk.CTkButton
    :ivar assistant_button: Botão de navegação para o assistente IA.
    :type assistant_button: ctk.CTkButton
    :ivar settings_button: Botão de navegação para configurações.
    :type settings_button: ctk.CTkButton
    :ivar main_frame: Frame principal onde as diferentes telas (views) são exibidas.
    :type main_frame: ctk.CTkFrame
    :ivar views: Dicionário que mapeia os nomes das telas (views) às suas respectivas
                 instâncias.
    :type views: dict
    """
    # O método construtor, que recebe as instâncias dos serviços por injeção de dependência.
    def __init__(self, data_service: DataService, assistant_service: AssistantService):
        # Chama o construtor da classe pai (ctk.CTk).
        super().__init__()

        # Armazena as instâncias dos serviços como atributos da classe.
        self.data_service = data_service
        self.assistant_service = assistant_service

        # Define o título e o tamanho inicial da janela principal.
        ctk.set_appearance_mode("Dark")

        # Carrega o tema salvo ou usa o padrão "Black & Orange"
        # Usa get_resource_path para garantir que funcione no executável (PyInstaller)
        theme_relative_path = load_setting("app_theme_path", "app/ui/themes/black_orange.json")
        theme_path = get_resource_path(theme_relative_path)

        try:
            ctk.set_default_color_theme(theme_path)
        except FileNotFoundError:
            # Fallback seguro caso o arquivo de tema não exista mais
            print(f"AVISO: Tema não encontrado em {theme_path}. Usando tema padrão.")
            ctk.set_default_color_theme("blue")

        self.title("Profgent")
        self.geometry("1600x900")

        # Maximiza a janela de acordo com o sistema operacional
        if platform.system() == "Windows":
            self.state("zoomed")
        else:
            self.attributes("-zoomed", True)

        # Define uma função a ser chamada quando o usuário tenta fechar a janela.
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Obtém o loop de eventos asyncio, que será usado para tarefas em segundo plano.
        self.loop = asyncio.get_event_loop()

        # Cria uma fila thread-safe para comunicação entre a thread principal da UI e as threads de trabalho.
        self.async_queue = Queue()
        # Inicia o processo de verificação da fila.
        self._process_queue()

        # Define um ID inicial para o loop de polling do asyncio.
        # noinspection PyTypeChecker
        self._poll_id = None
        # Inicia o loop que integra o asyncio com o loop de eventos do tkinter.
        self.update_asyncio()

        # Configura o layout de grade da janela principal (1 linha, 2 colunas).
        self.grid_rowconfigure(0, weight=1)    # A linha 0 se expande verticalmente.
        self.grid_columnconfigure(1, weight=1) # A coluna 1 se expande horizontalmente.

        # Cria o frame (painel) de navegação à esquerda.
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew") # Posiciona o frame na grade.
        self.navigation_frame.grid_rowconfigure(8, weight=1) # Linha 8 do frame se expande para empurrar os botões para cima.
        self.navigation_frame.grid_columnconfigure(0, weight=1)

        # Adiciona um rótulo de título ao painel de navegação.
        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Navegação",
                                                  font=ctk.CTkFont(size=20, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Adiciona os botões de navegação. Cada botão chama o método `show_view` com o nome da tela correspondente.
        self.dashboard_button = ctk.CTkButton(self.navigation_frame, text="Dashboard", command=lambda: self.show_view("dashboard"))
        self.dashboard_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.class_selection_button = ctk.CTkButton(self.navigation_frame, text="Minhas Turmas", command=lambda: self.show_view("class_selection"))
        self.class_selection_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.schedule_button = ctk.CTkButton(self.navigation_frame, text="Horário", command=lambda: self.show_view("schedule"))
        self.schedule_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.assistant_button = ctk.CTkButton(self.navigation_frame, text="Assistente IA", command=lambda: self.show_view("assistant"))
        self.assistant_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.management_button = ctk.CTkButton(self.navigation_frame, text="Gestão de Dados", command=lambda: self.show_view("management"))
        self.management_button.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.settings_button = ctk.CTkButton(self.navigation_frame, text="Configurações", command=lambda: self.show_view("settings"))
        self.settings_button.grid(row=6, column=0, padx=20, pady=10, sticky="ew")


        # Cria o frame principal onde o conteúdo de cada tela será exibido.
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20) # Posiciona à direita do menu.
        self.main_frame.grid_rowconfigure(0, weight=1) # Permite que o conteúdo se expanda.
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Factories para criar as views sob demanda (Lazy Loading).
        # Isso otimiza o tempo de inicialização, criando os widgets pesados apenas quando necessário.
        self.view_factories = {
            "dashboard": lambda: DashboardView(self.main_frame, self),
            "schedule": lambda: ScheduleView(self.main_frame, self),
            "management": lambda: ManagementView(self.main_frame, self),
            "class_selection": lambda: ClassSelectionView(self.main_frame, self),
            "class_detail": lambda: ClassDetailView(self.main_frame, self),
            "assistant": lambda: AssistantView(self.main_frame, self, assistant_service=self.assistant_service),
            "settings": lambda: SettingsView(self.main_frame, self)
        }

        # Dicionário para armazenar as instâncias das views já criadas.
        self.views = {}

        # Exibe a tela de dashboard por padrão ao iniciar a aplicação.
        self.show_view("dashboard")

    # Método para processar a fila de tarefas assíncronas de forma contínua.
    def _process_queue(self):
        try:
            # Tenta obter uma tarefa da fila sem bloquear a execução.
            callback, args = self.async_queue.get_nowait()
            # Se uma tarefa for encontrada, executa a função (callback) com seus argumentos.
            callback(*args)
        except Empty:
            # Se a fila estiver vazia, não faz nada.
            pass
        finally:
            # Agenda a próxima verificação da fila para daqui a 100 milissegundos.
            # noinspection PyTypeHints
            self.after(100, self._process_queue)

    # Método para alternar entre as diferentes telas da aplicação.
    def show_view(self, view_name, **kwargs):
        # Instancia a view se ela ainda não existir (Lazy Loading)
        if view_name not in self.views and view_name in self.view_factories:
            # Cria a instância usando a factory e armazena no cache
            self.views[view_name] = self.view_factories[view_name]()

        # Esconde todas as telas para garantir que apenas uma esteja visível.
        for view in self.views.values():
            view.grid_forget()

        # Obtém a tela solicitada do dicionário.
        selected_view = self.views.get(view_name)

        if not selected_view:
            return

        # Exibe a tela selecionada na grade do frame principal.
        selected_view.grid(row=0, column=0, sticky="nsew")

        # Se a tela tiver um método 'on_show', chama-o. Isso permite que a tela atualize
        # seus dados sempre que for exibida. `**kwargs` passa argumentos extras.
        if hasattr(selected_view, 'on_show'):
            selected_view.on_show(**kwargs)

    # Método que integra o loop de eventos do asyncio com o do tkinter.
    def update_asyncio(self):
        # Força o loop do asyncio a executar as tarefas pendentes e depois parar.
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        # Agenda a próxima chamada a este método, criando um loop de polling.
        self._poll_id = self.after(20, self.update_asyncio)

    # Método chamado quando o usuário fecha a janela.
    def on_closing(self):
        # O loop de polling do asyncio (`update_asyncio`) deve continuar rodando
        # para permitir que a tarefa de limpeza seja executada.
        # Ele só será cancelado após a conclusão da limpeza.

        # Define e agenda a tarefa final de limpeza assíncrona.
        async def cleanup():
            # Fecha a conexão do serviço do assistente, se ele foi inicializado.
            if self.assistant_service and self.assistant_service.provider:
                await self.assistant_service.close()

            # Cancela quaisquer outras tarefas pendentes do asyncio.
            tasks = [t for t in asyncio.all_tasks(loop=self.loop) if t is not asyncio.current_task()]
            for task in tasks:
                task.cancel()

            # Aguarda a conclusão das tarefas canceladas, se houver.
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        # Inicia a tarefa de limpeza no loop de eventos do asyncio.
        cleanup_task = self.loop.create_task(cleanup())

        # Inicia um polling não bloqueante para verificar a conclusão da limpeza.
        self._check_cleanup_done(cleanup_task)

    # Método que verifica periodicamente se a tarefa de limpeza terminou.
    def _check_cleanup_done(self, task):
        # Se a tarefa de limpeza estiver concluída, é seguro parar o polling e destruir a janela.
        if task.done():
            # Cancela o loop de polling do asyncio.
            if hasattr(self, '_poll_id'):
                self.after_cancel(self._poll_id)

            # Agora, destrói a janela principal de forma segura.
            self.destroy()
        # Se a tarefa ainda não terminou, agenda uma nova verificação para daqui a 50ms.
        else:
            self.after(50, self._check_cleanup_done, task)
