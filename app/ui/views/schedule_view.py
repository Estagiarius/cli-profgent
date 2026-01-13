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
from tkinter import messagebox
from datetime import date, timedelta, datetime
from app.services import data_service
from app.ui.views.lesson_dialog import LessonDialog
from app.ui.views.add_dialog import AddDialog
from app.ui.views.base_dialog import BaseDialog

class ScheduleView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app

        # Estado
        self.current_week_start = self.get_start_of_current_week()
        self.days_map = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}

        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.title_label = ctk.CTkLabel(self.header_frame, text="Grade Horária", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left", padx=10)

        # Tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.tab_view.add("Visualização")
        self.tab_view.add("Configuração")

        # Configura as abas
        self.setup_visualization_tab()
        self.setup_configuration_tab()

    def get_start_of_current_week(self):
        today = date.today()
        # Monday = 0
        return today - timedelta(days=today.weekday())

    # --- ABA DE VISUALIZAÇÃO ---
    def setup_visualization_tab(self):
        tab = self.tab_view.tab("Visualização")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1) # Grid area

        # Controles de Navegação de Semana
        nav_frame = ctk.CTkFrame(tab)
        nav_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.prev_btn = ctk.CTkButton(nav_frame, text="< Semana Anterior", width=120, command=self.prev_week)
        self.prev_btn.pack(side="left", padx=10)

        self.week_label = ctk.CTkLabel(nav_frame, text="", font=ctk.CTkFont(weight="bold"))
        self.week_label.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(nav_frame, text="Próxima Semana >", width=120, command=self.next_week)
        self.next_btn.pack(side="right", padx=10)

        # Área do Grid
        self.grid_frame = ctk.CTkScrollableFrame(tab, orientation="horizontal") # Horizontal scroll se tiver muitos dias?
        # Na verdade precisamos de vertical scroll se tiver muitas aulas, e horizontal se a tela for pequena.
        # Vamos usar CTkScrollableFrame normal (vertical) e confiar no layout.
        self.grid_frame = ctk.CTkScrollableFrame(tab)
        self.grid_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.update_week_label()

    def update_week_label(self):
        end_week = self.current_week_start + timedelta(days=6)
        self.week_label.configure(text=f"Semana: {self.current_week_start.strftime('%d/%m')} a {end_week.strftime('%d/%m')}")
        self.render_grid()

    def prev_week(self):
        self.current_week_start -= timedelta(days=7)
        self.update_week_label()

    def next_week(self):
        self.current_week_start += timedelta(days=7)
        self.update_week_label()

    def render_grid(self):
        # Limpa grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Busca dados
        grid_data = data_service.get_full_schedule_grid()

        # Determina colunas (dias)
        # Vamos assumir Seg-Sex (0-4) fixo, ou dinâmico?
        # Melhor mostrar todos os dias que têm configuração.
        active_days = sorted(grid_data.keys())
        if not active_days:
            ctk.CTkLabel(self.grid_frame, text="Nenhum horário configurado. Vá para a aba 'Configuração'.").pack(pady=20)
            return

        # Headers (Dias)
        for col_idx, day_code in enumerate(active_days):
            day_name = self.days_map.get(day_code, "Dia")
            # Data específica desta semana
            current_day_date = self.current_week_start + timedelta(days=day_code)

            header_text = f"{day_name}\n{current_day_date.strftime('%d/%m')}"

            # Highlight se for hoje
            fg_color = "green" if current_day_date == date.today() else None

            lbl = ctk.CTkLabel(self.grid_frame, text=header_text, font=ctk.CTkFont(weight="bold"),
                               fg_color=fg_color, corner_radius=6, padx=10, pady=5)
            lbl.grid(row=0, column=col_idx, padx=5, pady=5, sticky="ew")
            self.grid_frame.grid_columnconfigure(col_idx, weight=1)

            # Slots do dia
            day_slots = grid_data[day_code]
            for slot_item in day_slots:
                row_idx = slot_item['period_index'] # Usa o índice configurado pelo usuário para a linha

                # Container do Slot
                slot_frame = ctk.CTkFrame(self.grid_frame, border_width=1, border_color="gray")
                slot_frame.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")

                # Horário
                time_text = f"{slot_item['start_time']} - {slot_item['end_time']}"
                ctk.CTkLabel(slot_frame, text=time_text, font=ctk.CTkFont(size=10)).pack(pady=(5,0))

                assignment = slot_item['assignment']

                if assignment:
                    # Slot Ocupado
                    cls_info = f"{assignment['class_name']}\n{assignment['course_name']}"
                    btn = ctk.CTkButton(slot_frame, text=cls_info,
                                        fg_color="transparent", border_width=1,
                                        command=lambda s=slot_item, d=current_day_date: self.on_slot_click(s, d))
                    btn.pack(padx=5, pady=5, fill="both", expand=True)

                    # Verifica se já tem aula registrada (indicador visual)
                    # Isso pode ser pesado (N queries). DataService tem get_lesson_for_schedule?
                    # Vamos fazer uma verificação rápida se possível.
                    # Mas por enquanto, deixa sem indicador visual de "concluído" para não complicar a performance.

                else:
                    # Slot Vazio (Alocar)
                    btn = ctk.CTkButton(slot_frame, text="+ Alocar", fg_color="transparent", text_color="gray",
                                        command=lambda s=slot_item: self.open_allocation_dialog(s))
                    btn.pack(padx=5, pady=5, fill="both", expand=True)


    def on_slot_click(self, slot_item, date_val):
        """Abre o diálogo de registro de aula."""
        assignment = slot_item['assignment']
        class_subject_id = assignment['class_subject_id']

        # Verifica se já existe aula
        existing_lesson = data_service.get_lesson_for_schedule(class_subject_id, date_val)

        dialog = LessonDialog(self, class_subject_id, date_val, lesson_data=existing_lesson, on_save=self.render_grid)
        # O on_save re-renderiza o grid, mas como não temos indicador visual, talvez não mude nada.
        # Mas é bom para garantir consistência.

    def open_allocation_dialog(self, slot_item):
        """Abre diálogo para vincular uma turma ao slot."""
        # Precisa selecionar Turma e depois Disciplina daquela turma?
        # Ou listar todas as disciplinas de todas as turmas?
        # Vamos listar "Turma - Disciplina"

        classes = data_service.get_all_classes()
        if not classes:
            messagebox.showwarning("Aviso", "Não há turmas cadastradas.")
            return

        # Prepara lista hierárquica para escolha
        # Opção 1: Dois dropdowns (Turma -> Disciplina)
        # Opção 2: Um dropdown (Turma : Disciplina)
        # Vamos usar opção 1 com AddDialog customizado? AddDialog é simples.
        # Melhor fazer um popup custom aqui rapidinho ou usar CTkInputDialog é pouco.

        self.show_allocation_popup(slot_item['slot_id'])

    def show_allocation_popup(self, slot_id):
        top = BaseDialog(self, "Alocar Turma")
        top.geometry("400x300")
        top.center_on_screen()

        ctk.CTkLabel(top, text="Selecione a Turma:").pack(pady=10)
        class_combo = ctk.CTkComboBox(top, values=[])
        class_combo.pack(pady=5)

        ctk.CTkLabel(top, text="Selecione a Disciplina:").pack(pady=10)
        subject_combo = ctk.CTkComboBox(top, values=[])
        subject_combo.pack(pady=5)

        # Dados
        classes = data_service.get_all_classes()
        class_map = {c['name']: c['id'] for c in classes}
        class_combo.configure(values=list(class_map.keys()))

        subject_map = {} # nome -> id

        def on_class_change(choice):
            class_id = class_map[choice]
            subjects = data_service.get_subjects_for_class(class_id)
            subject_names = [s['course_name'] for s in subjects]
            subject_map.clear()
            for s in subjects:
                subject_map[s['course_name']] = s['id']
            subject_combo.configure(values=subject_names)
            if subject_names: subject_combo.set(subject_names[0])
            else: subject_combo.set("Nenhuma disciplina")

        class_combo.configure(command=on_class_change)
        if classes:
            class_combo.set(classes[0]['name'])
            on_class_change(classes[0]['name'])

        def confirm():
            subj_name = subject_combo.get()
            if not subj_name or subj_name not in subject_map:
                messagebox.showerror("Erro", "Selecione uma disciplina válida.")
                return

            subj_id = subject_map[subj_name]
            data_service.create_schedule_assignment(slot_id, subj_id)
            top.destroy()
            self.render_grid()

        ctk.CTkButton(top, text="Confirmar", command=confirm).pack(pady=20)


    # --- ABA DE CONFIGURAÇÃO ---
    def setup_configuration_tab(self):
        tab = self.tab_view.tab("Configuração")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Lista de Dias
        self.config_scroll = ctk.CTkScrollableFrame(tab)
        self.config_scroll.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.refresh_config_list()

    def refresh_config_list(self):
        for w in self.config_scroll.winfo_children(): w.destroy()

        # Renderiza seções para Seg-Sex (e Sab?)
        for day_code in range(5): # 0-4 (Seg-Sex)
            self.render_day_config(day_code)

    def render_day_config(self, day_code):
        day_frame = ctk.CTkFrame(self.config_scroll)
        day_frame.pack(fill="x", padx=10, pady=5)

        header = ctk.CTkFrame(day_frame, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)

        day_name = self.days_map[day_code]
        ctk.CTkLabel(header, text=day_name, font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="+ Adicionar Aula", width=100,
                      command=lambda d=day_code: self.add_slot_popup(d)).pack(side="right")

        # Lista slots existentes
        slots = data_service.get_time_slots(day_code)
        if not slots:
            ctk.CTkLabel(day_frame, text="Nenhum horário configurado.", text_color="gray").pack(pady=5)

        for slot in slots:
            row = ctk.CTkFrame(day_frame, border_width=1)
            row.pack(fill="x", padx=10, pady=2)

            txt = f"{slot['period_index']}ª Aula: {slot['start_time']} - {slot['end_time']}"
            ctk.CTkLabel(row, text=txt).pack(side="left", padx=10)

            ctk.CTkButton(row, text="X", width=30, fg_color="red",
                          command=lambda sid=slot['id']: self.delete_slot(sid)).pack(side="right", padx=5, pady=2)

    def add_slot_popup(self, day_code):
        def save(data):
            try:
                idx = int(data['index'])
                start = data['start']
                end = data['end']
                data_service.create_time_slot(day_code, idx, start, end)
                self.refresh_config_list()
                self.render_grid() # Atualiza aba visualização tb
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar slot: {e}")

        AddDialog(self, f"Adicionar Horário - {self.days_map[day_code]}",
                  fields={"index": "Nº da Aula (ex: 1)", "start": "Início (HH:MM)", "end": "Fim (HH:MM)"},
                  save_callback=save)

    def delete_slot(self, slot_id):
        if messagebox.askyesno("Confirmar", "Deseja excluir este horário? A alocação será perdida."):
            data_service.delete_time_slot(slot_id)
            self.refresh_config_list()
            self.render_grid()

    def on_show(self):
        # Chamado quando a view aparece
        self.render_grid()
