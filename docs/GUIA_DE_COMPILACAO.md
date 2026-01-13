# Guia de Compilação do Profgent

Este guia descreve como gerar os executáveis e instaladores do **Profgent** para Windows, MacOS e Linux.

## Pré-requisitos Gerais

1.  **Python 3.10+** instalado.
2.  Dependências instaladas via Poetry:
    ```bash
    poetry install --with dev
    ```

---

## 1. Gerando o Executável (Todas as Plataformas)

O projeto inclui um script de automação que utiliza o **PyInstaller** para gerar o executável. Este script deve ser executado no sistema operacional alvo (ex: rode no Windows para gerar .exe, no Mac para gerar .app).

1.  Abra o terminal na raiz do projeto.
2.  Execute o script de build:
    ```bash
    poetry run python scripts/build_executable.py
    ```
3.  O script irá gerar duas versões na pasta `dist/`:
    *   `dist/onedir/`: Uma pasta contendo o executável e dependências (Início mais rápido).
    *   `dist/onefile/`: Um arquivo único executável (Mais fácil de compartilhar).

**Nota sobre Ícone:**
Se desejar um ícone personalizado, coloque um arquivo chamado `icon.ico` (Windows) ou `icon.icns` (Mac) na pasta `app/ui/assets/` antes de compilar.

---

## 2. Criando Instaladores

Após gerar o executável (Passo 1), você pode criar um instalador profissional.

### Windows (Inno Setup)

1.  Instale o **Inno Setup** (https://jrsoftware.org/isdl.php).
2.  Navegue até a pasta `scripts/installers/`.
3.  Abra o arquivo `windows_setup.iss` com o Inno Setup Compiler.
4.  Clique em "Compile".
5.  O instalador `Profgent_Setup.exe` será gerado na pasta `dist/installers/`.

### MacOS (DMG)

1.  Certifique-se de ter rodado o passo 1 no MacOS (gerando o `Profgent.app`).
2.  No terminal, dê permissão de execução e rode o script:
    ```bash
    chmod +x scripts/installers/create_dmg.sh
    ./scripts/installers/create_dmg.sh
    ```
3.  O arquivo `.dmg` será gerado em `dist/installers/`.

### Linux

No Linux, a distribuição geralmente é feita via o arquivo executável "OneFile" (AppImage é outra opção, mas o OneFile é suficiente para muitos casos).

Para criar um atalho no menu de aplicativos:
1.  Rode o script `scripts/installers/linux_setup.sh`.
2.  Ele criará um arquivo `.desktop` que pode ser movido para `~/.local/share/applications/`.

---

## Solução de Problemas

*   **Banco de Dados:** O executável criado usará a pasta do usuário (`C:\Users\Nome\.academic_management_app` ou `~/.academic_management_app`) para armazenar o banco de dados e logs. Isso evita problemas de permissão.
*   **Erro "Failed to execute script":** Execute o programa via terminal para ver as mensagens de erro. Verifique se todas as pastas de assets (`app/data`, `app/ui/themes`) foram copiadas corretamente (o script de build faz isso automaticamente).
