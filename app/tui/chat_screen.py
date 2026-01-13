from textual.app import ComposeResult
from textual.widgets import Header, Footer, Input, Static, Button, ListView, ListItem, Label
from textual.containers import Container, Vertical, HorizontalScroll
from textual.screen import Screen
from textual.message import Message
from textual import on
import asyncio

class ChatMessage(ListItem):
    def __init__(self, role: str, content: str):
        super().__init__()
        self.role = role
        self.content_text = content

    def compose(self) -> ComposeResult:
        role_color = "green" if self.role == "user" else "blue"
        role_label = "Você" if self.role == "user" else "Assistente"

        yield Label(f"[{role_color}]{role_label}:[/{role_color}]", classes="role_label")
        yield Label(self.content_text, classes="message_content")

class ChatScreen(Screen):
    CSS = """
    ChatMessage {
        height: auto;
        margin-bottom: 1;
        padding: 1;
        background: $surface;
    }
    .role_label {
        text-style: bold;
    }
    #chat_history {
        height: 1fr;
        border: solid $primary;
        overflow-y: auto;
    }
    #input_area {
        height: auto;
        dock: bottom;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            ListView(id="chat_history"),
            id="chat_container"
        )
        yield Container(
            Input(placeholder="Digite sua mensagem...", id="chat_input"),
            Button("Enviar", id="send_btn", variant="primary"),
            id="input_area"
        )
        yield Footer()

    def on_mount(self):
        # Initial greeting
        self.add_message("assistant", "Olá! Como posso ajudar na gestão acadêmica hoje?")

    def add_message(self, role: str, content: str):
        history = self.query_one("#chat_history", ListView)
        history.append(ChatMessage(role, content))
        # Scroll to bottom
        history.scroll_end(animate=False)

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send_btn":
            await self.process_input()

    @on(Input.Submitted, "#chat_input")
    async def on_input_submitted(self):
        await self.process_input()

    async def process_input(self):
        input_widget = self.query_one("#chat_input", Input)
        user_text = input_widget.value.strip()

        if not user_text:
            return

        self.add_message("user", user_text)
        input_widget.value = ""

        # Show loading indicator (simple version)
        self.title = "ProfGent - Processando..."

        # Call assistant service
        # Note: We access the app's assistant service instance
        response = await self.app.assistant_service.get_response(user_text)

        self.title = "ProfGent"

        if response and response.content:
            self.add_message("assistant", response.content)
        else:
            self.add_message("assistant", "(Sem resposta textual, verifique os logs ou ferramentas executadas.)")
