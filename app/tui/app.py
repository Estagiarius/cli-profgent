from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Label
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import TabbedContent, TabPane
import plotext as plt
from rich.text import Text

# Import services
from app.services import data_service
from app.services.assistant_service import AssistantService
from app.tui.chat_screen import ChatScreen
from app.tui.management_screens import StudentListScreen, ClassListScreen

class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Bem-vindo ao ProfGent TUI", id="welcome_msg", classes="header-text"),
            Static("Carregando estatísticas...", id="stats_panel"),
            id="dashboard_container"
        )
        yield Footer()

    def on_mount(self):
        self.load_stats()

    def load_stats(self):
        # Placeholder for stats loading
        stats_panel = self.query_one("#stats_panel", Static)

        # Example of Plotext integration (simple text for now)
        try:
            plt.clear_figure()
            plt.theme('dark')
            plt.simple_bar(["Turma A", "Turma B"], [8.5, 7.2], width=60, title="Médias Recentes")
            chart = plt.build()
            stats_panel.update(Text.from_ansi(chart))
        except Exception as e:
            stats_panel.update(f"Erro ao gerar gráfico: {e}")

class TuiApp(App):
    CSS = """
    #dashboard_container {
        padding: 1;
        align: center middle;
    }
    .header-text {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Sair"),
        ("d", "switch_dashboard", "Dashboard"),
        ("c", "switch_chat", "IA Chat"),
        ("s", "switch_students", "Alunos"),
        ("t", "switch_classes", "Turmas"),
    ]

    def __init__(self, data_service, assistant_service):
        super().__init__()
        self.data_service = data_service
        self.assistant_service = assistant_service

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())

    def action_switch_dashboard(self):
        self.push_screen(DashboardScreen())

    def action_switch_chat(self):
        self.push_screen(ChatScreen())

    def action_switch_students(self):
        self.push_screen(StudentListScreen())

    def action_switch_classes(self):
        self.push_screen(ClassListScreen())

if __name__ == "__main__":
    # For testing isolation
    app = TuiApp(data_service=data_service, assistant_service=AssistantService())
    app.run()
