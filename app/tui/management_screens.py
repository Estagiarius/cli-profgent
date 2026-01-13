from textual.app import ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, Button
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.binding import Binding

class StudentListScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Voltar"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("Lista de Alunos", classes="header-text"),
            DataTable(id="students_table"),
            Button("Atualizar", id="refresh_btn"),
            id="students_container"
        )
        yield Footer()

    def on_mount(self):
        self.load_students()

    def load_students(self):
        table = self.query_one("#students_table", DataTable)
        table.clear()
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Add columns
        table.add_columns("ID", "Nome", "Turma Atual")

        # Fetch data
        students = self.app.data_service.list_students()

        for student in students:
            # We need to find the current class for the student (optimization: query join in future)
            # For now, simplistic approach
            enrollments = self.app.data_service.get_student_enrollments(student['id'])
            active_class = "N/A"
            if enrollments:
                 # Get latest or active
                 active_class = enrollments[0]['class_name']

            table.add_row(str(student['id']), f"{student['first_name']} {student['last_name']}", active_class)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "refresh_btn":
            self.load_students()

class ClassListScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Voltar"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("Lista de Turmas", classes="header-text"),
            DataTable(id="classes_table"),
            Button("Atualizar", id="refresh_btn"),
            id="classes_container"
        )
        yield Footer()

    def on_mount(self):
        self.load_classes()

    def load_classes(self):
        table = self.query_one("#classes_table", DataTable)
        table.clear()
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_columns("ID", "Nome")

        classes = self.app.data_service.list_classes()
        for cls in classes:
            table.add_row(str(cls['id']), cls['name'])

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "refresh_btn":
            self.load_classes()
