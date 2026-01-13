#!/usr/bin/env python3
import PyInstaller.__main__
import sys
import os
from pathlib import Path

# Determina o diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

def build_executable():
    """
    Script de automação para build do Profgent com PyInstaller.
    Gera executáveis para Linux, e configurações para Windows/Mac.
    """
    print(f"Iniciando build no diretório: {BASE_DIR}")

    # 1. Definição de Caminhos e Assets

    # Assets de Dados (BNCC)
    data_path = BASE_DIR / "app" / "data"
    # Assets de UI (Temas)
    themes_path = BASE_DIR / "app" / "ui" / "themes"
    # Assets de Imagens (Se houver)
    assets_path = BASE_DIR / "app" / "ui" / "assets"

    # Verifica se os diretórios existem
    if not data_path.exists():
        print(f"AVISO: Diretório de dados não encontrado: {data_path}")
    if not themes_path.exists():
        print(f"AVISO: Diretório de temas não encontrado: {themes_path}")

    # Define o separador de caminho (Windows usa ';', Unix usa ':')
    sep = ';' if sys.platform.startswith('win') else ':'

    # Lista de arquivos/pastas para incluir (--add-data)
    # Formato: "origem:destino"
    add_data = [
        f"{data_path}/*.json{sep}app/data",
        f"{themes_path}/*.json{sep}app/ui/themes",
    ]

    # Se assets existir, adiciona
    if assets_path.exists():
        add_data.append(f"{assets_path}{sep}app/ui/assets")
        icon_path = assets_path / "icon.ico"
        if not icon_path.exists():
            # Tenta .png ou .icns dependendo do OS, mas .ico é o padrão do PyInstaller para Windows
            icon_path = None
    else:
        icon_path = None

    # 2. Definição de Imports Ocultos (--hidden-import)
    # Bibliotecas que o PyInstaller pode não detectar automaticamente
    hidden_imports = [
        "babel.numbers",
        "sqlalchemy.sql.default_comparator",
        "customtkinter",
        "PIL._tkinter_finder", # Às vezes necessário para CTk
        "app.services.data.student_service", # Garantir inclusão dos submódulos
        "app.services.data.course_service",
        "app.services.data.enrollment_service",
        "app.services.data.grade_service",
        "app.services.data.lesson_service",
        "app.services.data.incident_service",
        "app.services.data.schedule_service",
        "app.services.data.dashboard_service",
        "app.services.data.seating_chart_service",
        "app.core.llm.openai_provider", # Se usado dinamicamente
        "app.core.llm.anthropic_provider",
    ]

    # 3. Argumentos Comuns
    args = [
        str(BASE_DIR / "main.py"), # Script principal
        "--name=Profgent",
        "--noconfirm",
        "--clean",
        "--windowed", # Não abre console (GUI mode)
        # "--debug=all", # Descomente para debug
    ]

    # Adiciona dados
    for data in add_data:
        args.append(f"--add-data={data}")

    # Adiciona imports ocultos
    for hidden in hidden_imports:
        args.append(f"--hidden-import={hidden}")

    # Adiciona ícone se existir
    if icon_path:
        # Nota: No Linux, o ícone da janela é definido no .desktop ou runtime,
        # mas o PyInstaller aceita o argumento.
        args.append(f"--icon={str(icon_path)}")

    # 4. Modo OneDir (Diretório - Mais rápido para iniciar)
    print("\n[Build] Gerando versão OneDir (Pasta)...")
    onedir_args = args.copy()
    onedir_args.append("--onedir")
    # Output em dist/Profgent_Dir
    onedir_args.append("--distpath=dist/onedir")
    PyInstaller.__main__.run(onedir_args)

    # 5. Modo OneFile (Arquivo Único - Melhor distribuição simples)
    print("\n[Build] Gerando versão OneFile (Executável Único)...")
    onefile_args = args.copy()
    onefile_args.append("--onefile")
    onefile_args.append("--distpath=dist/onefile")
    PyInstaller.__main__.run(onefile_args)

    print("\n[Build] Concluído com sucesso!")
    print(f"Arquivos gerados em: {BASE_DIR}/dist/")

if __name__ == "__main__":
    build_executable()
