#!/bin/bash

APP_NAME="Profgent"
# Detecta o caminho absoluto atual para garantir que o .desktop funcione mesmo se movido (mas o exec precisa ser fixo ou no PATH)
# Para uma instalação "portable", o .desktop deve apontar para o caminho onde o executável foi gerado.
BASE_DIR="$(pwd)"
EXEC_PATH="$BASE_DIR/dist/onefile/$APP_NAME"
ICON_PATH="$BASE_DIR/app/ui/assets/icon.png"

# Verifica se o ícone existe, senão usa um genérico do sistema
if [ ! -f "$ICON_PATH" ]; then
    ICON_PATH="utilities-terminal" # Ícone genérico de fallback
fi

# Cria arquivo .desktop local
cat > Profgent.desktop <<EOF
[Desktop Entry]
Name=Profgent
Comment=Sistema de Gestão Acadêmica
Exec=$EXEC_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Education;Office;
EOF

chmod +x Profgent.desktop
echo "Atalho criado: Profgent.desktop"
echo "Para instalar no sistema, mova para ~/.local/share/applications/"
