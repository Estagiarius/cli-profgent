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
import tkinter as tk
from customtkinter import ThemeManager

class ScrollableCanvasFrame(ctk.CTkFrame):
    """
    A custom widget that provides a 2D scrollable area (vertical and horizontal).
    It uses a tkinter Canvas and CustomTkinter scrollbars.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Configure grid layout for the container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create the canvas
        # Use standard Canvas but style it to match CTk background
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Vertical Scrollbar
        self.v_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        # Horizontal Scrollbar
        self.h_scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure canvas to use scrollbars
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Create the inner frame that will hold the content
        self.scrollable_frame = ctk.CTkFrame(self.canvas, corner_radius=0)
        # Create window inside canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Bind events to update scroll region
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Initial background color setup to match CTk theme
        # We need to call this manually to apply the initial theme to the canvas
        self._apply_appearance_mode(ctk.get_appearance_mode())

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        """Resize the inner frame to match canvas width if desired (optional)"""
        # For 2D scrolling, we typically DON'T want to force width.
        # But if the content is smaller than canvas, we might want it to fill?
        # For a grid that extends horizontally, we leave it alone.
        pass

    def _apply_appearance_mode(self, mode_string):
        # Call super implementation and capture the return value (color string)
        color = super()._apply_appearance_mode(mode_string)

        # Guard against early call from super().__init__ before self.canvas exists
        if hasattr(self, "canvas"):
            # Attempt to match canvas background to the frame's background
            try:
                # CTk themes store colors as tuples (light, dark) or single strings
                fg_color = ThemeManager.theme["CTkFrame"]["fg_color"]

                if isinstance(fg_color, (list, tuple)):
                    bg_color = fg_color[1] if mode_string.lower() == "dark" else fg_color[0]
                else:
                    bg_color = fg_color

                self.canvas.configure(bg=bg_color)
            except Exception:
                # Fallback if theme structure is unexpected
                 if mode_string.lower() == "dark":
                    self.canvas.configure(bg="#2b2b2b")
                 else:
                    self.canvas.configure(bg="#f0f0f0")

        return color

    def bind_mouse_wheel(self, widget):
        """Recursively bind mouse wheel events to a widget and its children."""
        # Linux
        widget.bind("<Button-4>", self._on_mouse_wheel, add="+")
        widget.bind("<Button-5>", self._on_mouse_wheel, add="+")
        # Windows/Mac
        widget.bind("<MouseWheel>", self._on_mouse_wheel, add="+")

        for child in widget.winfo_children():
            self.bind_mouse_wheel(child)

    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling"""
        # Linux (Button-4/5)
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        # Windows/Mac (MouseWheel)
        else:
            # Typical delta is 120. -1*(event.delta/120) * speed
            delta = int(-1 * (event.delta / 120))
            self.canvas.yview_scroll(delta, "units")

        return "break"
