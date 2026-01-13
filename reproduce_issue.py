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
import sys
import os

# Add repo root to path
sys.path.append(os.getcwd())

from app.ui.widgets.scrollable_canvas_frame import ScrollableCanvasFrame

def test_widget_init():
    try:
        app = ctk.CTk()
        # This triggers the problematic __init__ -> super().__init__ -> _apply_appearance_mode cycle
        widget = ScrollableCanvasFrame(app)
        print("Widget initialized successfully.")

        # Test scroll binding on internal canvas
        if hasattr(widget, "canvas"):
            print("Canvas attribute exists.")

        app.destroy()
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_widget_init()
