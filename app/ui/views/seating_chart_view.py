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
from tkinter import messagebox, Menu, filedialog
import json
from app.ui.widgets.scrollable_canvas_frame import ScrollableCanvasFrame
from app.services import data_service
from app.ui.views.add_dialog import AddDialog
from app.services.report_service import ReportService
import os

class SeatingChartView(ctk.CTkFrame):
    def __init__(self, parent, class_id):
        super().__init__(parent)
        self.class_id = class_id
        self.report_service = ReportService()

        self.current_chart_id = None
        self.chart_data = None # Holds current chart details {rows, cols, layout_config, assignments}

        self.selected_student_id = None # From the sidebar list
        self.selected_cell = None # (row, col)

        # Main Layout: Sidebar (Left) + Grid (Right)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Student list expands (Row 4)

        # Layout Selector
        ctk.CTkLabel(self.sidebar_frame, text="Layouts Salvos:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.layout_combo = ctk.CTkOptionMenu(self.sidebar_frame, command=self.on_layout_change)
        self.layout_combo.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Layout Actions
        self.layout_actions_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.layout_actions_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(self.layout_actions_frame, text="+ Novo", width=80, command=self.add_layout_popup).pack(side="left", padx=(0, 5))
        ctk.CTkButton(self.layout_actions_frame, text="Excluir", width=80, fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_layout).pack(side="left")

        # Student List
        ctk.CTkLabel(self.sidebar_frame, text="Alunos (Clique para selecionar):", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=10, pady=(20, 5), sticky="nw")

        self.student_list_frame = ctk.CTkScrollableFrame(self.sidebar_frame)
        self.student_list_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

        # Export Button
        ctk.CTkButton(self.sidebar_frame, text="Exportar PDF/Vetor", command=self.export_chart).grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        # --- Grid Area ---
        self.grid_container = ctk.CTkFrame(self)
        self.grid_container.grid(row=0, column=1, sticky="nsew")
        self.grid_container.grid_rowconfigure(1, weight=1)
        self.grid_container.grid_columnconfigure(0, weight=1)

        # Header with Legend
        self.legend_frame = ctk.CTkFrame(self.grid_container, height=40)
        self.legend_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self._create_legend_item("Clique com o botão direito sobre a grade para abrir o menu e selecionar entre:", "transparent", "white")
        self._create_legend_item("Carteira", "white", "black")
        self._create_legend_item("Mesa Prof.", "#D3D3D3", "black")
        self._create_legend_item("Porta", "#8B4513", "white")
        self._create_legend_item("Vazio", "transparent", "white") # Logic visualization only
 # Logic visualization only

        # Canvas for Drawing
        self.canvas_frame = ScrollableCanvasFrame(self.grid_container)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=50, pady=50)

        # Bind events on canvas
        self.canvas = self.canvas_frame.canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click) # Right click for context menu

        # Initial Load
        self.populate_layout_combo()

    def _create_legend_item(self, text, bg_color, text_color):
        f = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
        f.pack(side="left", padx=10, pady=5)

        box = ctk.CTkLabel(f, text="", width=20, height=20, fg_color=bg_color)
        box.pack(side="left", padx=5)
        ctk.CTkLabel(f, text=text).pack(side="left")

    def populate_layout_combo(self):
        charts = data_service.get_seating_charts_for_class(self.class_id)
        if not charts:
            self.layout_combo.configure(values=["Nenhum Layout"])
            self.layout_combo.set("Nenhum Layout")
            self.layout_combo.configure(state="disabled")
            self.current_chart_id = None
            self.chart_data = None
            self.canvas.delete("all")
        else:
            self.layout_combo.configure(state="normal")
            names = [c['name'] for c in charts]
            self.layout_map = {c['name']: c['id'] for c in charts}
            self.layout_combo.configure(values=names)

            # Select first if none selected
            if not self.current_chart_id:
                first_name = names[0]
                self.layout_combo.set(first_name)
                self.on_layout_change(first_name)

    def on_layout_change(self, layout_name):
        if layout_name in self.layout_map:
            self.current_chart_id = self.layout_map[layout_name]
            self.load_chart_data()

    def load_chart_data(self):
        if not self.current_chart_id: return
        self.chart_data = data_service.get_seating_chart_details(self.current_chart_id)

        # Parse layout_config JSON
        try:
            self.chart_data['layout_config_parsed'] = json.loads(self.chart_data.get('layout_config', '{}'))
        except json.JSONDecodeError:
            self.chart_data['layout_config_parsed'] = {}

        # Parse Assignments into a map (r,c) -> student_data
        self.chart_data['assignments_map'] = {}
        for a in self.chart_data['assignments']:
            self.chart_data['assignments_map'][(a['row_index'], a['col_index'])] = a

        self.draw_grid()
        self.populate_student_list()

    def populate_student_list(self):
        # Clear list
        for widget in self.student_list_frame.winfo_children(): widget.destroy()

        # Get all active students
        all_students = data_service.get_enrollments_for_class(self.class_id)
        active_students = [s for s in all_students if s['status'] == 'Active']

        # Filter out already assigned students
        assigned_ids = {a['student_id'] for a in self.chart_data['assignments']}
        unassigned = [s for s in active_students if s['student_id'] not in assigned_ids]

        for s in unassigned:
            call_num = s['call_number'] if s['call_number'] is not None else "?"
            btn = ctk.CTkButton(
                self.student_list_frame,
                text=f"{call_num} - {s['student_first_name']} {s['student_last_name']}",
                fg_color="transparent",
                border_width=1,
                border_color="#555",
                text_color=("black", "white"),
                hover_color=("#AAA", "#444"),
                anchor="w",
                command=lambda sid=s['student_id']: self.select_student(sid)
            )
            btn.pack(fill="x", padx=5, pady=2)

    def select_student(self, student_id):
        self.selected_student_id = student_id
        # Visual feedback: Change cursor for the whole app window (a bit hacky but effective for Tkinter)
        self.configure(cursor="hand2")

    def add_layout_popup(self):
        def save_callback(data):
            name = data['name']
            rows_str = data['rows']
            cols_str = data['cols']

            try:
                rows = int(rows_str)
                cols = int(cols_str)
                if rows <= 0 or cols <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Linhas e Colunas devem ser números positivos.")
                return

            data_service.create_seating_chart(self.class_id, name, rows, cols)
            self.populate_layout_combo()
            self.layout_combo.set(name)
            self.on_layout_change(name)

        fields = {"name": "Nome do Layout", "rows": "Linhas", "cols": "Colunas"}
        AddDialog(self, "Novo Mapa de Sala", fields=fields, save_callback=save_callback)

    def delete_layout(self):
        if not self.current_chart_id: return
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este layout?"):
            return

        data_service.delete_seating_chart(self.current_chart_id)
        self.current_chart_id = None
        self.populate_layout_combo()

    # --- Drawing Logic ---
    CELL_WIDTH = 140
    CELL_HEIGHT = 80
    PADDING = 20

    def draw_grid(self):
        self.canvas.delete("all")
        if not self.chart_data: return

        rows = self.chart_data['rows']
        cols = self.chart_data['columns']
        layout_config = self.chart_data['layout_config_parsed']
        assignments = self.chart_data['assignments_map']

        # Calculate canvas size
        width = cols * self.CELL_WIDTH + (self.PADDING * 2)
        height = rows * self.CELL_HEIGHT + (self.PADDING * 2)

        # Configure scroll region
        self.canvas_frame.canvas.configure(scrollregion=(0, 0, width, height))

        for r in range(rows):
            for c in range(cols):
                x1 = self.PADDING + (c * self.CELL_WIDTH)
                y1 = self.PADDING + (r * self.CELL_HEIGHT)
                x2 = x1 + self.CELL_WIDTH
                y2 = y1 + self.CELL_HEIGHT

                cell_key = f"{r},{c}"
                cell_type = layout_config.get(cell_key, "student_seat")

                # Draw based on type
                if cell_type == "void":
                    # Draw nothing or faint outline
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="#333", dash=(2, 4))

                elif cell_type == "door":
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#8B4513", outline="black")
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="Porta", fill="white", font=("Arial", 12, "bold"))

                elif cell_type == "teacher_desk":
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#D3D3D3", outline="black")
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="Mesa\nProf.", justify="center", font=("Arial", 11))

                elif cell_type == "student_seat":
                    # Draw Seat
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")

                    # Check assignment
                    assignment = assignments.get((r, c))
                    if assignment:
                        name = assignment['student_name']
                        call_num = assignment.get('call_number')
                        call_str = f"{call_num}" if call_num is not None else "?"

                        # Display: Call Number (top left)
                        self.canvas.create_text(x1+8, y1+8, text=call_str, anchor="nw", fill="blue", font=("Arial", 10, "bold"))

                        # Name: Try to display more complete name
                        # Split name and take up to 2 parts, join with newline if needed
                        parts = name.split()
                        if len(parts) >= 2:
                            display_name = f"{parts[0]}\n{parts[-1]}"
                        else:
                            display_name = name

                        self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=display_name, justify="center", fill="black", font=("Arial", 12), width=self.CELL_WIDTH-10)
                    else:
                        self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="Vazio", fill="#AAA", font=("Arial", 10))

    def on_canvas_click(self, event):
        if not self.chart_data: return

        # Translate canvas coordinates accounting for scroll
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)

        # Determine Cell
        col = int((cx - self.PADDING) // self.CELL_WIDTH)
        row = int((cy - self.PADDING) // self.CELL_HEIGHT)

        if 0 <= row < self.chart_data['rows'] and 0 <= col < self.chart_data['columns']:
            self.handle_cell_click(row, col)

    def handle_cell_click(self, row, col):
        cell_key = f"{row},{col}"
        cell_type = self.chart_data['layout_config_parsed'].get(cell_key, "student_seat")

        if cell_type != "student_seat":
            return # Ignore clicks on doors/teacher desks for assignment

        # Check if occupied
        assignments_map = self.chart_data['assignments_map']
        current_assignment = assignments_map.get((row, col))

        if current_assignment:
            # Clicked on occupied seat -> Unassign
            # Remove from list
            new_assignments = [a for a in self.chart_data['assignments']
                               if not (a['row_index'] == row and a['col_index'] == col)]

            # Save
            # Convert full dicts back to simple list for service
            save_list = [{'student_id': a['student_id'], 'row_index': a['row_index'], 'col_index': a['col_index']}
                         for a in new_assignments]

            data_service.save_seat_assignments(self.current_chart_id, save_list)
            self.load_chart_data() # Refresh

        elif self.selected_student_id:
            # Clicked on empty seat -> Assign selected student
            # Create new assignment object
            new_assign = {
                'student_id': self.selected_student_id,
                'row_index': row,
                'col_index': col
            }

            # Prepare full list
            current_assignments = [
                {'student_id': a['student_id'], 'row_index': a['row_index'], 'col_index': a['col_index']}
                for a in self.chart_data['assignments']
            ]
            current_assignments.append(new_assign)

            data_service.save_seat_assignments(self.current_chart_id, current_assignments)

            self.selected_student_id = None # Reset selection
            self.load_chart_data()

    def on_canvas_right_click(self, event):
        if not self.chart_data: return

        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        col = int((cx - self.PADDING) // self.CELL_WIDTH)
        row = int((cy - self.PADDING) // self.CELL_HEIGHT)

        if 0 <= row < self.chart_data['rows'] and 0 <= col < self.chart_data['columns']:
            # Show Context Menu
            menu = Menu(self, tearoff=0)
            menu.add_command(label="Carteira (Aluno)", command=lambda: self.set_cell_type(row, col, "student_seat"))
            menu.add_command(label="Mesa Professor", command=lambda: self.set_cell_type(row, col, "teacher_desk"))
            menu.add_command(label="Porta", command=lambda: self.set_cell_type(row, col, "door"))
            menu.add_command(label="Vazio / Corredor", command=lambda: self.set_cell_type(row, col, "void"))
            menu.tk_popup(event.x_root, event.y_root)

    def set_cell_type(self, row, col, new_type):
        key = f"{row},{col}"
        config = self.chart_data['layout_config_parsed']

        if new_type == "student_seat":
            if key in config:
                del config[key] # Default is student_seat
        else:
            config[key] = new_type

        # Update DB
        data_service.update_seating_chart_layout(self.current_chart_id, json.dumps(config))
        self.load_chart_data()

    def export_chart(self):
        if not self.current_chart_id: return

        # Ask user for format
        filepath = filedialog.asksaveasfilename(
            title="Exportar Mapa de Sala",
            defaultextension=".pdf",
            filetypes=[("PDF Document", "*.pdf"), ("Scalable Vector Graphics", "*.svg")],
            initialfile=f"mapa_sala_{self.current_chart_id}"
        )

        if not filepath: return

        # Determine format from extension
        _, ext = os.path.splitext(filepath)
        fmt = ext.lower().replace('.', '')
        if fmt not in ['pdf', 'svg']:
            fmt = 'pdf' # Default

        try:
            # We need to expose a method in report_service that accepts a path or returns content,
            # currently it generates its own path.
            # Ideally report service should allow overriding path.
            # But since report_service methods return a path inside 'reports/', let's just generate it there
            # and then move/copy it, or assume the user wants it in the reports folder if they didn't pick location?
            # Actually, standard flow in this app seems to be auto-gen in reports/ folder.
            # But since we are asking for a save location now (standard for "Export"), we should respect it.
            # However, ReportService currently hardcodes path.

            # Let's call the internal generator directly or update ReportService?
            # Updating ReportService is cleaner but might touch more files.
            # Let's just generate it using the existing method which returns a path, then rename/move it to user selection.

            generated_path = self.report_service._generate_seating_chart_plot(self.current_chart_id, fmt)

            # Move to selected path
            import shutil
            shutil.move(generated_path, filepath)

            messagebox.showinfo("Sucesso", f"Mapa exportado com sucesso para:\n{filepath}")

            # Open file
            if os.name == 'nt':
                os.startfile(filepath)
            else:
                os.system(f'xdg-open "{filepath}"')

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar: {e}")
