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
import sys
import os
import subprocess
import platform
from pathlib import Path

def open_file_in_os(filepath: str):
    """
    Abre um arquivo ou diretório usando o aplicativo padrão do sistema operacional.
    Compatível com Windows, MacOS e Linux.

    :param filepath: Caminho absoluto do arquivo a ser aberto.
    """
    if platform.system() == 'Windows':
        os.startfile(filepath)
    elif platform.system() == 'Darwin':  # MacOS
        subprocess.Popen(['open', filepath])
    else:  # Linux e outros Unix-like
        subprocess.Popen(['xdg-open', filepath])

def get_resource_path(relative_path: str | Path) -> str:
    """
    Resolve o caminho absoluto de um recurso (arquivo de dados, imagem, tema),
    funcionando tanto em modo de desenvolvimento (local) quanto em modo
    executável congelado (PyInstaller --onefile ou --onedir).

    :param relative_path: O caminho relativo ao diretório raiz do projeto.
                          Ex: "app/ui/themes/black_orange.json"
    :return: O caminho absoluto resolvido como string.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller OneFile: _MEIPASS é a pasta temporária onde os arquivos são extraídos
        base_path = Path(sys._MEIPASS)
    elif getattr(sys, 'frozen', False):
        # PyInstaller OneDir: Os recursos estão relativos ao executável
        # Em OneDir, sys.executable aponta para o binário.
        # Os arquivos de dados geralmente estão na mesma pasta ou em subpastas preservadas.
        base_path = Path(sys.executable).parent
    else:
        # Modo de desenvolvimento: base é a raiz do projeto (CWD)
        base_path = Path(os.getcwd())

    # Converte para Path se for string
    if isinstance(relative_path, str):
        # Remove ./ inicial se existir para evitar confusão
        if relative_path.startswith("./"):
            relative_path = relative_path[2:]
        relative_path = Path(relative_path)

    return str(base_path / relative_path)
