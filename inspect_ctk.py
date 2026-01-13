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

def check_ctk_internals():
    try:
        app = ctk.CTk()

        # Check CTkScrollableFrame internals
        sf = ctk.CTkScrollableFrame(app)
        print(f"CTkScrollableFrame dir: {dir(sf)}")

        if hasattr(sf, "_parent_canvas"):
            print("CTkScrollableFrame has _parent_canvas")
        elif hasattr(sf, "_canvas"):
            print("CTkScrollableFrame has _canvas")
        else:
            print("CTkScrollableFrame canvas attribute NOT FOUND")

        # Check _apply_appearance_mode return value
        frame = ctk.CTkFrame(app)
        ret = frame._apply_appearance_mode("Dark")
        print(f"CTkFrame._apply_appearance_mode return value: {ret}")

        app.destroy()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_ctk_internals()
